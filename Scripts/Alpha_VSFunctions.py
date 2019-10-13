import numpy as np
import cv2
import muvsfunc_numpy as mufnp
import mvsfunc as mvs
import vapoursynth as vs
from vapoursynth import core

#https://github.com/WolframRhodium/muvsfunc/wiki/OpenCV-Python-for-VapourSynth
def OpenCV_Detail(clip, strength=100):
    enhance_core = cv2.detailEnhance # aliasing
    clip = mvs.ToRGB(clip, depth = 8)
    pclip = mufnp.numpy_process(clip, enhance_core, input_per_plane=False, output_per_plane=False)
    return core.std.Merge(clip, pclip, (strength * 0.01))
