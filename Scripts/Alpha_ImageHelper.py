import glob
import time
import threading
import os, shutil
import time
#from timeit import default_timer as timer
from datetime import datetime
from PIL import Image
#from itertools import groupby
import vapoursynth as vs
from vapoursynth import core
#import muvsfunc as muf
import mvsfunc as mvs
from pprint import pprint
import functools


def remove_prefix(text, prefix):
	#helper function to remove a prefix from a string
	if text.startswith(prefix):
		return text[len(prefix):]
	return text  # or whatever

#https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def GetImageClip(sizeformatdict):
	#An imwri.Read wrapper to handle alpha
	#takes a single sizeformatdict created by getfiledict
	if len(sizeformatdict) != 1:
		raise Exception('The input dictionary should not have more than one entry.')
	key, value = sizeformatdict.popitem()
	if key[4]:		#alpha processing boolean
		return core.imwri.Read(value, mismatch=False, alpha=True)
	else:
		return core.imwri.Read(value, mismatch=False, alpha=False)

def ProcessImages(func, alphafunc, settingsdict, sizeformatdict, inputfolder, imgformat, nopreview, writeimages, showoriginal, showalpha, quality, inputformat, **kwargs):
	inputfolder = os.path.normpath(inputfolder)
	movedict = dict()
	i = 0
	#this dict is used by the writer threads
	for value in sizeformatdict.values():
		for addr in value:
			movedict[i] = addr
			i = i + 1

	def WriterThread(n, inputfolder, imgformat):
		#Moves images from vapoursynth's imwri output a mirror of the original path
		buffstr = os.path.normpath(inputfolder + r"/../VapourSynth_Processing/VapourSynth_Image_Buffer/" + str(n) + "." + imgformat)
		movestr = os.path.normpath((inputfolder + r"/../VapourSynth_Processing/Processed_Images/" + remove_prefix(movedict[n], inputfolder))[:-len(inputformat)] + imgformat)
		if os.path.isfile(movestr):
			os.remove(movestr)
		os.makedirs(os.path.dirname(movestr), exist_ok=True)
		time.sleep(0.1)
		z = 0.14
		#keep trying... 
		#might need to be adjusted with *really* slow frames
		while z < 20:
			if os.path.isfile(buffstr):
				shutil.move(buffstr, movestr)
				return 0
			z = z*1.5
			time.sleep(z)
		raise Exception('Frame ' + n + 'not moved!')

	def Writer(n, tclip):
		#This function is called every frame, just after imwri.write
		threading.Thread(target=WriterThread, args=(n, inputfolder, imgformat), daemon=False).start()
		return tclip

	if len(sizeformatdict) == 1:
		#This is the image matching branch
		key, value = sizeformatdict.copy().popitem()
		if key[4]:	#alpha boolean
			clip, alphaclip = GetImageClip(sizeformatdict)
			clip = core.std.AssumeFPS(clip, fpsnum=1)
			alphaclip = core.std.AssumeFPS(alphaclip, fpsnum=1)
			origclip = clip
			origalpha = alphaclip
			clip = func(clip, settingsdict)
			alphaclip = alphafunc(alphaclip, settingsdict)
			#Defaults to resizing the alpha layer to the color plane size. 
			#This should probably be customizable... 
			if (clip.width, clip.height) != (alphaclip.width, alphaclip.height):
				alphaclip = core.resize.Spline36(alphaclip, clip.width, clip.height)
			if writeimages:
				clip = core.imwri.Write(clip, imgformat = imgformat, filename = inputfolder + r"/../VapourSynth_Processing/VapourSynth_Image_Buffer/%d."  + imgformat, firstnum = 0, quality = quality, overwrite=True, alpha = alphaclip)
				clip = core.std.FrameEval(clip, functools.partial(Writer, tclip=clip))
			#I think clips still need to be piped somewhere, even if you don't need any output?
			if nopreview:
				dummyclip = core.std.BlankClip(alphaclip, width = 4, height = 4)
				dummyclip = core.std.BlankClip(clip, width = 4, height = 4)
				return dummyclip
			#Lots of logic is needed just to switch between outputs
			if showoriginal:
				#Scale original clip to final clip size
				origclip = core.resize.Point(origclip, clip.width, clip.height)
				if showalpha: 
					origalpha = core.resize.Point(origalpha, alphaclip.width, alphaclip.height)
					return mvs.Preview([clip, origclip,  alphaclip, origalpha], depth=10)
				else:
					return mvs.Preview([clip, origclip], depth=10)
			else:
				if showalpha:
					return mvs.Preview([clip, alphaclip], depth=10)
				else:
					return clip
		else:	#No alpha branch
			clip = core.std.AssumeFPS(GetImageClip(sizeformatdict), fpsnum=1)
			origclip = clip
			clip = func(clip, settingsdict)
			if writeimages:
				clip = core.imwri.Write(clip, imgformat = imgformat, filename = inputfolder + r"/../VapourSynth_Processing/VapourSynth_Image_Buffer/%d."  + imgformat, firstnum = 0, quality = quality, overwrite=True)
				clip = core.std.FrameEval(clip, functools.partial(Writer, tclip=clip))
			if nopreview:
				return core.std.BlankClip(clip, width=4, height=4)
			if showoriginal:
				origclip = core.resize.Point(origclip, clip.width, clip.height)	
				return mvs.Preview([clip, origclip], depth=10)
			else:
				return clip
	elif len(sizeformatdict) > 1:
		#This is the filetype filter branch
		#Vapoursynth doesn't like inconsistant input formats, so all the clips are padded and converted
		fullclip = core.std.BlankClip(width = 4, height = 4, length = 1, format = vs.RGB30, fpsnum = 1, fpsden = 1)
		for key in sizeformatdict.keys():
			if key[4]:	#alpha branch
				clip, alphaclip = GetImageClip({key: sizeformatdict[key]})
				origclip = clip
				origalpha = alphaclip
				clip = func(clip, settingsdict)
				alphaclip = alphafunc(alphaclip, settingsdict)
				#defaults to resizing alpha to image size. This should probably be customizable... 
				if (clip.width, clip.height) != (alphaclip.width, alphaclip.height):
					alphaclip = core.resize.Spline36(alphaclip, clip.width, clip.height)
				if writeimages:
					clip = core.imwri.Write(clip, imgformat = imgformat, filename = inputfolder + r"/../VapourSynth_Processing/VapourSynth_Image_Buffer/%d."  + imgformat, firstnum = 0, quality = quality, overwrite=True, alpha = alphaclip)
				if nopreview:
					clip = core.std.BlankClip(clip, width = 4, height = 4, format = vs.RGB30)
				else:	
					if showoriginal:
						origclip = core.resize.Point(origclip, clip.width, clip.height)
						if showalpha: 
							origalpha = core.resize.Point(origalpha, alphaclip.width, alphaclip.height)
							clip = mvs.Preview([clip, origclip, alphaclip, origalpha], depth=10)
						else:
							clip = mvs.Preview([clip, origclip], depth=10)
					else:
						if showalpha:
							clip = mvs.Preview([clip, alphaclip], depth=10)
						else:
							clip = mvs.Preview(clip, depth=10)
			else: #no alpha branch
				clip = GetImageClip({key: sizeformatdict[key]})
				origclip = clip
				clip = func(clip, settingsdict)
				if writeimages:
					clip = core.imwri.Write(clip, imgformat = imgformat, filename = inputfolder + r"/../VapourSynth_Processing/VapourSynth_Image_Buffer/%d."  + imgformat, firstnum = 0, quality = quality, overwrite=True)
				if nopreview:
					clip = core.std.BlankClip(clip, width = 4, height = 4, format = vs.RGB30)
				else:	
					if showoriginal:
						origclip = core.resize.Point(origclip, clip.width, clip.height)
						clip = mvs.Preview([clip, origclip], depth=10)
					else:
						clip = mvs.Preview(clip, depth=10)
			if not nopreview: #pad the clip with borders
				if clip.width > fullclip.width:
					fullclip = core.std.AddBorders(fullclip, right = clip.width - fullclip.width)
				if clip.height > fullclip.height:
					fullclip = core.std.AddBorders(fullclip, bottom = clip.height - fullclip.height)
				if clip.width < fullclip.width:
					clip = core.std.AddBorders(clip, right = fullclip.width - clip.width)
				if clip.height < fullclip.height:
					clip = core.std.AddBorders(clip, bottom = fullclip.height - clip.height)
			fullclip = fullclip + core.std.AssumeFPS(clip, fpsnum = 1)
		#Splice everything into a uniform clip for previewing
		fullclip = core.std.DeleteFrames(fullclip, [0])
		fullclip = core.std.FrameEval(fullclip, functools.partial(Writer, tclip=fullclip))
		return fullclip
	else: 
		raise Exception('No input data!')

