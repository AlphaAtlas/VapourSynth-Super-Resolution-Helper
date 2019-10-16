
import subprocess, os, sys, json, shutil, tempfile, tarfile, ctypes
from Alpha_SharedFunctions import get_set_root, check_cuda, check_cudnn, compact, download, get_cuda_ver, create_vsgan_folder
import traceback


CUDAJSON = "https://raw.githubusercontent.com/AlphaAtlas/VapourSynth-Super-Resolution-Helper/master/URLs/CUDA_URL.json"

#TODO: remove modules that aren't needed
cuda_args = ['nvcc', 'cuobjdump', "nvprune", "cupti", "gpu_library_advisor", "memcheck", "nvdisasm", "nvprof", "visual_profiler", "visual_studio_integration"," demo_suite", "documentation", "cublas", "cublas_dev", "cudart", "cufft", "cufft_dev", "curand", "curand_dev", "cusolver", "cusolver_dev", "cusparse", "cusparse_dev", "nvgraph", "npp", "npp_dev", "nvrtc", "nvrtc_dev", "nvml_dev"]

torchgpu101 = ["torch===1.3.0", "torchvision===0.4.1", "-f", r"""https://download.pytorch.org/whl/torch_stable.html"""]

torchgpu92 = ["torch==1.3.0+cu92", "torchvision==0.4.1+cu92", "-f", r"""https://download.pytorch.org/whl/torch_stable.html"""]

#This script needs to relaunch itself with elevated privledges, so it has to be a seperate file.

def install_vsgan_gpu(cver):
    root = get_set_root()
    if cver == "10.1":
        subprocess.run([sys.executable, "-m", "pip", "install"] + torchgpu101 + ["--upgrade"], shell=True, check=True)
        subprocess.run([sys.executable, "-m", "pip", "install" + "vsgan" "--upgrade"], shell=True, check=True)
        print("Installed VSRGAN for CUDA 10.1")
        print (" ")
        create_vsgan_folder()

    elif cver == "9.2":
        subprocess.run([sys.executable, "-m", "pip", "install"] + torchgpu92 + ["vsgan" "--upgrade"], shell=True, check=True)
        subprocess.run([sys.executable, "-m", "pip", "install" + "vsgan" "--upgrade"], shell=True, check=True)
        print("Installed VSRGAN for CUDA 9.2")
        print(" ")
        create_vsgan_folder()
    else:
        print("Unable to install VSGAN, as it requires CUDA 10.1 or CUDA 9.2")
        print("Please rerunn the installer and reinstall CUDA if you want to use VSGAN")
        print(" ")
        input("Press ENTER to continue...")

def install_mxnet_gpu(cver):
    #Installs the appropriate version of mxnet with pip
    root = get_set_root()
    cudastr = cver.replace(".", "")
    mxmodule = "mxnet-cu" + cudastr
    try: 
        subprocess.run([sys.executable, "-m", "pip", "install", mxmodule, "--upgrade"], shell=True, check=True)
    except:
        print("ERROR: mxnet module for CUDA " + cudafull + "is not availible!")
        print("Please install an appropriate version of CUDA and rerun this update script, if you want MXNet processing")
        print("")
        input("Press ENTER to continue...")

#https://stackoverflow.com/questions/130763/request-uac-elevation-from-within-a-python-script
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

#https://gist.github.com/GaryLee/d1cf2089c3a515691919
def run_as_admin(argv=None, debug=False):
    shell32 = ctypes.windll.shell32
    if argv is None and shell32.IsUserAnAdmin():
        return True
        
    if argv is None:
        argv = sys.argv
    if hasattr(sys, '_MEIPASS'):
        # Support pyinstaller wrapped program.
        arguments = map(str, argv[1:])
    else:
        arguments = map(str, argv)
    argument_line = u' '.join(arguments)
    executable = str(sys.executable)
    if debug:
        print('Command line: ', executable, argument_line)
    ret = shell32.ShellExecuteW(None, u"runas", executable, argument_line, None, 1)
    if int(ret) <= 32:
        return False
    return None

