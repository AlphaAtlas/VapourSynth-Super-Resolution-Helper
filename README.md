# vs_mxnet_helper
Some simple scripts that ease the setup and configuration of MXNet image processing in VapourSynth.

Installation Instructions:

This guide will show you how to get a wide range of neural networks upscalers running on videos and images in no time. It’s only been tested on Windows 10 so far, but might work if you have Windows 7. Linux users will have to install the dependencies themself, for now. If you have an AMD or Intel GPU, only a single upscaler is included now, and you can skip basically all of this guide. Make sure to have 7zip or a similar archive manager installed beforehand. 

First, download the latest version of the Vapoursynth FATPACK from here: 

https://forum.doom9.org/showthread.php?t=175529

Uzip it somewhere you have at least 10GB of free space.

Download Nvidia CUDA 9.2 From Here:

https://developer.nvidia.com/cuda-92-download-archive?target_os=Windows&target_arch=x86_64

Do a custom install, and ONLY install everything under the “CUDA” checkbox, so it won’t try to overwrite your current drivers, as seen below:

![Screenshot](CUDA1.jpg)
![Screenshot](CUDA2.jpg)

Next, give Nvidia an email address and download cuDNN for CUDA 9.2 from the link below. Don't get the version for 10.0, or any of the older CUDA versions, only 9.2. I cannot legally redistribute this file, you have to download it yourself: 

https://developer.nvidia.com/rdp/form/cudnn-download-survey

Next, open or unzip the cuDNN archive. Drag the 3 folders in the archive’s “cuda” folder to the “v9.2” folder in your Nvidia CUDA install location. By default, it’s at “%programfiles%\NVIDIA GPU Computing Toolkit\CUDA\v9.2” for me, but it might be in the hidden %programdata% folder instead. 

![Screenshot](cuDNN.png)

Or, alternatively, you can follow Nvidia’s instructions here, which tell you to do the same thing:

https://docs.nvidia.com/deeplearning/sdk/cudnn-install/index.html#installwindows

Now, drag all the files from the “VapourSynth64Portable” folder in the download below (or the releases section of this repo) to the “VapourSynth64Portable” folder you unzipped from the VapourSynth fatpack. 
