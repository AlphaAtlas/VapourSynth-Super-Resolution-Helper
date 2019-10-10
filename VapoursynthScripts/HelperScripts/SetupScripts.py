import os, json, zipfile, io, urllib.request, shutil, glob, subprocess, sys, time, importlib, threading, tempfile
from pySmartDL import SmartDL
from urllib.parse import urlparse
from .InstallCUDA import check_cuda, check_cudnn

mxurl = "https://api.github.com/repos/kice/vs_mxnet/releases/latest"

pipmodules = "pyperclip Pillow ffmpeg-python elevate pySmartDL"

modelurl = "https://github.com/WolframRhodium/Super-Resolution-Zoo/trunk"

svnurlurl = "https://raw.githubusercontent.com/AlphaAtlas/VapourSynth-Super-Resolution-Helper/master/URLs/SVN_URL"

def get_set_root():
    p = os.path.dirname(sys.executable)
    os.chdir(p)
    return p

def check_existing_download(durl, size=None):
    urlfile = os.path.basename(urlparse(durl)[2])
    s = os.path.join([os.getenv("TEMP"), "/pySmartDL/", urlfile])
    if os.path.isfile(s):
        if size is not None: 
            if (os.stat(s).st_size == size):
                print("Existing file with matching size found! Skipping download...")
                return s
    return None

#todo: checksum? more retries?
def download(dlurl, retry = True):
    with SmartDL(dlurl) as dlobj:
        s = dlobj.get_final_filesize()
        c = check_existing_download(dlurl, size=s)  
        if c is not None:
            return c
        dlobj.start()
        dlobj.wait()
        if (not dlobj.isSuccessful()) or (os.stat(dlobj.get_dest()).st_size != s):
            if retry == True:
                print("Download failed. Trying again...")
                return download(dlurl, retry = False) 
            else:
                raise Exception("Download from " + dlurl + "failed!")
        return dlobj.get_dest()

def get_latest_release_github(url):
    #tries to automatically get the latest github release
    attempt = 0 
    error = "unknown"
    while attempt <= 3:
        attempt = attempt + 1
        with urllib.request.urlopen(url) as urlstuff:
            data = json.loads(urlstuff.read().decode())
            if urlstuff.getcode() == 200:
                return json.loads(data)['assets'][0]["browser_download_url"]
        print("Error fetching Github release.")
        time.sleep(1)
        print("Trying again...")
    raise Exception("Failed fetching GitHub release with response code " + urlstuff.getcode() + " from " + url)

def download_mx_plugin():
    root = get_set_root()
    rurl = get_latest_release_github(mxurl)
    d = download(rurl)
    if os.path.isdir("MXNet"):
        shutil.rmtree("MXNet")
    with tempfile.TemporaryDirectory() as t:    
        zipfile.ZipFile(d).extractall(path=t.gettempdir())
        filelist = glob.glob(t.gettempdir() + "/temp/**/vs_mxnet.dll", recursive=True)
        os.mkdir("MXNet")
        shutil.move(src=filelist[0], dst="MXNet")

def install_svn():
    root = get_set_root()
    #get URL for SVN download
    print("Fetching SVN URL...")
    svnurl = str(urllib.request.urlopen(svnurlurl).read().decode()).rstrip()
    print("Downloading SVN archive...")
    svnarchivedir = download(svnurl)
    s = subprocess.run(["../bin/7za.exe", "x", svnarchivedir, "-o" + os.path.join(root, "../bin/PortableSub"), "-aoa"], check=True, shell=True)
    os.chdir(os.path.join(root , ".."))



def install_neural_networks():
    root = get_set_root()
    os.chdir(os.path.join(root , ".."))
    if os.path.isdir("NeuralNetworks"):
        s = subprocess.run(["bin/PortableSub/bin/svn.exe", "update", "--set-depth", "immediates", "NeuralNetworks"], check=True, shell=True)
    else:
        s = subprocess.run(["bin/PortableSub/bin/svn.exe", "checkout --depth immediates", modelurl, "NeuralNetworks"], check=True, shell=True)
    os.chdir(root)

def install_python_modules():
    root = get_set_root()
    subprocess.run([sys.executable, "-m", "pip", "install", pipmodules, "--upgrade"], shell=True, check=True)

def get_gpu_vendor():
    #Returns a boolean tuple with (Nvidia, AMD, Intel)
    t = (False, False, False) 
    for line in subprocess.check_output("wmic path win32_VideoController get name"):
        if "Nvidia" in line:
            t[0] = True
        if "AMD" in line:
            t[1] = True
        if "Intel" in line:
            t[2] = True
    if t == (False, False, False):
        raise Exception("Error finding active graphics card manufacturer!")
    return t

def install_mxnet():
    root = get_set_root()
    cpumodule = "mxnet"
    gpumodule = "mxnet-cu101mkl"
    module = ""
    if check_cuda() and check_cudnn():
        module = gpumodule
    else:
        module = cpumodule
    subprocess.run([sys.executable, "-m", "pip", "install", module, "--upgrade"], shell=True, check=True)

if __name__ == "__main__":
    root = get_set_root()
    install_python_modules()
#    t = threading.Thread(target=install_neural_networks)
#    t.start()
#    t2 = threading.Thread(target=download_mx_plugin)
#    t2.start()
    install_neural_networks()
    download_mx_plugin()
    if get_gpu_vendor()[0] == True:
        #This script needs to relaunch itself for admin privledges
        #Hence it needs to be called as a subprocess
        cudascriptpath = "../HelperScripts/InstallCUDA.py"
        subprocess.run([sys.executable, "-m", "../HelperScripts/InstallCUDA.py"], shell=True, check=True)
    
#    t.join()
#    t2.join()