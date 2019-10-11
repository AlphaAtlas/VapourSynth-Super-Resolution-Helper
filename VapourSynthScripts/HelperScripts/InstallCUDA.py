import importlib, subprocess, os, sys, urllib.request, json, shutil, tempfile, tarfile

from .SetupScripts import get_set_root, check_existing_download, download

CUDAJSON = "https://github.com/AlphaAtlas/VapourSynth-Super-Resolution-Helper/raw/master/URLs/CUDA_URL"

cuda_args = ['nvcc', 'cuobjdump', "nvprune", "cupti", "gpu_library_advisor", "memcheck", "nvdisasm", "nvprof", "visual_profiler", "visual_studio_integration"," demo_suite", "documentation", "cublas", "cublas_dev", "cudart", "cufft", "cufft_dev", "curand", "curand_dev", "cusolver", "cusolver_dev", "cusparse", "cusparse_dev", "nvgraph", "npp", "npp_dev", "nvrtc", "nvrtc_dev", "nvml_dev"]

#This script needs to relaunch itself with elevated privledges, so it has to be a seperate file.


def check_cuda():
    return (shutil.which("nvcc.exe") is not None) and (os.getenv("CUDA_PATH") is not None)

def install_cuda(ujson, cudver = "10.1"):
    #todo: remove modules that aren't needed
    cuda_string = "-s "
    for s in cuda_args:
        cuda_string = cuda_string + "_" + cudver + " "
    cuurl = None
    if sys.getwindowsversion() == 10:
        cuurl = ujson['CUDAWin10']
    else:
        print("WARNING: Versions of Windows older than Windows 10 aren't tested.")
        cuurl = ujson['CUDAWin']
    print ("Downloading the online CUDA installer")
    print("It should be in %TEMP%/pySmartDL/ if you need it")    
    cuobj = download(cuurl)
    s = subprocess.run([cuobj.get_dest(), cuda_string], check=True, shell=True)
    if not check_cuda():
        raise Exception("CUDA installation failed!")

def check_cudnn():
    return os.path.isfile(os.path.join(os.environ("CUDA_PATH"), "Library/bin/cudnn64_7.dll"))

def install_cudnn(cver, ujson):
    if (cver in ujson['cudnn']) and check_cuda():
        cudnnurl = ujson['cudnn'][cver]
        print ("Downloading cuDNN for " + cver)
        print("The archive should be in %TEMP%/pySmartDL/ if you need it")
        dnnobj = download(cudnnurl)
        tar = tarfile.open(dnnobj.get_dest(), "r:bz2")  
        tar.extractall(os.path.normpath(os.environ("CUDA_PATH")))
        tar.close()
        if not check_cudnn():
            raise Exception("Error installing cuDNN!")
        print('cuDNN installed!')
    else:
        print("No appropriate version of cuDNN found for CUDA " + cver)
        print("MXNet will NOT work without cuDNN, but other filters should work fine")
        print("Would you like to install the newest version of CUDA?")
        print("This could overwrite your default CUDA installation.")
        choice = input("Yes/No:")
        if choice.lower() == 'yes':
            install_cuda(ujson)
            install_cudnn(cver, ujson)
        


#Check for, install, and verify CUDA and cuDNN
if __name__ == "__main__": 
    root = get_set_root()
    if importlib.util.find_spec("spam") is None:
        subprocess.call([sys.executable, "-m", "pip", "install", "elevate", "--upgrade"])
    if importlib.util.find_spec("pySmartDL") is None:
        subprocess.call([sys.executable, "-m", "pip", "install", "pySmartDL", "--upgrade"])
    from elevate import elevate
    elevate()
    from pySmartDL import SmartDL
    urljson = json.loads(urllib.request.urlopen(CUDAJSON).read().decode())
    if check_cuda():
        print("Existing CUDA installation detected!")
        CUDAVersion = str(os.path.basename(os.environ("CUDA_PATH")))[1:]
        if CUDAVersion is None:
            raise Exception("Error getting CUDA version")
        if check_cudnn():
            print("cuDNN files found!")
        else: 
            install_cudnn(CUDAVersion, urljson)
    else:
        install_cuda()
        install_cudnn()
        print("Compressing CUDA directory in background...")
    subprocess.Popen(r"""compact /c /s:"%programfiles%/NVIDIA GPU Computing Toolkit" /i /q""")
