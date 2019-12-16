import sys, os, cv2
sys.path.append('/VapourSynthImports')
import vapoursynth as vs
import vsgan as VSGAN
import mvsfunc as mvf
#import muvsfunc as muf
#import fvsfunc as fvf
import havsfunc as haf
import Alpha_CuPy as ape
import muvsfunc_numpy as mufnp
#import BMToolkit as bm
import G41Fun as G41
#import vsutil as util
#import edi_rpow2 as edi
#import kagefunc as kage
#import lostfunc as lost
#import vsTAAmbk as taa
#import xvs as xvs
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

#clip = core.ffms2.Source(r"Path To Your Video/video.mkv")
#clip = core.lsmas.LWLibavSource("/tmp/%d.png")
#clip = core.imwri.Read("testimage.tiff")

#save source for comparison later
source = clip

#Resample an image to 16 bits. Higher bit depth processing usually results in better quality. 
clip = core.std.Resize(clip, format = vs.YUV444P16)

#Temporal denoiser that runs on the GPU. h is the denoising strength, d sets the number of previous/next frames to look at (temporal noise), a is the search radius (spatial noise)
#clip = core.knlm.KNLMeansCL(clip, d=3, a=7, h=1.2)

#Deblocking Functions
#clip = haf.Deblock_QED(clip)
#clip = fvf.AutoDeblock(clip)
#clip = lof.fast_deblock(clip)
	
#MXnet super resolution function. This will resample your clip to 32 bits!
#https://github.com/WolframRhodium/muvsfunc/blob/master/muvsfunc.py#L4329
#clip = muf.super_resolution(clip, **manual_sr_args)

preupscale = clip
#VSRGAN (PyTorch) super resolution. Requires 32-bit RGB input. See https://github.com/imPRAGMA/VSGAN/wiki
#clip = core.resize.Spline36(clip, format = vs.RGBS, matrix_in_s="709")
#vsgan_device = VSGAN.VSGAN()
#vsgan_device.load_model(model=r"""../ESRGANModels/ad_test_tf.pth""", scale=4)
#clip = vsgan_device.run(clip = clip, chunk = False, pad = 16)

#Downscale on the GPU
#clip = ape.GPU_Downscale(clip, width = 3840, height = 2160)

#Convert back down to YUV 444:
clip = core.resize.Spline36(clip, format = vs.YUV444P16, matrix_s = "709")

#Strong temporal denoiser and stabilizer with the LR as a motion reference clip, for stabilizing AI upscalers.
#prefilter = core.resize.Spline36(preupscale, format = clip.format, width = clip.width, height = #clip.height, matrix_s = "709")
#clip = G41.SMDegrain(clip, tr=3, RefineMotion=True, pel = 1, prefilter = prefilter)

#Another CPU denoiser/stabilizer. "very high" is very slow.
#clip = haf.MCTemporalDenoise(clip, settings = "very high", useTTmpSm = True, maxr=4, stabilize = True)

#Stabilized Anti Aliasing, with some GPU acceleration
#clip = taa.TAAmbk(clip, opencl=True, stabilize = 3)

#Example sharpeners that work well on high-res images
#Masks or mvf.limitfilter are good ways to keep artifacts in check
#clip = core.warp.AWarpSharp2(clip)
#clip = G41.NonlinUSM(clip, z=3, sstr=0.28, rad=9, power=1)

#Interleave the source and processed clip for easy comparison in VSEDIT's preview window.
#clip = mvs.Preview(clips=[core.text.Text(clip, "Processed"), core.text.Text(source, "Source")])

#Interpolate to double the source framerate
#super = core.mv.Super(inter)
#backward_vectors = core.mv.Analyse(super, isb = True,  overlap=4, search = 3)
#forward_vectors = core.mv.Analyse(super, isb = False, overlap=4, search = 3)
#inter = core.mv.FlowFPS(inter, super, backward_vectors, forward_vectors, num=0, den=0)

#Change the bit depth and the video format for final output. You probably want to do this if encoding a video.
#clip = mvs.ToYUV(clip, css="420", depth=8, dither_type = "error_diffusion")

#final output
clip.set_output()
