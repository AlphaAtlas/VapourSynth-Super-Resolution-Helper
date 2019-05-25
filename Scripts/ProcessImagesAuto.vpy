import sys, os
sys.path.append(os.getcwd() + "/HelperScripts")
sys.path.append(os.getcwd() + "/../CustomScripts/HelperScripts")
sys.path.append(os.getcwd() + "/CustomScripts/HelperScripts")
import functools
import mvsfunc as mvs
import vapoursynth as vs
import ImageMover as move



#Main options

#DON'T USE SINGLE BACK SLASHES. Use / or \\ instead. 
ImageFolder = "D:/Scratch/KOTOR2"	#This is the path to the directory with images you want to upscale
#SERIOUSLY, TERRIBLE THINGS WILL HAPPEN IF YOU USE SINGLE BACK SLASHES.
ImageFormat = "tga"		#Input image file extension
OutputFormat = "jpeg"	#Output image file extension
Horizontal_Resolution = 256			
Vertical_Resolution = 256

#Extra Options
Compression = "DXT5"		#Algorithm to use for .dds file compression. None, DXT1, DXT5, and (maybe) DXT3 are valid.  
Alpha = True 					#True or False. If True, Vapoursynth will attempt to process image alpha channels. 
Quality = 100					#Quality to use for JPEG/PNG/MNG/MIFF compression. Should always be 100 for JPEG unless you're short on disk space or uploading test images, otherwise 90+ is good, 75+ is OK. 


filelist = move.GetImageList(ifolder = ImageFolder, iformat = ImageFormat, hRes = Horizontal_Resolution, vRes = Vertical_Resolution)

from vapoursynth import core

if Alpha == True:
	clip, alphaclip = core.imwri.Read(filelist, mismatch=False, alpha=True)
else:
	clip = core.imwri.Read(filelist, mismatch=False, alpha=False)
	alphaclip = core.std.BlankClip()
#clip = core.imwri.Read(filename=filelist, mismatch=False, alpha=False)
clip = core.nnedi3cl.NNEDI3CL(clip, field = 0, dh = True, dw = True, qual = 2)
clip = move.Writer(clip, ImageFormat, OutputFormat, ImageFolder, filelist, Compression, Alpha, Quality, alphaclip)	#Save images with a custom script. 

clip.set_output()
