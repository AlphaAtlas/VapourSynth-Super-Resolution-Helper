import sys, os
sys.path.append(os.getcwd() + "/HelperScripts")
sys.path.append(os.getcwd() + "/../CustomScripts/HelperScripts")
sys.path.append(os.getcwd() + "/CustomScripts/HelperScripts")
import mvsfunc as mvs
import muvsfunc as muf
from vapoursynth import core
core.std.LoadPlugin(r'MXNet/vs_mxnet.dll', altsearchpath=True)
import ImageFetcher as move
try: nopreview
except NameError: nopreview = False



#Main options

#DON'T USE SINGLE BACK SLASHES. Use / or \\ instead. 
ImageFolder = r"""S:\NewsImages\Small"""	#This is the path to the directory with images you want to upscale
#SERIOUSLY, TERRIBLE THINGS WILL HAPPEN IF YOU USE SINGLE BACK SLASHES.
ImageFormat = "jpg"			#Input image file extension, all other file types will be ignored. 
OutputFormat = "png"			#Pretty much any image file extension under the sun is supported, see the full list here: https://imagemagick.org/script/formats.php
Horizontal_Resolution = 0	#If Horizonal and Vertical Resoluton are set to anything other than 0
Vertical_Resolution = 0		#The script will only process images with these dimensions


#Extra Options
Compression = "DXT5"		#Algorithm to use for .dds file compression. None, DXT1, DXT5, and (maybe) DXT3 are valid.  
Alpha = False 					#True or False (case sensetive). If True, alphaclip will contain grayscale alpha channels from images. 
Quality = 100					#Quality to use for JPEG/PNG/MNG/MIFF compression. Should always be 100 for JPEG unless you're short on disk space or uploading test images.

sr_args = dict(model_filename=r'../NeuralNetworks/ARAN\aran_c0_s0_x2', device_id=0,up_scale=2, is_rgb_model=True, pad=None, crop=None, pre_upscale=False)

sr_args['block_w']=64
sr_args['block_h']=64


cliplist, filelist = move.GetClipList(ifolder = ImageFolder, iformat =ImageFormat, hRes = Horizontal_Resolution, vRes = Vertical_Resolution)
fullclip = core.std.BlankClip(cliplist[0][0], width = 8, height = 8, length = 1)
fullalpha = core.std.BlankClip(cliplist[0][0], width = 8, height = 8, length = 1)
for doubleclip in cliplist:
	clip = doubleclip[0]
	alphaclip = doubleclip[1]
	#clip = core.std.CropAbs(clip,100,100)
	#clip = mvs.Depth(clip, depth=32, sample = 1)
	clip = muf.super_resolution(clip, **sr_args)
	#clip = core.nnedi3cl.NNEDI3CL(clip, field = 0, dh = True, dw = True, qual = 2)
	#clip = core.text.Text(clip, str(clip.width))
	clip = core.text.ClipInfo(clip, alignment = 1)
	clip = mvs.Depth(clip, depth=8)
	fullclip = core.std.Splice([fullclip, clip], mismatch = True)
	fullalpha = core.std.Splice([fullalpha, alphaclip], mismatch = True)
	
fullclip = core.std.DeleteFrames(fullclip, [0])
fullalpha = core.std.DeleteFrames(fullalpha, [0])
fullclip = move.Writer(fullclip, ImageFormat, OutputFormat, ImageFolder, filelist, Compression, Alpha, Quality, fullalpha)	#Save images with a custom script. 
if nopreview:
	fullclip = core.std.CropAbs(fullclip,8,8)
fullclip.set_output()
