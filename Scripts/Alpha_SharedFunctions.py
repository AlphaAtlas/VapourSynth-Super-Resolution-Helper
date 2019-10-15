import os, sys, subprocess, shutil
from urllib.parse import urlparse

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
            return dlobj.get_dest()
    except:
        if(getjson):
            raise Exception("Fetching JSON from" + dlurl + "failed!")
        print("Download failed! Trying backup method...")
        print(" ")
        return backupdownload(dlurl)

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

def compact(directory):
    subprocess.Popen(["compact", "/C", "/S", "/I", "/Q", directory], creationflags=subprocess.CREATE_NEW_CONSOLE)