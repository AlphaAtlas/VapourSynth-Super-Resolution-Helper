@echo off
if exist VapourSynth64Portable\ (
    echo Portable VapourSynth is already installed here!
    echo Please delete it or install somewhere else.
    pause
    goto :eof
)
for /f "usebackq delims== tokens=2" %%x in (`wmic logicaldisk where "DeviceID='%CD:~0,2%'" get FreeSpace /format:value`) do set FreeSpace=%%x
if %FreeSpace:~0,-6% LEQ 12880 (
    echo You need at least 12GB of free space!
    timeout 10
    goto :eof
)
rmdir /s /q download_temp
cls
mkdir download_temp
cd download_temp
echo Fetching URL.
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://raw.githubusercontent.com/AlphaAtlas/vs_mxnet_helper_helper/master/Latest_FATPack_URL', 'url.txt')"
set /p VSURL=<url.txt
del url.txt
echo Downloading a ~100MB archive from %VSURL%...
powershell -Command "Import-Module BitsTransfer; Start-BitsTransfer %VSURL% fatpack.7z"
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://github.com/AlphaAtlas/vs_mxnet_helper/archive/master.zip', 'vs_mxnet_helper-master.zip')"
echo Downloading 7zip...
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://github.com/AlphaAtlas/vs_mxnet_helper_helper/raw/master/7za.exe', '7za.exe')"
echo Extracting portable Vapoursynth pack...
7za.exe x fatpack.7z -o.. -aoa
7za.exe x vs_mxnet_helper-master.zip 
robocopy vs_mxnet_helper-master ..\VapourSynth64Portable /e /MOV /XO
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://raw.githubusercontent.com/AlphaAtlas/vs_mxnet_helper_helper/master/Git_URL', 'url.txt')"
set /p GitURL=<url.txt
del url.txt
echo Downloading a ~100MB portable Git archive from %GitURL%...
powershell -Command "(New-Object Net.WebClient).DownloadFile('%GitURL%', 'PortableGit.exe')"
echo Extracting git...
mkdir ..\VapourSynth64Portable\PortableGit
7za.exe x PortableGit.exe -o..\VapourSynth64Portable\PortableGit -aoa
cd ..\VapourSynth64Portable\PortableGit
start /wait "Post-Install" cmd /c post-install.bat
cd ..
start /wait "Even More Installing" cmd /c _install_and_update_everything.bat
echo Compressing...
compact /c /s * /i /q
echo Cleaning up.
cd ..
rmdir /s /q download_temp
timeout 10
