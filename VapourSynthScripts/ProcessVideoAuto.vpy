#Import stuff here. Comment out what you don't need. 
import mxnet as mx
import mvsfunc as mvs
import muvsfunc as muf
import Alpha_VSFunctions as avsfunc
import fvsfunc as fvf
import havsfunc as haf
import lostfunc as lof
import vsgan as VSGAN
import vapoursynth as vs
from vapoursynth import core

#Comment this out if mxnet isn't working
core.std.LoadPlugin(r'MXNet/vs_mxnet.dll', altsearchpath=True)

#Set max cache size, in MB. If you have RAM to spare, remove the "#" in front of the line below and change the value.
#core.max_cache_size = 6000

#Argument for the neural network. $un "_Select_Neural_Network_.bat" to change this automatically!
sr_args = dict(model_filename=r'../NeuralNetworks/MSRN\MSRN_2x', device_id=0,up_scale=2, is_rgb_model=True, pad=None, crop=None, pre_upscale=False)

#change super resolution arguments here!
manual_sr_args = sr_args
manual_sr_args['block_w']=64
manual_sr_args['block_h']=64


#Change the path to the video you're working with!
#clip = core.ffms2.Source(r"""Path To Your Video/video.mkv""")

#Alternative source filter, good if ffms2 gives you video corruption
#clip = core.lsmas.LWLibavSource(r"""Path To Your Video/video.mkv""")

#This reads an image instead of a video. See http://www.vapoursynth.com/doc/plugins/imwri.html
clip = core.imwri.Read(r"""Samples/texture.dds""")

#save source for comparison later
source = clip

#Resample an image to 16 bits. Higher bit depth processing usually results in better quality. 
#Note that some models aren't RGB models, and each plane might need to be upscaled individually. 
clip = mvs.Depth(clip, depth=16)

#Temporal denoiser that runs on the GPU. Unlike NN denoisers, it can look at multiple frames for noise. 
#h is the denoising strength, d sets the number of previous/next frames to look at (temporal noise), a is the search radius (spatial noise)
#core.knlm.KNLMeansCL(clip, d=2, a=3, h=1.2)

#Various Deblocking Functions
#clip = haf.Deblock_QED(clip)
#clip = fvf.AutoDeblock(clip)
#clip = lof.fast_deblock(clip)

#Double the size of a clip
#clip = core.resize.Spline36(clip, width=clip.width *2, height = clip.height * 2)

#Interesting OpenCV detail enhancement function
#clip = avsfunc.OpenCV_Detail(clip, strength = 50)
	
#MXnet super resolution function. This will resample your clip to 32 bits!
#https://github.com/WolframRhodium/muvsfunc/blob/master/muvsfunc.py#L4329
#clip = muf.super_resolution(clip, **manual_sr_args)

#VSRGAN (PyTorch) super resolution. It'll resample your clip to 8 bit RGB!
#https://gitlab.com/imPRAGMA/VSGAN/wikis/Usage
#clip = VSGAN.Start(clip=clip, model=r"""../ESRGANModels/ad_test_tf.pth""", scale=4, old_arch=False)

#Interleave the source and processed clip for easy comparison.
clip = mvs.Preview(clips=[core.text.Text(clip, "Processed"), core.text.Text(source, "Source")])

#This is a very sharp downscaling filter, when shrinking output is necessary.
#clip = mvs.SSIM_downsample(clip, w = 640, h = 360) 

#Change the bit depth and the video format for final output. You probably want to do this if encoding a video.
#clip = mvs.ToYUV(clip, css="420", depth=10)

#final output
clip.set_output()
