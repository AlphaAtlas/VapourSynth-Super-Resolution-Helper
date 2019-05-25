import glob
import functools
import os
import shutil
import time
from PIL import Image
import vapoursynth as vs
import muvsfunc as muf
from vapoursynth import core

def remove_prefix(text, prefix):
	funcname = "remove_prefix"
	if text.startswith(prefix):
		return text[len(prefix):]
	return text  # or whatever

def GetImageList(ifolder, iformat, hRes, vRes):
	funcName = 'GetImageList'
	rawlist = glob.glob(ifolder + "/**/*." + iformat, recursive=True)
	directorylist = glob.glob(ifolder + "/**/*/", recursive=True)
	filelist=[]
	for imagedir in rawlist:
		im = Image.open(imagedir)
		width, height = im.size
		im.close()
		if (width == hRes) and (height == vRes):
			filelist.append(imagedir)
	os.makedirs(ifolder + r"/../Process_Temp", exist_ok = True)
	os.makedirs(ifolder + r"/../Processed", exist_ok = True)
	for dir in directorylist:
		os.makedirs(ifolder + r"/../Processed/" + remove_prefix(dir, ifolder), exist_ok = True)
	return filelist

def saver(n, clip, ImageFolder, OutputFormat, filelist, iformat):
	funcname = "Saver"
	if (n >= 10):
		try: 
			shutil.move(ImageFolder + r"/../Process_Temp/image" + str(n-10) + "." + OutputFormat, ImageFolder + r"/../Processed/" + remove_prefix(filelist[n-10], ImageFolder)[:-len(iformat)] + OutputFormat)
		except:
			print(ImageFolder + r"/../Process_Temp/image" + str(n-10) + "." + OutputFormat + " failed to copy!")
	if n == clip.num_frames-1:
		time.sleep(0.5)
		for x in range (n-9, n+1):
			try: 
				shutil.move(ImageFolder + r"/../Process_Temp/image" + str(x) + "." + OutputFormat, ImageFolder + r"/../Processed/" + remove_prefix(filelist[x], ImageFolder)[:-len(iformat)] + OutputFormat)
			except:
				print(ImageFolder + r"/../Process_Temp/image" + str(x) + "." + OutputFormat + " failed to copy!")
	return clip

def Writer(clip, iformat, oformat, ifolder, filelist, comp = "DXT5", alpha = False, q = 100, alphaclip = None, ):
	funcname = "Writer"
	if alpha == True:
		while clip.width > alphaclip.width:
			alphaclip = core.nnedi3cl.NNEDI3CL(alphaclip, field = 0, dh = True, dw = True, qual = 2)
		if (clip.width != alphaclip.width) or (clip.height != alphaclip.height):
			alphaclip = muf.SSIM_downsample(alphaclip, clip.width, clip.height)
		clip = core.imwri.Write(clip, imgformat = oformat.upper(), filename = ifolder + r"/../Process_Temp/image%d."  + oformat, firstnum = 0, quality = q, overwrite=True, alpha = alphaclip)
	else:
		clip = core.imwri.Write(clip, imgformat = oformat.upper(), filename = ifolder + r"/../Process_Temp/image%d."  + oformat, firstnum = 0, quality = q, overwrite=True)
	clip = core.std.FrameEval(clip, functools.partial(saver, clip=clip, ImageFolder = ifolder, OutputFormat = oformat, filelist = filelist, iformat = iformat))
	return clip