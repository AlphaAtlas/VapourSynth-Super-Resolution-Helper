import glob
import functools
import os
import shutil
import time
from PIL import Image
from itertools import groupby
from vapoursynth import core
import muvsfunc as muf


def remove_prefix(text, prefix):
	#helper function to remove a prefix from a string
	if text.startswith(prefix):
		return text[len(prefix):]
	return text  # or whatever

def GetClipList(ifolder, iformat, hRes = 0, vRes = 0, balpha = False):
	#Generate a list of image paths inside a folder and its subfolders, filtered by size and format
	#If the resolution is 0 or unspecified, the image size filter will be skipped. 
	rawlist = glob.glob(ifolder + "/**/*." + iformat, recursive=True)
	directorylist = glob.glob(ifolder + "/**/*/", recursive=True)
	filelist=[]
	cliplist = []
	os.makedirs(ifolder + r"/../VapourSynth_Image_Buffer", exist_ok = True)
	os.makedirs(ifolder + r"/../Processed_Images", exist_ok = True)
	for dir in directorylist:
		os.makedirs(ifolder + r"/../Processed_Images/" + remove_prefix(dir, ifolder), exist_ok = True)
	if hRes == 0 and vRes == 0:
		sizelist = [] 					#Size matters
		for imagedir in rawlist:		#Get a list of image sizes
			im = Image.open(imagedir)
			width, height = im.size
			im.close()
			sizelist.append([width,height])
		reslist =  [k for k,v in groupby(sorted(sizelist))]					#remove duplicates
		for res in reslist:				#Turn the image directories into clips grouped by resolution
			tempdirs = []
			n = 0
			for size in sizelist:
				if size == res:
					tempdirs.append(rawlist[n])
				n = n+1
			cliplist.append(GetClip(tempdirs, balpha))
			filelist.append(tempdirs)
		return cliplist, filelist
	else:
		for imagedir in rawlist:
			im = Image.open(imagedir)
			width, height = im.size
			im.close()
			if (width == hRes) and (height == vRes):
				filelist.append(imagedir)
		return [GetClip(filelist, balpha)], filelist



def GetClip(filelist, balpha, mis = False):
	#Returns a VapourSynth clip and alpha clip containing images from filelist
	#Clips need to be spliced together like this to support images with multiple resolutions
	if balpha == True:
		clip, alphaclip =  core.imwri.Read(filelist[0], mismatch=False, alpha=True)
		if len(filelist) > 1:
			filelist = filelist[1:]
			for file in filelist:
				singleclip, singlealphaclip = core.imwri.Read(file, mismatch=False, alpha=True)
				clip = core.std.Splice([clip, singleclip], mismatch = mis)
				alphaclip = core.std.Splice([alphaclip, singlealphaclip], mismatch = mis)
		return clip, alphaclip
	else:
		clip =  core.imwri.Read(filelist[0], mismatch=False, alpha=False)
		if len(filelist) > 1:
			filelist = filelist[1:]
			for file in filelist:
				singleclip = core.imwri.Read(file, mismatch=False, alpha=False)
				clip = core.std.Splice([clip, singleclip], mismatch = mis)
		return clip, core.std.BlankClip(clip, length = clip.num_frames)





#def saver(n, clip, ImageFolder, OutputFormat, filelist, iformat):
	#Moves images from the output folder to a folder with the file structure and names of the original images
	#This action needs to be delayed because the it takes time for the image writer to actually write an image. 
	#As it turns out, the actual image writing lags behind imwri.Write, so this function doesn't work. 
#	if (n >= 10):
#		try: 
#			shutil.move(ImageFolder + r"/../VapourSynth_Image_Buffer/image" + str(n-10) + "." + OutputFormat, ImageFolder + r"/../Processed_Images/" + remove_prefix(filelist[n-10], ImageFolder)[:-len(iformat)] + OutputFormat)
#		except:
#			print(ImageFolder + r"/../VapourSynth_Image_Buffer/image" + str(n-10) + "." + OutputFormat + " failed to copy!")
#	if n == clip.num_frames-1:
#		
#		for x in range (n-9, n+1):
#			if x >= 0:
#				try: 
#					if os.path.isfile(ImageFolder + r"/../VapourSynth_Image_Buffer/image" + str(x) + "." + OutputFormat):
#						shutil.move(ImageFolder + r"/../VapourSynth_Image_Buffer/image" + str(x) + "." + OutputFormat, ImageFolder + r"/../Processed_Images/" + remove_prefix(filelist[x], ImageFolder)[:-len(iformat)] + OutputFormat)
#					else:
#						leftovers.append(ImageFolder + r"/../VapourSynth_Image_Buffer/image" + str(x) + "." + OutputFormat)
#						leftoverdest.append(ImageFolder + r"/../Processed_Images/" + remove_prefix(filelist[x], ImageFolder)[:-len(iformat)] + OutputFormat)
#
#				except FileNotFoundError:
#					os.system('start cmd.exe /k "echo ' + 'error' + '"')
#					print(ImageFolder + r"/../VapourSynth_Image_Buffer/image" + str(x) + "." + OutputFormat + " failed to copy!")
#	return clip

def Writer(clip, iformat, oformat, ifolder, filelist, comp = "DXT5", alpha = False, q = 100, alphaclip = None, ):
	#Writes images to an output folder. Upscales the alpha channel if necessary. 
	if alpha == True:
		while clip.width > alphaclip.width:
			alphaclip = core.nnedi3cl.NNEDI3CL(alphaclip, field = 0, dh = True, dw = True, qual = 2)
		if (clip.width != alphaclip.width) or (clip.height != alphaclip.height):
			alphaclip = muf.SSIM_downsample(alphaclip, clip.width, clip.height)
		clip = core.imwri.Write(clip, imgformat = oformat.upper(), filename = ifolder + r"/../VapourSynth_Image_Buffer/image%d."  + oformat, firstnum = 0, quality = q, overwrite=True, alpha = alphaclip)
	else:
		clip = core.imwri.Write(clip, imgformat = oformat.upper(), filename = ifolder + r"/../VapourSynth_Image_Buffer/image%d."  + oformat, firstnum = 0, quality = q, overwrite=True)
#	clip = core.std.FrameEval(clip, functools.partial(saver, clip=clip, ImageFolder = ifolder, OutputFormat = oformat, filelist = filelist, iformat = iformat))
	return clip




