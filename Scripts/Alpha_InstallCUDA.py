
import subprocess, os, sys, json, shutil, tempfile, tarfile, ctypes
from Alpha_SharedFunctions import get_set_root, check_cuda, check_cudnn, compact, download
import traceback


CUDAJSON = "https://raw.githubusercontent.com/AlphaAtlas/VapourSynth-Super-Resolution-Helper/master/URLs/CUDA_URL.json"

#TODO: remove modules that aren't needed
cuda_args = ['nvcc', 'cuobjdump', "nvprune", "cupti", "gpu_library_advisor", "memcheck", "nvdisasm", "nvprof", "visual_profiler", "visual_studio_integration"," demo_suite", "documentation", "cublas", "cublas_dev", "cudart", "cufft", "cufft_dev", "curand", "curand_dev", "cusolver", "cusolver_dev", "cusparse", "cusparse_dev", "nvgraph", "npp", "npp_dev", "nvrtc", "nvrtc_dev", "nvml_dev"]

#This script needs to relaunch itself with elevated privledges, so it has to be a seperate file.

def install_mxnet_cupy_gpu():
    #Installs the appropriate version of mxnet with pip
    root = get_set_root()
    cudafull = get_cuda_ver()
    cudastr = cudafull.replace(".", "")
    mxmodule = "mxnet-cu" + cudastr
    try: 
        subprocess.run([sys.executable, "-m", "pip", "install", mxmodule, "--upgrade"], shell=True, check=True)
    except:
        print("ERROR: mxnet module for CUDA " + cudafull + "is not availible!")
        print("Please install an appropriate version of CUDA and rerun the update script, if you want MXNet processing")
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

def get_cuda_ver():
    CUDAVersion = None
    try: 
        CUDAVersion = str(os.path.basename(os.getenv("CUDA_PATH")))[1:]
    except:
        raise Exception("CUDA is not on PATH. It might be installed incorrectly!")
    if CUDAVersion is None:
        raise Exception("Error getting CUDA version")
    return CUDAVersion

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
    install_mxnet_cupy_gpu()


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
            else:
                install_cuda(urljson)
                cver = get_cuda_ver()
                install_cudnn(cver, urljson)
                print(" ")
            print("Compressing CUDA directory in background...")
            compact(os.path.normpath(os.path.join(os.getenv("programfiles"), "NVIDIA GPU Computing Toolkit")))
        else:
            #But this also seems to be "getting admin privledges?"
            pass
    except Exception as e:
        #Cant seem to write to stderr or stdout from the admin console
        #And I don't know how to stop it from closing
        #Fine... just catch ALL the exceptions and print them
        traceback.print_exc()
        input("Press ENTER to continue...")