import os, json, zipfile, io, urllib.request, shutil, glob, subprocess, sys, time, importlib, threading, tempfile
from urllib.parse import urlparse
from Alpha_SharedFunctions import get_set_root, check_existing_download, download, backupdownload, check_cuda, check_cudnn, get_gpu_vendor, compact


mxurl = "https://api.github.com/repos/kice/vs_mxnet/releases/latest"

pipmodules = ["pyperclip", "Pillow", "elevate", "pySmartDL"]

modelurl = "https://github.com/WolframRhodium/Super-Resolution-Zoo/trunk"

svnurlurl = "https://raw.githubusercontent.com/AlphaAtlas/VapourSynth-Super-Resolution-Helper/master/URLs/SVN_URL"

cpumodule = "mxnet"

gpumodule = "mxnet-cu101mkl"

#TODO: Use pySmartDL JSON fetcher instead
def get_latest_release_github(url):
    #tries to automatically get the latest github release from a repo 
    attempt = 0 
    error = "unknown"
    while attempt <= 3:
        attempt = attempt + 1
        with urllib.request.urlopen(url) as urlstuff:
            data = json.loads(urlstuff.read().decode())
            if urlstuff.getcode() == 200:
                return data['assets'][0]["browser_download_url"]
        print("Error fetching Github release.")
        time.sleep(1)
        print("Trying again...")
    raise Exception("Failed fetching GitHub release with response code " + urlstuff.getcode() + " from " + url)

def download_mx_plugin():
    #Downloads and moves kice's MXNet plugin. Automatically gets newest release. 
    root = get_set_root()
    rurl = get_latest_release_github(mxurl)
    d = download(rurl)
    if os.path.isdir("MXNet"):
        shutil.rmtree("MXNet")
    with tempfile.TemporaryDirectory() as t:    
        zipfile.ZipFile(d).extractall(path=t)
        mxfile = glob.glob(os.path.join(t + "/**/vs_mxnet.dll"), recursive=True)
        os.mkdir("MXNet")
        shutil.move(src=mxfile[0], dst="MXNet")

def install_svn():
    #Downloads SVN, used for selectively pulling giant repos
    root = get_set_root()
    if not os.path.isfile(os.path.join(root, "../bin/PortableSub/bin/svn.exe")):
        #get URL for SVN download
        print("Fetching SVN URL...")
        svnurl = str(urllib.request.urlopen(svnurlurl).read().decode()).rstrip()
        print("Downloading SVN archive...")
        svnarchivedir = download(svnurl)
        s = subprocess.run([os.path.join(root, "../bin/7za.exe"), "x", svnarchivedir, "-o" + os.path.join(root, "../bin/PortableSub"), "-aoa"], check=True, shell=True)



def install_neural_networks():
    #Sets up Neural Networks folder
    root = get_set_root()
    if os.path.isdir(os.path.join(root, "../NeuralNetworks")):
        s = subprocess.run([os.path.join(root, "../bin/PortableSub/bin/svn.exe"), "update", "--set-depth", "immediates", os.path.join(root, "../NeuralNetworks")], check=True, shell=True)
    else:
        s = subprocess.run([os.path.join(root, "../bin/PortableSub/bin/svn.exe"), "checkout", "--depth", "immediates", modelurl, os.path.join(root, "../NeuralNetworks")], check=True, shell=True)
    os.chdir(root)

def install_python_modules():
    #Pip!
    root = get_set_root()
    subprocess.run([sys.executable, "-m", "pip", "install"] + pipmodules + ["--upgrade"], shell=True, check=True)

def install_mxnet():
    #Installs the appropriate version of mxnet with pip
    root = get_set_root()
    module = ""
    if check_cuda() and check_cudnn():
        module = gpumodule
    else:
        module = cpumodule
    subprocess.run([sys.executable, "-m", "pip", "install", module, "--upgrade"], shell=True, check=True)

#TODO: Thread Updates
if __name__ == "__main__":
    root = get_set_root()
    install_python_modules()
    import pySmartDL
    install_svn()
    install_neural_networks()
    download_mx_plugin()
    root = get_set_root()
    compact(os.path.join(root, ".."))
    if get_gpu_vendor()[0] == True:
        #This script needs to relaunch itself for admin privledges
        #Hence it needs to be called as a subprocess
        cudascriptpath = "../HelperScripts/InstallCUDA.py"
        subprocess.run([sys.executable, "-m", "../HelperScripts/InstallCUDA.py"], shell=True, check=True)
    