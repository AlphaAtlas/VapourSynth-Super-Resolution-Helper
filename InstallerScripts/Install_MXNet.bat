@echo off
cd VapourSynth64
echo Installing misc python modules...
python.exe -m pip install pyperclip --upgrade
echo Installing MXNet for CUDA 10.0
python.exe -m pip install mxnet-cu100 --pre --upgrade
timeout /t 3
cls
echo Testing MXnet...
echo If you get any errors, try re-installing CUDA and cuDNN.
python.exe -c "import mxnet as mx; print(mx.__version__); a = mx.nd.ones((2, 3), mx.gpu()); b = a * 2 + 1; print(b.asnumpy())" -m
echo If you got a matrix with 3s, MXNet is working!
timeout /t 10
