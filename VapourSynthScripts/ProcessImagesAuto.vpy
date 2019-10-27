#Command line switch for vspipe
try: nopreview
except NameError: nopreview = False

#Import stuff here. Comment out what you don't need.
import mxnet as mx
import mvsfunc as mvs
import muvsfunc as muf
import muvsfunc_numpy as mufnp
import Alpha_ImageHelper as helper
import Alpha_VSFunctions as avsfunc
import vsgan as VSGAN
import vapoursynth as vs
from vapoursynth import core

#------------
#Main options
#------------

#(r"""folder path""") Folder to read images out of. Use / or \\ instead of single backslashes, and try not to leave a slash behind the last folder. 
inputfolder = r"Samples"	#This is the path to the directory with images you want to upscale

#('string')Filter mode."filetype" gets all images with the 'inputformat' extension, "similarimage" gets images with the same resolution/format as a specified image
filtermode = r"filetype"

#(r"""folder path""") Only images with the same properties as this image will be processed if "similarimage" is set as the filter mode. And remember, \ is bad, mkay? 
inputimagedir = r"Samples/mop.png"					

#('string') Input image file extension when "filetype" is set as the filter mode, all other file types will be ignored.
inputformat = r"png"

#('string') Output image format. Pretty much any image file extension under the sun is supported, see the full list here: https://imagemagick.org/script/formats.php	
imgformat= "jpg"

#Setting to "True" will completely disable most preview processing 
#Otherwise, you should leave this commented out with a #, as it's a command line parameter for batch files. 
#nopreview = False

#-------------
#Extra Options
#-------------

#('string')Algorithm to use for .dds file compression, among other filetypes. 
#None, DXT1, DXT5, and (maybe) DXT3 are valid. See http://www.vapoursynth.com/doc/plugins/imwri.html
#You should probably leave it as "Undefined" for anything other than .dds
compression_type = "Undefined"		

#(0-100)Quality to use for JPEG/PNG/MNG/MIFF compression. Should basically always be 100.
quality = 100

#(True, False) Setting to True will write processed images to disk
writeimages = True

#Manually max cache size, in MB. If you have RAM to spare, remove the "#" in front of the line below and change the value.
#core.max_cache_size = 6000

#Parameters for mxnet processing. Will be set automatically by select_neural_network.bat. 
sr_args = dict(model_filename=r'../NeuralNetworks/IDN\IDN_2x', device_id=0,up_scale=2, is_rgb_model=False, pad=(1, 1, 1, 1), crop=(1, 2, 1, 2), pre_upscale=False, upscale_uv=False, merge_source=True, resample_kernel='Catmull-Rom')
#You can add/modify neural network settings here. 
manual_sr_args = sr_args
manual_sr_args['block_w']=64
manual_sr_args['block_h']=64

#---------------------

#Get a dict of categorized images in the 'inputfolder' directory
settings.update(manual_sr_args)

#This function processes your images. Some example functions are commented out:
def ImageProcess(clip):
	#Keep everything in this function tabbed!
	#Resampling to a higher bit depth first generally gives you better quality
	#clip = mvs.Depth(clip, bits = 16)

	#Denoise on the GPU. Works with AMD/Intel/Nvidia, h represents strength, a is kind of quality. 
	#core.knlm.KNLMeansCL(clip, d=0, a=3, h=1.0)
	
	#Interesting OpenCV detail enhancement function
	#clip = avsfunc.OpenCV_Detail(clip, strength = 50)

	#Double the size of an image with regular spline scaling
	#clip = core.resize.Spline36(clip, width=clip.width *2, height = clip.height * 2)
	
	#MXnet super resolution function. This will resample your clip to 32 bits!
	#https://github.com/WolframRhodium/muvsfunc/blob/master/muvsfunc.py#L4329
	#clip = muf.super_resolution(clip, **manual_sr_args)	
	
	#Super resolution using numpy. Untested!
	#clip = mufnp.super_resolution(clip, **manual_sr_args)

	#VSRGAN (PyTorch) super resolution. It'll resample your clip to 8 bit RGB!
	#vsgan_device = VSGAN.VSGAN()
	#vsgan_device.load_model(model=r"""../ESRGANModels/ad_test_tf.pth""", scale=4)
	#ad = vsgan_device.run(clip=clip, chunk = False)
	#vsgan_device.load_model(model=r"""../ESRGANModels/4x_SpongeBob_235000_G.pth""", scale=4)
	
	
	
	#Convert back to RGB, for image writing
	#clip = mvs.ToRGB(clip, bits = 16)
	
	return clip

#This function processes alpha (transparency) layers, if there are any
def AlphaProcess(alphaclip):
	return alphaclip

def Preview(clip, alphaclip, original, origalpha):
	#Script the preview window here
	#Sometimes alphaclip will be "None", so it needs a check if you do anything to it:
	if alphaclip is not None:
		pass	
	#YUVPreview will write the text you feed it inside a string
	#"Processed, Original, Alpha, Original Alpha"
	writelist = ["P", "O", "A", "OA"]
	cliplist = [clip]
	preview = helper.YUVPreview(cliplist, matrix_s = "709")
	return preview

#Run all the finctions, write the processed images if necessary, and set output.
clip = helper.ProcessImages(ImageProcess, AlphaProcess, Preview, inputfolder = inputfolder, filtermode = filtermode, inputimagedir = inputimagedir, inputformat = inputformat, imgformat = imgformat, compression_type = compression_type, quality = quality, writeimages = writeimages)
clip.set_output() 
