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

#Ripped from https://github.com/WolframRhodium/muvsfunc/blob/master/Collections/examples/BilateralGPU_cupy/bilateral_gpu_cupy.vpy
def GPU_Bilateral(src, sigmaS = 3.0, sigmaR = 0.02, sigma = 0):
    half_kernel_size = round(sigmaS * 2)
    blksize = (32, 8)
    fast = False
    snn = int(sigma > 0) # whether to use SNN sampling strategy

    if src.format.id != vs.GRAYS:
        raise vs.Error("Bilateral: Only 32-bit float grayscale is supported!")

    w, h = src.width, src.height

    # source code of CUDA kernel
    with open(os.path.join(os.path.dirname(Path(__file__).resolve()),'bilateral.cu'), 'r') as f:
        kernel_source_code = f.read()

    kernel_source_code = Template(kernel_source_code)
    kernel_source_code = kernel_source_code.substitute(
        width=w, height=h, sigma_s=-0.5/(sigmaS**2), sigma_r=-0.5/(sigmaR**2), 
        sigma=sigma, snn=snn, half_kernel_size=half_kernel_size)


    if fast:
        kernel = cp.RawKernel(kernel_source_code, 'bilateral', 
            options=('--use_fast_math', ))
    else:
        kernel = cp.RawKernel(kernel_source_code, 'bilateral')

    # create NumPy function
    def bilateral_core(h_img, kernel):
        # h_img must be a 2-D image

        d_img = cp.asarray(h_img)
        d_out = cp.empty_like(d_img)

        kernel(((w + blksize[0] - 1)//blksize[0], (h + blksize[1] - 1)//blksize[1]), blksize, (d_img, d_out))

        h_out = cp.asnumpy(d_out)

        return h_out

    # process
    return mufnp.numpy_process(src, bilateral_core, kernel=kernel)