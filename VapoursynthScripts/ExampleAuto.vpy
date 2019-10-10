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


#Wrapper for super_resolution, which itself is a wrapper for vs_mxnet, which is a interface for mxnet. Checks if the model is an RGB or grayscale one. 
def NeuralNet(clip):
	if (bool(sr_args["is_rgb_model"])):
		clip = mvf.Depth(clip, depth=32)
		clip = muf.super_resolution(clip, **sr_args)
	else:
		Yclip = core.fmtc.bitdepth(core.std.ShufflePlanes(clip, planes=0, colorfamily=vs.GRAY), bits=32)
		Uclip = core.fmtc.bitdepth(core.std.ShufflePlanes(clip, planes=1, colorfamily=vs.GRAY), bits=32)
		Vclip = core.fmtc.bitdepth(core.std.ShufflePlanes(clip, planes=2, colorfamily=vs.GRAY), bits=32)
		Yclip = muf.super_resolution(Yclip, **sr_args)
		Uclip = muf.super_resolution(Uclip, **sr_args)
		Vclip = muf.super_resolution(Vclip, **sr_args)
		clip = core.std.ShufflePlanes(clips=[Yclip, Uclip, Vclip], planes=[0, 0, 0], colorfamily=vs.YUV)
	return clip




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

#Process the image with a pretrained neural network
clip = NeuralNet(clip)

#Interleave the source and processed clip for easy comparison. Comment this out for processing
clip = mvf.Preview(clips=[core.text.Text(clip, "Processed"), core.text.Text(source, "Source")])

#This is a very sharp downscaling filter, when shrinking output is necessary.
#clip = mvf.SSIM_downsample(clip, w = 640, h = 360) 

#Change the bit depth and the video format for final output. You probably want to do this if encoding a video.
#clip = mvf.ToYUV(clip, css="420", depth=10)

#final output
clip.set_output()
