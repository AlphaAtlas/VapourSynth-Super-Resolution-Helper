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
    return os.path.isfile(os.path.join(os.environ("CUDA_PATH"), "Library/bin/cudnn64_7.dll"))

def check_existing_download(durl):
    #Checks if a download matching the url already exists, returns the path or None
    size = 0
    try: 
        size = pySmartDL.utils.get_filesize(durl)
    except:
        print("Error getting size of " + durl)
    urlfile = os.path.basename(urlparse(durl)[2])
    s = os.path.join(os.getenv("TEMP"), "pySmartDL", urlfile)
    if os.path.isfile(s):
        if size is not 0:
            if (os.stat(s).st_size == size):
                print("Existing file with matching size found! Skipping download...")
                return s
        os.remove(s)
    return None

def backupdownload(dlurl):
    #Some URLs just always fail on certain systems with Python and BITS, yet work fine from a browser.
    #I don't know why...
    #Fine. We can shell out to powershell (which seems to work for some reason)
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


def download(dlurl):
    #Wrapper for pySMartDL
    #Uses cached files if the size is correct
    #Doesn't check hashes yet, delete %TEMP% if you get a corrupted download
    try: 
        import pySmartDL
    except:
        pass
    check = check_existing_download(dlurl)
    if check is not None:
        return check
    try:
        dlobj = pySmartDL.SmartDL(dlurl, timeout = 20)
        dlobj.start(blocking=True)
        return dlobj.get_dest()
    except:
        print("Download failed! Trying backup method...")
        return backupdownload(dlurl)

#TODO: Multi GPU vendor support?
def get_gpu_vendor():
    #Returns a boolean list with (Nvidia, AMD, Intel)
    t = [False, False, False] 
    line = str(subprocess.check_output("wmic path win32_VideoController get name"))
    if "Nvidia" in line:
        t[0] = True
    if "AMD" in line:
        t[1] = True
    if "Intel" in line:
        t[2] = True
    if t == [False, False, False]:
        raise Exception("Error finding active graphics card manufacturer!")
    return t

def compact(directory):
    subprocess.Popen(["compact", "/C", "/S", "/I", "/Q", directory])