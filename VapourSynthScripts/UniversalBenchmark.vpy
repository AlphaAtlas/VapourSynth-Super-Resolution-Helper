import vapoursynth as vs
import mvsfunc as mvf
core = vs.get_core()

#input clip to benchmark
clip = core.ffms2.Source(r"../CustomScripts/Samples/isssmall.mkv")
clip = core.fmtc.bitdepth(clip, bits=32)
clip2 = core.w2xc.Waifu2x(clip, noise = 1, photo=True)
clip = core.w2xc.Waifu2x(clip, noise = 2, photo=False)
clip = core.std.Interleave([clip, clip2])
clip.set_output()
