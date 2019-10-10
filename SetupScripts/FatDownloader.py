import os, sys, shutil, subprocess, urllib.request, tempfile
from pprint import pprint
from urllib.parse import urlparse
from pySmartDL import SmartDL
faturlurl = "https://raw.githubusercontent.com/AlphaAtlas/VapourSynth-Super-Resolution-Helper/master/URLs/FATPACK_URL"
zipurl = "https://github.com/AlphaAtlas/VapourSynth-Super-Resolution-Helper/raw/master/bin/7za.exe"
helperurl = "https://github.com/AlphaAtlas/VapourSynth-Super-Resolution-Helper/archive/master.zip"

def check_existing_download(durl, size=None):
    urlfile = os.path.basename(urlparse(durl)[2])
    s = os.path.join([os.getenv("TEMP"), "/pySmartDL/", urlfile])
    if os.path.isfile(s):
        if size is not None: 
            if (os.stat(s).st_size == size):
                print("Existing file with matching size found! Skipping download...")
                return s
    return None

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

def get_gpu_vendor():
    #Returns a boolean tuple with (Nvidia, AMD, Intel)
    t = (False, False, False) 
    for line in subprocess.check_output("wmic path win32_VideoController get name"):
        if "Nvidia" in line:
            pprint("Nvidia graphics detected and active!")
            pprint("As long as your graphics card isn't ancient, and your drivers are reasonably up to date, your GPU should accelerate MXNet processing.")
            pprint(" ")
            input("Press ENTER to continue...")
            t[0] = True
        if "AMD" in line:
            pprint("AMD graphics detected!")
            pprint("MXNet upscaling will only run on the CPU, which is VERY slow.")
            pprint("However, Waifu2X, GPU denoising and other OpenCL filters will work fine, even on AMD integrated graphics.")
            pprint("If you just want to upscale videos with Waifu2X quickly, I recommend trying Dandere2x or Video2X:")
            pprint("https://github.com/aka-katto/dandere2x")
            pprint("https://github.com/k4yt3x/video2x")
            pprint(" ")
            pprint("Theoretically you could set up Vapoursynth and AMD ROCm on Linux, but good luck with that...")
            pprint(" ")
            input("Press ENTER to continue...")
            t[1] = True
        if "Intel" in line:
            pprint("Intel graphics detected!")
            pprint("If you're on a laptop or an iMac-style all-in-one computer, you should force enable your main Nvidia/AMD graphics card.")
            pprint("If you have no active dedicated graphics card, upscaling will be CPU only and VERY slow.")
            pprint(" ")
            input("Press ENTER to continue...")
            t[2] = True
    if t == (False, False, False):
        raise Exception("Error finding active graphics card manufacturer!")
    return t

if __name__ == "__main__":
    pprint(r"This exe will download scripts from https://github.com/AlphaAtlas/VapourSynth-Super-Resolution-Helper")
    pprint(r"Make sure you have a at least 10GB free in this directory, some free space on C: for CUDA and an internet connection before continuing!")
    c = input("Do you want to continue[Y/N]")
    if c.lower() != "y":
        raise Exception("You didn't type y!")
    path = os.cwd() 
    #get free space
    if shutil.disk_usage(path)[2] < 10000000000:
        raise Exception("You should have at least 10GB of free disk space!")
    gpu = get_gpu_vendor()
    cwd = os.getcwd()
    os.system('cls')
    if os.path.isdir(os.path.join(cwd, "VapourSynth64Portable")):
        pprint("Existing VapourSynth Fatpack installation found in this directory. Please delete it or move this installer somewhere else!")
        pprint("If you just want to update everything, please use the updater batch file")
        pprint(" ")
        input("Press ENTER to continue...")
        raise Exception("Existing VapourSynth Fatpack installation found.")
    pprint("Downloading Vapoursynth FatPack URL...")
    url = None
    faturl = str(urllib.request.urlopen(faturlurl).read().decode()).rstrip()
    pprint("Downloading Vapoursynth FatPack...")
    fatarchivedir = download(faturl)
    pprint("Downloading 7zip...")
    zipexedir = download(zipurl)
    pprint("Extracting FatPack...")
    subprocess.run([zipexedir, "x", fatarchivedir, "-o" + cwd], shell=True, check=True)
    pprint("Downloading Super-Resolution Helper Repo...")
    helperarchivedir = download(helperurl)
    pprint("Extracting Super-Resolution Helper Stuff...")
    with tempfile.TemporaryDirectory() as t:
        subprocess.run([zipexedir, "x", helperarchivedir, "-o" + t.gettempdir()], shell=True, check=True)
        shutil.rmtree(os.path.join(t.gettempdir(), "VapourSynth-Super-Resolution-Helper-master/URLs"), ignore_errors = False)
        shutil.rmtree(os.path.join(t.gettempdir(), "VapourSynth-Super-Resolution-Helper-master/SetupScripts"), ignore_errors = False)
        shutil.move(os.path.join(t.gettempdir(), "VapourSynth-Super-Resolution-Helper-master"), os.path.join(cwd, "VapourSynth64Portable"))
    subprocess.Popen(["VapourSynth64Portable/VapourSynth64/python.exe", "VapourSynth64Portable/VapourSynthScripts/HelperScripts/SetupScripts.py" "-m" ])