import glob
import time
import threading
import os, shutil
from datetime import datetime
from PIL import Image
import vapoursynth as vs
from vapoursynth import core
#import muvsfunc as muf
import mvsfunc as mvs
from pprint import pprint
import functools
from collections import OrderedDict
import concurrent.futures

#mvsfunc.Preview() modified to output YUV instead of RGB
#Needs a colorspace for output.
#Also tries to do point resizing instead of bicubic
#Also can print text from a list after upscaling
#Any "None" objects instead of text in the list will be skipped
#Put in the biggest clip first!
def YUVPreview(clips, matrix_s, writelist = [], matrix=None, full=None, depth=None,\
dither=None, kernel=None, a1=None, a2=None, prefer_props=None, drawtext=True, alignment = 7):
    # Set VS core and function name
	funcName = "YUVPreview"
	if len(writelist) != len(clips):
		writelist = [None] * len(clips)
	if isinstance(clips, list):
		#Remove all Nones from the clip list
		tlist = []
		n = 0
		for c in clips:
			if c == None:
				del writelist[n]
			else:
				n = n + 1
				if not isinstance(c, vs.VideoNode):
					raise TypeError(funcName + ': \"clips\" must be a list of clips!') 
				tlist.append(c)
		clips = tlist
		ref = clips[0]	
	else:
		raise TypeError(funcName + ': \"clips\" must be a list of clips!')
    
    # Get properties of output clip
	if depth is None:
		depth = 10
	elif not isinstance(depth, int):
		raise TypeError(funcName + ': \"depth\" must be an int!')
	if depth >= 32:
		sample = vs.FLOAT
	else:
		sample = vs.INTEGER
	dFormat = core.register_format(vs.YUV, sample, depth, 0, 0).id

	def Conv(clip,txt):
		if (ref.width % clip.width == 0) and (ref.height % clip.height == 0):
			clip = core.resize.Point(clip, ref.width, ref.height, matrix_s = matrix_s, format=dFormat, matrix_in=mvs.GetMatrix(clip, matrix, True, True), range_in=full, dither_type=dither, prefer_props=prefer_props)
		else:
			clip = core.resize.Bicubic(clip, ref.width, ref.height, matrix_s = matrix_s, format=dFormat, matrix_in=mvs.GetMatrix(clip, matrix, True, True), range_in=full, filter_param_a=0, filter_param_b=0.5, dither_type=dither, prefer_props=prefer_props)
		if txt is not None:
			clip = core.text.Text(clip, txt, alignment =  alignment)
		return clip

	for i in range(len(clips)):
		clips[i] = Conv(clips[i], writelist[i])
	clip = core.std.Interleave(clips, extend = False)
	return clip

def remove_prefix(text, prefix):
	#helper function to remove a prefix from a string
	if text.startswith(prefix):
		return text[len(prefix):]
	return text