def GetFileDict(inputfolder, inputformat="PNG", filtermode = "filetype", inputimagedir = None, **kwargs):
	#Generate a dict of image paths inside a folder and its subfolders, filtered by size, and sorted by size/format
	#If the resolution is 0 or unspecified, the image size filter will be skipped. 
	inputfolder = os.path.normpath(inputfolder)
	inputimagedir = os.path.normpath(inputimagedir)
	#raise Exception(glob.glob(os.path.normpath(inputfolder + r"""/../VapourSynth_Processing/VapourSynth_Image_Buffer""") + r"./[0-" + str(1000) + r"]*." + "JPG".lower()))
	if filtermode == "similarimage":
		inputimage = Image.open(inputimagedir)
		inputimage.verify()
		hRes, vRes = inputimage.size
		inputformat = inputimage.format
		imode = inputimage.mode
		inputimage.close()
	elif filtermode != "filetype":
		raise Exception('invalid filter mode')
	
	rawlist = glob.glob(inputfolder + "/**/*." + inputformat, recursive=True)
#	directorylist = glob.glob(inputfolder + "/**/*/", recursive=True)
	
	os.makedirs(inputfolder + r"/../VapourSynth_Processing/VapourSynth_Image_Buffer", exist_ok = True)
#	os.makedirs(inputfolder + r"/../VapourSynth_Processing/Processed_Images", exist_ok = True)
#	for dir in directorylist:
#		os.makedirs(inputfolder + r"/../VapourSynth_Processing/Processed_Images/" + remove_prefix(dir, inputfolder), exist_ok = True)
	sizeformatdict = dict()
	alphamodes = ("RGBA", "LA", "PA", "RGBa", "La")
	#TODO: Thread the Pillow image reader
	#Note: multiprocessing seemingly crashes VSEdit. Maybe I was just doing it wrong...
	for imagedir in rawlist:
		width = 0
		height = 0
		mode = "broken file"
		form = "broken file"	#default to a broken file categorization in case the file is funky
		balpha = False
		try:
			with Image.open(imagedir) as im:
				im.verify()
				width, height = im.size
				form = im.format
				mode = im.mode
				im.close()
				if mode in alphamodes:
					balpha = True
		except Exception:
			pass
		if filtermode == "filetype":
			sizeformatdict.setdefault((width, height, form, mode, balpha), []).append(os.path.normpath(imagedir))
		if filtermode == "similarimage":
			if (width, height, mode) == (hRes, vRes, imode):
				sizeformatdict.setdefault((width, height, form, mode, balpha), []).append(os.path.normpath(imagedir))
		#The key is a size/format tuple, the item is a directory list with image of that size/format """
	time = str(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
	if (0, 0, "broken file", "broken file", False) in sizeformatdict:
		try:
			os.remove(inputfolder + r"/../VapourSynth_Processing/Broken Image List.txt")
		except:
			pass
		broken_file_log = open(inputfolder + r"/../VapourSynth_Processing/Broken Image List.txt" , "a")
		pprint(r"Directories of broken images as of " + time, stream = broken_file_log)
		pprint(sizeformatdict[(0, 0, "broken file", "broken file", False)], stream = broken_file_log)
		broken_file_log.close()
		del sizeformatdict[(0, 0, "broken file", "broken file", False)]
	try:
		os.remove(inputfolder + r"/../VapourSynth_Processing/Image_Formats.txt")
	except:
		pass
	image_format_log = open(inputfolder + r"/../VapourSynth_Processing/Image_Formats.txt" , "a")
	pprint(r"Categorization of images as of " + time, stream=image_format_log)	
	pprint(r"""Format is (width, height, file format, image format, alpha layer) [image paths].""", stream=image_format_log)
	pprint(sizeformatdict, stream=image_format_log)	
	image_format_log.close()
	return sizeformatdict