def install_cuda(ujson, cudver = "10.1"):
    #Installs the appropriate version of CUDA silently
    #Might overwrite existing installs???
    cuda_strings = ["-s"]
    for s in cuda_args:
        cuda_strings.append("_" + cudver)
    cuurl = None
    if str(sys.getwindowsversion()) == '10':
        cuurl = ujson['CUDAWin10']
    else:
        print("WARNING: Versions of Windows older than Windows 10 aren't tested.")
        print(" ")
        cuurl = ujson['CUDAWin']
    print ("Downloading the online CUDA installer.")
    print(" ")
    cudir = download(cuurl, reuse = True)
    print(r"""The installer should be in %TEMP%/pySmartDL/ if you need it.""") 
    print(" ")
    print("Silently Installing CUDA. This could take awhile...")
    print(" ")
    s = subprocess.run([cudir] + cuda_strings, check=True, shell=True)
    if not check_cuda():
        raise Exception("CUDA installation failed!")
    print("CUDA installation done.")

def install_cudnn(cver, ujson):
    #Installs the appropriate version of cuDNN, using a json for reference
    if (cver in ujson['cudnn']) and check_cuda(): 
        cudnnurl = ujson['cudnn'][cver]
        print ("Downloading cuDNN for " + cver)
        print(" ")
        dnndir = download(cudnnurl, reuse=True)
        print(" ")
        print("The archive should be in %TEMP%/pySmartDL/ if you need it.")
        print(" ")
        print("Extracting cuDNN...")
        #TODO: Shell out to 7zip for faster decompressing.
        tar = tarfile.open(dnndir, "r:bz2")  
        tar.extractall(os.path.normpath(os.getenv("CUDA_PATH")))
        tar.close()
        if not check_cudnn():
            raise Exception("Error installing cuDNN!")

        print('cuDNN installed!')
    else:
        print("No appropriate version of cuDNN found for CUDA " + cver + ".")
        print("MXNet will NOT work without cuDNN, but other GPU filters should work fine.")
        print("Would you like to install the newest version of CUDA?")
        print("This could overwrite your default CUDA installation.")
        choice = input("Yes/No:")
        if choice.lower() == 'yes':
            install_cuda(ujson)
            install_cudnn(cver, ujson)


#Check for, install, and verify CUDA and cuDNN
if __name__ == "__main__":
    try:
        ret = run_as_admin()
        if ret is None:
            #Documentations claims this is getting admin privledges
            print("Getting admin rights...")
        if ret is True:
            #This branch only runs with admin privledges
            root = get_set_root()
            print("Installing CUDA stuff!")
            print("Please note that this Python script needs Admin privledges to access CUDA/cuDNN in Program Files")
            print(" ")
            input("Press ENTER to continue...")
            print(" ")
            print("Fetching cuDNN version table from GitHub")
            urljson = download(CUDAJSON, getjson=True)
            print(' ')
            if check_cuda():
                print("Existing CUDA installation detected!")
                cver = get_cuda_ver()
                if check_cudnn():
                    print("cuDNN files found!")
                else: 
                    install_cudnn(cver, urljson)
                install_mxnet_gpu(cver)
                install_vsgan_gpu(cver)
            else:
                install_cuda(urljson)
                cver = get_cuda_ver()

                install_cudnn(cver, urljson)
                install_mxnet_gpu(cver)
                install_vsgan_gpu(cver)
                print(" ")
            print("Compressing CUDA directory in background...")
            compact(os.path.normpath(os.path.join(os.getenv("programfiles"), "NVIDIA GPU Computing Toolkit")))
        else:
            #But this also seems to be "getting admin privledges?"
            pass
    except Exception as e:
        #SHOW ME WHAT YOU GOT
        print(" ")
        traceback.print_exc()
        input("Press ENTER to continue...")