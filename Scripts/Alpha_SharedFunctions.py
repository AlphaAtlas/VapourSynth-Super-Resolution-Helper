import os, sys, subprocess, shutil
from urllib.parse import urlparse

modelurl = r"""https://www41.zippyshare.com/d/PVqPgXNB/41889/ad_test_tf.pth"""

def check_cuda():
    #Checks if CUDA is on PATH. It could still be broken!
    return (shutil.which("nvcc.exe") is not None) and (os.getenv("CUDA_PATH") is not None)


def get_set_root():
    #Sets root to python directory
    p = os.path.dirname(sys.executable)
    os.chdir(p)
    return p

def check_cudnn():
    #Checks for CUDNN files
    #Not particularly comprehensive...
    return os.path.isfile(os.path.join(os.environ["CUDA_PATH"], "Library/bin/cudnn64_7.dll"))

def check_existing_download(durl, reuse=False):
    #Checks if a download matching the url already exists, returns the path or None
    size = 0
    try: 
        size = pySmartDL.utils.get_filesize(durl)
    except:
    #    print("Error getting size of " + durl)
    #    print(" ")
        pass
    urlfile = os.path.basename(urlparse(durl)[2])
    s = os.path.join(os.getenv("TEMP"), "pySmartDL", urlfile)
    b = os.path.isfile(s)
    if (b) and (size is not 0):
        if (os.stat(s).st_size == size):
            print("Existing file with matching size found! Skipping download...")
            print(" ")
            return s
        os.remove(s)
        return None
    if b and reuse:
        print("Target download found on disk, but it can't be verified!")
        print("It might be an incomplete download, or it might be OK.")
        print("Would you like to try and reuse the file anyway?")
        print(" ")
        i = input("Y/N: ")
        if i.lower() == "y":
            return s
    return None


def backupdownload(dlurl):
    #Some URLs just always fail on certain systems with Python and Windows BITS, yet work fine from a browser.
    #I don't know why...
    #Fine. We can shell out to powershell (which seems to work for some reason (sometimes))
    urlfile = os.path.basename(urlparse(dlurl)[2])
    filepath = os.path.join(os.getenv("TEMP"), "pySmartDL", urlfile)
    folderpath = os.path.join(os.getenv("TEMP"), "pySmartDL")
    cwd = os.getcwd()
    if not os.path.isdir(folderpath):
        os.mkdir(folderpath)
    if os.path.isfile(filepath):
        os.remove(filepath)
    os.chdir(folderpath)
    #   *Holds Breath*
    s = r"""-Command "(New-Object Net.WebClient).DownloadFile('""" + dlurl + r"""', '""" + filepath + r'''')"'''
    subprocess.run("powershell.exe " + s, shell = True, check=True)
    os.chdir(cwd)
    return filepath


def download(dlurl, getjson = False, reuse=False):
    #Wrapper for pySmartDL
    #Uses locally cached files if the size is correct
    #Delete %TEMP%/pySmartDL if you get a corrupted download!
    #Returns either a directory, or a json dict
    try: 
        import pySmartDL
    except:
        pass
    check = check_existing_download(dlurl, reuse)
    if check is not None:
        return check
    try:
        dlobj = pySmartDL.SmartDL(dlurl, timeout = 20)
        dlobj.fetch_hash_sums()
        dlobj.start(blocking=True)
        if(getjson):
            return dlobj.get_json()
        else:
            return os.path.normpath(dlobj.get_dest())
    except:
        if(getjson):
            raise Exception("Fetching JSON from" + dlurl + "failed!")
        print("Download failed! Trying backup method...")
        print(" ")
        return os.path.normpath(backupdownload(dlurl))

#TODO: Multi GPU vendor support?
def get_gpu_vendor():
    #Returns a boolean list with (Nvidia, AMD, Intel)
    t = [False, False, False] 
    line = str(subprocess.check_output("wmic path win32_VideoController get name"))
    if "nvidia" in line.lower():
        t[0] = True
    if "amd" in line.lower():
        t[1] = True
    if "intel" in line.lower():
        t[2] = True
    if t == [False, False, False]:
        raise Exception("Error finding active graphics card manufacturer!")
    return t

def get_cuda_ver():
    CUDAVersion = None
    try: 
        CUDAVersion = str(os.path.basename(os.getenv("CUDA_PATH")))[1:]
    except:
        raise Exception("CUDA is not on PATH. It might be installed incorrectly!")
    if CUDAVersion is None:
        raise Exception("Error getting CUDA version")
    return CUDAVersion

def create_vsgan_folder():
    root = get_set_root()
    if not os.path.isdir("../ESRGANModels"):
        modeldir = None
        try: 
            print("Downloading example ESRGAN model from: ")
            print("https://upscale.wiki/wiki/Model_Database#Cartoon_.2F_Comic_2")
            print(" ")
            dlpath = download(modelurl)
            if modeldir is not None:
                zippath = os.path.normpath(os.path.join(root, r"../bin/7za.exe"))
                modelpath = os.path.normpath(os.path.join(root, r"../ESRGANModels"))
                os.mkdir(modelpath)
                s = subprocess.run([zippath, "x", dlpath , "-o" + modelpath, "-aoa"], check=True, shell=True)
        except:
            print("Error downloading example ESRGAN model!")
            print(" ")






def compact(directory):
    subprocess.Popen(["compact", "/C", "/S", "/I", "/Q", directory], creationflags=subprocess.CREATE_NEW_CONSOLE)