#https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def ProcessImages(func, alphafunc, previewfunc, inputfolder, inputformat = None, filtermode = "filetype", inputimagedir = None, imgformat = "png", nopreview = False, writeimages = True, quality = 100, scalealpha = True, compression_type = "Undefined", tempdir = None):
	#init sttuff
	if inputimagedir is not None:
		inputimagedir = os.path.normpath(inputimagedir)
	if filtermode == "filetype" and (not isinstance(inputformat, str)):
		raise Exception ("Input format must be specified")
	if filtermode == "similarimage" and os.path.isfile(inputimagedir):
		raise Exception("inputimagedir must be a valid image!")
	inputfolder = os.path.normpath(inputfolder)
	if not os.path.isdir(inputfolder):
		raise Exception("Invalid input folder!")
	if tempdir == None:
		tempdir = os.path.normpath(os.path.join(os.getenv("TEMP"), "VapourSynth_Image_Cache"))
	if filtermode == "similarimage":
		inputimage = Image.open(inputimagedir)
		inputimage.verify()
		hRes, vRes = inputimage.size
		inputformat = inputimage.format
		imode = inputimage.mode
		inputimage.close()
	elif filtermode != "filetype":
		raise Exception('invalid filter mode')

	prootname = r"VapourSynth_Processing"
	pfoldername = os.path.normpath(os.path.join(prootname, r"Processed_Images"))
	pfolder = os.path.normpath(os.path.join(inputfolder, "..", pfoldername))

	def GetFileDict():
		#Generate a dict of image paths inside a folder and its subfolders, filtered by size, and sorted by size/format
		#Also generate empty images in a temporary directory, linked to a mirrored source folder
		udict = dict()
		alphamodes = ("RGBA", "LA", "PA", "RGBa", "La")
		time = str(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
		lock = threading.Lock()
		if os.path.isfile(os.path.join(inputfolder,  "..", pfoldername, "Broken Image List.txt")):
			os.remove(os.path.join(inputfolder,  "..", pfoldername, "Broken Image List.txt"))
		#Check if the target image is valid, and get its parameters
		def imageworker(imdir):
			def logbrokenfile(bfiledir):
				lock.acquire()
				with open(os.path.join(inputfolder , "..", prootname, "Broken Image List.txt") , "a+") as broken_file_log:
					#print(r"Directories of broken images as of " + time + "\n", file = broken_file_log)
					print("Broken file: " + bfiledir + "\n", file = broken_file_log)
				lock.release()

			width = 0
			height = 0
			mode = "broken file"
			form = "broken file"	#default to a broken file categorization in case the file is funky
			balpha = False
			try:
				with Image.open(imdir) as im:
					im.verify()
					width, height = im.size
					form = im.format
					mode = im.mode
				if mode in alphamodes:
					balpha = True
				if width == 0 or height == 0:
					logbrokenfile(imdir)
					return 0
				#The key is a size/format tuple, the item is a directory list with image of that size/format
				#A lock theoretically shouldn't be needed with Python's GIL, but you never know...
				if filtermode == "filetype":
					lock.acquire()
					udict.setdefault((width, height, form, mode, balpha), []).append(os.path.normpath(imdir))
					lock.release()
				if filtermode == "similarimage":
					if (width, height, mode) == (hRes, vRes, imode):
						lock.acquire()
						udict.setdefault((width, height, form, mode, balpha), []).append(os.path.normpath(imdir))
						lock.release()
			except Exception:
				logbrokenfile(imdir)

		def initnclean():
			if os.path.isdir(tempdir):
				shutil.rmtree(tempdir)
			if os.path.isdir(pfolder):
				shutil.rmtree(pfolder)
			os.makedirs(tempdir, exist_ok = False)
			os.makedirs(pfolder, exist_ok = False)

		#Multi threaded (but not multicore) executor for globbing and categorizing images
		#True multiprocessing just seems to crash VSEdit.
		with concurrent.futures.ThreadPoolExecutor() as executor:
			executor.submit(initnclean)
			for imagedir in glob.iglob(inputfolder + "/**/*." + inputformat, recursive=True):
				executor.submit(imageworker, imagedir)
			executor.shutdown(wait=True)
		if (0, 0, "broken file", "broken file", False) in udict:
			raise Exception("Found broken files in the image dict. This should never happen!")
		sorteddict = OrderedDict(sorted(udict.items()))

		def linkworker(source, n): 
			#Link a temp image directory with a mirrored version of the source
			#This make IMWRI less angry than moving after writing, linking before writing, calling it once for each image
			pdest = pfolder + remove_prefix(source, inputfolder)[:-len(inputformat)] + imgformat
			cachefile = os.path.join(tempdir, str(n) + "." + imgformat)
			os.makedirs(os.path.dirname(pdest), exist_ok=True)
			#with open(pdest, "x") as x:
			#	pass
			with open(cachefile, "x") as x:
				pass
			os.link(cachefile, pdest)
		
		def dictwriter():
			#Write a text file with all the image categorizations
			dictdir = os.path.normpath(os.path.join(inputfolder, "..", prootname, "Image_Formats.txt"))
			if os.path.isfile(dictdir):
				os.remove(dictdir)
			with open(dictdir, "a+") as image_format_log:
				print(r"Categorization of images as of " + time + "\n", file=image_format_log)	
				print(r"""Format is (width, height, file format, image format, alpha layer) [image paths].""" + "\n", file=image_format_log)
				pprint(sorteddict, stream=image_format_log)

		with concurrent.futures.ThreadPoolExecutor() as executor:
			executor.submit(dictwriter)
			i =  0
			for key in sorteddict.keys():
				for d in sorteddict[key]:
					executor.submit(linkworker, d, i)
					i = i + 1
		return sorteddict

	def Processor(key, sizeformatdict, start):
		#Writes the images, and does all the processing from the .vpy script
		#This function expects clips to have a constant format/size!
		clip = None
		alphaclip = None
		if key[4]:
			clip, alphaclip = core.imwri.Read(sizeformatdict[key], mismatch=False, alpha=True)
		else:
			clip = core.imwri.Read(sizeformatdict[key], mismatch=False, alpha=False)
		clip = core.std.AssumeFPS(clip, fpsnum=1)
		original = clip
		clip = func(clip)
		if key[4]:
			alphaclip = core.std.AssumeFPS(alphaclip, fpsnum=1)
			origalpha = alphaclip
			alphaclip = alphafunc(alphaclip)
			#Defaults to resizing the alpha layer to the color clip size. 
			#Technically optional, but I'm not sure IMWRI supports a format where the alpha is smaller than the image.  
			if ((clip.width, clip.height) != (alphaclip.width, alphaclip.height)) and scalealpha:
				alphaclip = core.resize.Spline36(alphaclip, clip.width, clip.height)
		if writeimages:
			if key[4]:
				clip = core.imwri.Write(clip, imgformat = imgformat, filename = os.path.join(tempdir, r"%d." + imgformat ), firstnum = start, quality = quality, overwrite=True, compression_type = compression_type, alpha = alphaclip)
			else:
				clip = core.imwri.Write(clip, imgformat = imgformat, filename = os.path.join(tempdir, r"%d." + imgformat ), firstnum = start, quality = quality, overwrite=True, compression_type = compression_type)
		#Don't bother converting if previewing is disabled
		if nopreview:
			return clip
		if not key[4]:
			alphaclip = None
			origalpha = None
		return previewfunc(clip, alphaclip, original, origalpha)

	sizeformatdict = GetFileDict()
	if len(sizeformatdict) == 1:
		#This is the image matching branch
		#It's also the filetype branch when there's only one format/size of file
		tkey, tvalue = sizeformatdict.copy().popitem()
		return Processor(tkey, sizeformatdict, start = 0)
		
	if len(sizeformatdict) > 1:
		#This is the filetype filter branch, when there's more than one size/format of image
		#Vapoursynth doesn't like inconsistant input formats, so all the image categories are run through a for loop
		#Then they're padded to the same size (with black borders), and spliced into one clip.
		start = 0
		fullclip = core.std.BlankClip(width = 4, height = 4, length = 1)
		for tkey in sizeformatdict.keys():
			clip = Processor(tkey, sizeformatdict, start)
			start = start + clip.num_frames
			if not nopreview: #pad the clip with borders
				if fullclip.format != clip.format:
					fullclip = core.std.BlankClip(clip, length = 1)
				if clip.width > fullclip.width:
					fullclip = core.std.AddBorders(fullclip, right = clip.width - fullclip.width)
				if clip.height > fullclip.height:
					fullclip = core.std.AddBorders(fullclip, bottom = clip.height - fullclip.height)
				if clip.width < fullclip.width:
					clip = core.std.AddBorders(clip, right = fullclip.width - clip.width)
				if clip.height < fullclip.height:
					clip = core.std.AddBorders(clip, bottom = fullclip.height - clip.height)
				#Splice everything into a uniform clip for previewing
				fullclip = fullclip + core.std.AssumeFPS(clip, fpsnum = 1)
			else:
				fullclip = core.std.Splice([fullclip, clip], mismatch = 1)
		fullclip = core.std.DeleteFrames(fullclip, [0])
		return fullclip
	else: 
		raise Exception('No input data!')






