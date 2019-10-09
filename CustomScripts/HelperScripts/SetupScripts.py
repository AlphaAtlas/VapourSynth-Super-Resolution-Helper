import urllib, os, json, zipfile, io, requests, shutil, glob, subprocess, sys, time, importlib




#https://stackoverflow.com/questions/12332975/installing-python-module-within-code
def install(package):
    subprocess.call([sys.executable, "-m", "pip", "install", package])

def get_set_root():
    p = os.path.dirname(sys.executable())
    os.chdir(p)
    return p

def get_latest_zip_github(url):
    attempt = 0 
    error = "unknown"
    while attempt <= 3:
        attempt = attempt + 1
        with urllib.request.urlopen(url) as urlstuff:
            data = json.loads(urlstuff.read().decode())
            rurl = data['assets'][0]["browser_download_url"]
            with requests.get(rurl) as r:
                error = r.status_code
                if r.status_code == 200:
                    return zipfile.ZipFile(io.BytesIO(r.content))
        time.sleep(1)
    raise Exception("Failed downloading file with response code " + error + " at " + url)

def get_url():
    pass

def download_mx_plugin():
    root = get_set_root()
    url = "https://api.github.com/repos/kice/vs_mxnet/releases/latest"
    z = get_latest_zip_github(url)
    if os.path.isdir("MXNet"):
        shutil.rmtree("MXNet")
    z.extractall(path="temp")
    filelist = glob.glob("temp/**/vs_mxnet.dll", recursive=True)
    os.mkdir("MXNet")
    shutil.move(src=filelist[0], dst="MXNet")
    shutil.rmtree("temp")

def install_neural_networks():
    model_url = "https://github.com/WolframRhodium/Super-Resolution-Zoo/trunk NeuralNetworks"
    root = get_set_root()
    os.chdir(os.path.join(root , ".."))
    if os.path.isdir("NeuralNetworks"):
        s = subprocess.run(["bin/PortableSub/bin/svn.exe", "update", "--set-depth", "immediates", "NeuralNetworks"], check=True, shell=True)
    else:
        s = subprocess.run(["bin/PortableSub/bin/svn.exe", "checkout --depth immediates", model_url, "NeuralNetworks"], check=True, shell=True)

def install_python_modules():
    modules = "pyperclip Pillow ffmpeg-python, elevate"
    root = get_set_root()
    subprocess.call([sys.executable, "-m", "pip", "install", modules, "--upgrade"])

def CUDA_check():
    return shutil.which("nvcc.exe") is not None

def run_as_admin():
    if importlib.util.find_spec("spam") is None:
        subprocess.call([sys.executable, "-m", "pip", "install", "elevate", "--upgrade"])
    if os.getuid() == 0
    from elevate import elevate



def get_gpu_vendor():
    #Returns a boolean tuple with (Nvidia, AMD, Intel)
    t = (False, False, False) 
    for line in subprocess.check_output("wmic path win32_VideoController get name"):
        if "Nvidia" in line:
            t[0] = True
        if["AMD"] in line:
            t[1] = True
        if["Intel"] in line:
            t[2] = True
    if t == (False, False, False):
        raise Exception("Error finding active graphics card!")
    return t

def check_cudnn()


def install_mxnet():
    if CUDA_check():
