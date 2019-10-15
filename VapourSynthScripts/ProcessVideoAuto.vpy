import vapoursynth as vs
core = vs.get_core()
core.std.LoadPlugin(r'MXNet/vs_mxnet.dll', altsearchpath=True)
import mvsfunc as mvf
import muvsfunc as muf
import havsfunc as hav

#Set max cache size, in MB. If you have RAM to spare, remove the "#" in front of the line below and change the value.
#core.max_cache_size = 6000

#Argument for the neural network. run "_Select_Neural_Network_.bat" to change this automatically!
sr_args = dict(model_filename=r'../NeuralNetworks/MSRN\MSRN_2x', device_id=0,up_scale=2, is_rgb_model=True, pad=None, crop=None, pre_upscale=False)

#change super resolution arguments here!
manual_sr_args = sr_args
manual_sr_args['block_w']=64
manual_sr_args['block_h']=64


#Change the path to the video you're working with!
#clip = core.ffms2.Source(r"../CustomScripts/Samples/isssmall.mkv")

#Alternative source filter, good if ffms2 gives you video corruption
#clip = core.lsmas.LWLibavSource(r"../CustomScripts/Samples/isssmall.mkv")

#This reads an image instead of a video. See http://www.vapoursynth.com/doc/plugins/imwri.html
clip = core.imwri.Read(r"../CustomScripts/Samples/texture.dds")

#save source for comparison later
source = clip


#Temporal denoiser that runs on the GPU. Unlike NN denoisers, it can look at multiple frames for noise. 
#h is the denoising strength, d sets the number of previous/next frames to look at (temporal noise), a is the search radius (spatial noise)
#core.knlm.KNLMeansCL(clip = core.fmtc.bitdepth(clip, bits=16), d=2, a=2, h=0.8)

#Double the size of a clip
#clip = core.resize.Spline36(clip, width=clip.width *2, height = clip.height * 2)
	
#Resample an image to 32 bits. This is the bit depth muf.super_resoltuon needs
#Note that some models aren't RGB models, and each plane might need to be upscaled individually. 
clip = mvs.Depth(clip, depth=32)
	
#Neural network super resolution function	
clip = muf.super_resolution(clip, **manual_sr_args)	
	
#Interesting OpenCV detail enhancement function
clip = avsfunc.OpenCV_Detail(clip, strength = 50)

#Interleave the source and processed clip for easy comparison. Comment this out for processing
clip = mvf.Preview(clips=[core.text.Text(clip, "Processed"), core.text.Text(source, "Source")])

#This is a very sharp downscaling filter, when shrinking output is necessary.
#clip = mvf.SSIM_downsample(clip, w = 640, h = 360) 

#Change the bit depth and the video format for final output. You probably want to do this if encoding a video.
#clip = mvf.ToYUV(clip, css="420", depth=10)

#final output
clip.set_output()
