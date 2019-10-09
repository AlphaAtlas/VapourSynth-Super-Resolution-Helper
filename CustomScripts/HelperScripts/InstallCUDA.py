import importlib, subprocess, os, sys

#This script needs to relaunch itself with elevated privledges, so it has to be a seperate file.

#Check for, install, and verify CUDA and cuDNN
if __name__ == "__main__": 
    CUDA10URL = "https://github.com/AlphaAtlas/VapourSynth-Super-Resolution-Helper/raw/master/URLs/CUDA_Win10_URL"

    CUDA7URL = "http://developer.download.nvidia.com/compute/cuda/10.1/Prod/network_installers/cuda_10.1.243_windows_network.exe"

    
    if importlib.util.find_spec("spam") is None:
        subprocess.call([sys.executable, "-m", "pip", "install", "elevate", "--upgrade"])
    if importlib.util.find_spec("pySmartDL") is None:
        subprocess.call([sys.executable, "-m", "pip", "install", "pySmartDL", "--upgrade"])
    from elevate import elevate
    elevate()
    from pySmartDL import SmartDL
    obj = SmartDL(
