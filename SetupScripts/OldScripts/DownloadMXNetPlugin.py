import urllib.request, os, json, zipfile, io, requests, shutil, glob

url = " "
with urllib.request.urlopen("https://api.github.com/repos/kice/vs_mxnet/releases/latest") as url:
    data = json.loads(url.read().decode())
    url = data['assets'][0]["browser_download_url"]
r = requests.get(url)
z = zipfile.ZipFile(io.BytesIO(r.content))
try:
    shutil.rmtree("MXNet")
except:
    print(" ")
z.extractall(path="temp")
filelist = glob.glob("temp/**/vs_mxnet.dll", recursive=True)
os.mkdir("MXNet")
shutil.move(src=filelist[0], dst="MXNet")
shutil.rmtree("temp")
