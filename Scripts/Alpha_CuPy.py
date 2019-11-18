from string import Template

import cupy as cp
import vapoursynth as vs
import muvsfunc_numpy as mufnp
from pathlib import Path
import os

core = vs.get_core()

#just copied from https://github.com/WolframRhodium/muvsfunc/blob/master/Collections/examples/Dpid_cupy/dpid_cupy.vpy
def GPU_Downscale(src, width, height, _lambda = 1.0, fast = False):
    # pre-processing
    if src.format.color_family != vs.RGB:
        raise TypeError("'src' must be a RGB clip.")


    if src.format.sample_type == vs.FLOAT:
        dtype = 'float'

    elif src.format.bits_per_sample == 8:
        dtype = 'uchar'

    else:
        dtype = 'ushort'


    # load CUDA kernel
    with open(os.path.join(os.path.dirname(Path(__file__).resolve()),'dpid.cu'), 'r') as f:
        kernel_source_code = f.read()

    kernel_source_code = Template(kernel_source_code)
    kernel_source_code = kernel_source_code.substitute(
        iwidth=src.width, iheight=src.height, owidth=width, oheight=height,
        pwidth=src.width / width, pheight=src.height / height, lamda=_lambda, 
        dtype=dtype)

    if fast:
        kernelGuidance = cp.RawKernel(code=kernel_source_code, name='kernelGuidance', 
            options=('--use_fast_math', ))
        kernelDownsampling = cp.RawKernel(code=kernel_source_code, name='kernelDownsampling', 
            options=('--use_fast_math', ))
    else:
        kernelGuidance = cp.RawKernel(code=kernel_source_code, name='kernelGuidance')
        kernelDownsampling = cp.RawKernel(code=kernel_source_code, name='kernelDownsampling')


    # create NumPy function
    def dpid_core(h_input, width, height, kernelGuidance, kernelDownsampling):
        d_input = cp.asarray(h_input)
        d_output = cp.zeros((height, width, 3), dtype=h_input.dtype)
        d_guidance = cp.zeros((height, width, 3), dtype=h_input.dtype)

        kernelGuidance((width // 4, height, 1), (128, 1, 1), (d_input, d_guidance))
        kernelDownsampling((width // 4, height, 1), (128, 1, 1), (d_input, d_guidance, d_output))

        h_out = cp.asnumpy(d_output)

        return h_out
    return mufnp.numpy_process(
        [core.std.BlankClip(src, width=width, height=height), src], 
        dpid_core, width=width, height=height, 
        kernelGuidance=kernelGuidance, kernelDownsampling=kernelDownsampling, 
        input_per_plane=False, output_per_plane=False, omit_first_clip=True)
    