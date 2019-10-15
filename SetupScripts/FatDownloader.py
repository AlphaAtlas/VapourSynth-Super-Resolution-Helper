import os, sys, shutil, subprocess, urllib.request, tempfile, time, traceback
from urllib.parse import urlparse
import pySmartDL
faturlurl = "https://raw.githubusercontent.com/AlphaAtlas/VapourSynth-Super-Resolution-Helper/master/URLs/FATPACK_URL"
zipurl = "https://github.com/AlphaAtlas/VapourSynth-Super-Resolution-Helper/raw/master/bin/7za.exe"
helperurl = "https://github.com/AlphaAtlas/VapourSynth-Super-Resolution-Helper/archive/master.zip"
svnurlurl = "https://raw.githubusercontent.com/AlphaAtlas/VapourSynth-Super-Resolution-Helper/master/URLs/SVN_URL"
#https://lukelogbook.tech/2018/01/25/merging-two-folders-in-python/
#recursively merge two folders including subfolders
def mergefolders(root_src_dir, root_dst_dir):
    for src_dir, dirs, files in os.walk(root_src_dir):
        dst_dir = src_dir.replace(root_src_dir, root_dst_dir, 1)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                os.remove(dst_file)
            shutil.copy(src_file, dst_dir)

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



def get_gpu_vendor():
    #Returns a boolean tuple with (Nvidia, AMD, Intel)
    #Todo: add support for multiple GPUs?
    t = [False, False, False] 
    line = str(subprocess.check_output("wmic path win32_VideoController get name"))
    print(line)
    if "nvidia" in line.lower():
        os.system('cls')
        print("Nvidia graphics detected and active.")
        print("Your GPU should accelerate MXNet processing.")
        print(" ")
        input("Press ENTER to continue...")
        t[0] = True
    if "amd" in line.lower():
        os.system('cls')
        print("AMD graphics detected.")
        print("MXNet upscaling will only run on the CPU, which is VERY slow.")
        print("However, Waifu2X, GPU denoising and other OpenCL filters will work fine, even on AMD integrated graphics.")
        print("If you just want to upscale videos with Waifu2X quickly, I recommend trying Dandere2x or Video2X:")
        print("https://github.com/aka-katto/dandere2x")
        print("https://github.com/k4yt3x/video2x")
        print(" ")
        input("Press ENTER to continue...")
        t[1] = True
    if "intel" in line.lower():
        os.system('cls')
        print("Intel graphics detected.")
        print("If you're on a laptop or an iMac-style all-in-one computer, you should force enable your main Nvidia/AMD graphics card.")
        print("If you have no active dedicated graphics card, upscaling will be CPU only and VERY slow.")
        print("OpenCL filters may or may not run on your IGP, depending on how new it is.")
        print(" ")
        input("Press ENTER to continue...")
        t[2] = True
    if t == [False, False, False]:
        raise Exception("Error finding active graphics card manufacturer!")
    return t

if __name__ == "__main__":
    try:
        print(r"This exe will download scripts from https://github.com/AlphaAtlas/VapourSynth-Super-Resolution-Helper")
        print("Make sure you have a at least 10GB free in this directory, some free space on C: for CUDA and an internet connection before continuing!")
        print(" ")
        c = input("Do you want to continue? [Y/N]")
        if c.lower() != "y":
            raise Exception("You didn't type Y!")
        #get free space
        cwd = os.getcwd()
        if shutil.disk_usage(cwd)[2] < 10000000000:
            raise Exception("You should have at least 10GB of free disk space!")
        gpu = get_gpu_vendor()
        os.system('cls')
        if os.path.isdir(os.path.join(cwd, "VapourSynth64Portable")):
            print("Existing VapourSynth Fatpack installation found in this directory. Please delete it or move this installer somewhere else!")
            print("If you just want to update everything, please use the updater batch file")
            print(" ")
            input("Press ENTER to continue...")
            sys.exit()
        print("Downloading Vapoursynth FatPack URL...")
        #get download URLs from repo
        faturl = str(urllib.request.urlopen(faturlurl).read().decode()).rstrip()
        svnurl = str(urllib.request.urlopen(svnurlurl).read().decode()).rstrip()
        #TODO: Start a threadpool for all these downloads. 
        print("Downloading 7zip...")
        zipexedir = download(zipurl)
        print("Downloading Vapoursynth FatPack...")
        fatarchivedir = download(faturl)
        print("Downloading Super-Resolution Helper Repo...")
        helperarchivedir = download(helperurl)
        print("Downloading SVN archive...")
        svnarchivedir = download(svnurl)
        #TODO: Thread some of these 7zip calls while downloads are running in the background.
        print("Extracting FatPack...")
        subprocess.run([zipexedir, "x", fatarchivedir, "-o" + cwd], shell=True, check=True)  
        print("Extracting Super-Resolution Helper Stuff...")
        with tempfile.TemporaryDirectory() as t:
            subprocess.run([zipexedir, "x", helperarchivedir, "-o" + t], shell=True, check=True)
            shutil.rmtree(os.path.join(t, "VapourSynth-Super-Resolution-Helper-master/URLs"), ignore_errors = False)
            shutil.rmtree(os.path.join(t, "VapourSynth-Super-Resolution-Helper-master/SetupScripts"), ignore_errors = False)
            os.rename(os.path.join(t, "VapourSynth-Super-Resolution-Helper-master"), os.path.join(t, "VapourSynth64Portable"))
            mergefolders(os.path.join(t, "VapourSynth64Portable"), os.path.join(cwd, "VapourSynth64Portable"))
        subprocess.run([zipexedir, "x", svnarchivedir, "-o" + "VapourSynth64Portable/bin/PortableSub"], check=True, shell=True)
        subprocess.Popen(["VapourSynth64Portable/VapourSynth64/python.exe", "VapourSynth64Portable/Scripts/Alpha_SetupScripts.py"], creationflags=subprocess.CREATE_NEW_CONSOLE)
    except Exception as e:
    #SHOW ME WHAT YOU GOT
        traceback.print_exc()
        input("Press ENTER to continue...")