import os, sys
sys.path.append(os.getcwd() + "/HelperScripts")
sys.path.append(os.getcwd() + "/../CustomScripts/HelperScripts")
sys.path.append(os.getcwd() + "/CustomScripts/HelperScripts")
import mvsfunc as mvs
import muvsfunc as muf
#import vapoursynth as vs
from vapoursynth import core
core.std.LoadPlugin(r'MXNet/vs_mxnet.dll', altsearchpath=True)
import ImageHelper as helper
settings = dict()
try: nopreview
except NameError: settings['nopreview'] = False
#Parameters for mxnet processing. Will be set automatically by select_neural_network.bat. 
sr_args = dict(model_filename=r'../NeuralNetworks/ARAN\aran_c0_s0_x2', device_id=0,up_scale=2, is_rgb_model=True, pad=None, crop=None, pre_upscale=False)



#Main options

#(r"""folder path""") Folder to read images out of. Use / or \\ instead of single backslashes, and try not to leave a slash behind the last folder. 
settings['inputfolder'] = r"""C:/Users/Alex/MPRimworld/RimWorld1-0-2282Win64\\Mods\\1127530465\\Textures"""	#This is the path to the directory with images you want to upscale

#('string')Filter mode."filetype" gets all images with the 'inputformat' extension, "similarimage" gets images with the same resolution/format as a specified image
settings['filtermode']= r"similarimage"

#(r"""folder path""") Only images with the same properties as this image will be processed if "similarimage" is set as the filter mode. And remember, \ is bad, mkay? 
settings['inputimagedir'] = r"""C:\\Users\\Alex\\MPRimworld\\RimWorld1-0-2282Win64\\Mods\\1127530465\\Textures\\Rimatomics\\Things\\RimatomicsBuildings\\raddetector.png"""					

#('string') Input image file extension when "filetype" is set as the filter mode, all other file types will be ignored.
settings['inputformat'] = r"png"

#('string') Output image format. Pretty much any image file extension under the sun is supported, see the full list here: https://imagemagick.org/script/formats.php			 
settings['imgformat']= r"jpg"

#settings['nopreview'] = True

#Extra Options

#('string')Algorithm to use for .dds file compression, among other filetypes. 
#None, DXT1, DXT5, and (maybe) DXT3 are valid. See http://www.vapoursynth.com/doc/plugins/imwri.html
#You should probably leave it as "Undefined" for anything other than .dds
settings['compression_type'] = "Undefined"		

#(0-100)Quality to use for JPEG/PNG/MNG/MIFF compression. Should basically always be 100.
settings['quality'] = 100

#(True, False) Setting to True will preview alpha masks in the output (but not write them to disk seperately) 
settings['showalpha'] = False					

#(True, False) Setting this to True will interleave the original images with the processed ones, making them easy to compare
settings['showoriginal'] = False

#(True, False) Setting to True will write processed images to disk
settings['writeimages'] = True

#You can add/modify neural network settings here. 
sr_args['block_w']=64
sr_args['block_h']=64

#Get a dict of categorized images in the 'inputfolder' directory
settings.update(sr_args)
settings['sizeformatdict'] = helper.GetFileDict(**settings)


#This function processes your images
def ImageProcess(clip, sdict):
	clip = core.resize.Spline36(clip, width=clip.width *2, height = clip.height * 2)	
	#clip = core.text.ClipInfo(clip, alignment = 1)
	return clip

#This function processes alpha (transparency) layers, if there are any
def AlphaProcess(alphaclip, sdict):
	return alphaclip

#Run all the things, write the processed images, and set output.
clip = helper.ProcessImages(ImageProcess, AlphaProcess, settings, **settings)
clip.set_output()
#helper.ExitMover(**settings)