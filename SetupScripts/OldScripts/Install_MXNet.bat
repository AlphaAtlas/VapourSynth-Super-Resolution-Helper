@echo off
cd VapourSynth64
echo Installing misc python modules...
python.exe -m pip install pyperclip Pillow ffmpeg-python --upgrade
:CUDACheck
for %%x in (nvcc.exe) do if not [%%~$PATH:x]==[] goto :CUDA
echo No existing CUDA install detected!
goto :NoCUDA

:CUDA
echo Installing MXNet for CUDA 10.1
python.exe -m pip install mxnet-cu101mkl --pre --upgrade
echo Testing mxnet...
echo If you get any errors, try re-installing CUDA and cuDNN.
python.exe -c "import mxnet as mx; print(mx.__version__); a = mx.nd.ones((2, 3), mx.gpu()); b = a * 2 + 1; print(b.asnumpy())" -m
goto :End

:NoCUDA
echo Installing CPU only MXNET
python.exe -m pip install mxnet --pre --upgrade
python.exe -c "import mxnet as mx; print(mx.__version__); a = mx.nd.ones((2, 3), mx.cpu()); b = a * 2 + 1; print(b.asnumpy())" -m
goto :End

:End
echo If you got a matrix with 3s, MXNet is working!
timeout /t 15
