import vapoursynth as vs
core = vs.get_core()
core.std.LoadPlugin(r'MXNet/vs_mxnet.dll', altsearchpath=True)
import mvsfunc as mvf
import muvsfunc as muf

#Argument for the Neural Network. run "_Select_Neural_Network_.bat" to change this automatically!
sr_args = dict(model_filename=r'../NeuralNetworks/MSRN\MSRN_2x', device_id=0,up_scale=2, is_rgb_model=True, pad=None, crop=None, pre_upscale=False)


#Wrapper for the super_resolution, which itself is a wrapper for MXNet. Checks if the model is an RGB or grayscale one.
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

#Set max cache size, in MB. If you have lots of RAM to spare, remove the "#" in front of the line below and change the value.
#core.max_cache_size = 9000

clip = core.ffms2.Source(r"../CustomScripts/Samples/isssmall.mkv")
clip = NeuralNet(clip)
clip.set_output()
