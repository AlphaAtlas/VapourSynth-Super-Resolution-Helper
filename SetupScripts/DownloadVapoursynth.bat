@echo off
if exist VapourSynth64Portable\ (
    echo Portable VapourSynth is already installed here!
    echo Please delete it or install somewhere else.
    pause
    goto :eof
)
rmdir /s /q download_temp
cls
mkdir download_temp
cd download_temp
echo Fetching URL.
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://raw.githubusercontent.com/AlphaAtlas/VapourSynth-Super-Resolution-Helper/master/URLs/Latest_FATPack_URL', 'url.txt')"
set /p VSURL=<url.txt
del url.txt
echo Downloading a ~100MB archive from 
echo %VSURL%
echo ...
powershell -Command "(New-Object Net.WebClient).DownloadFile('%VSURL%', 'fatpack.7z')"
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://github.com/AlphaAtlas/VapourSynth-Super-Resolution-Helper/archive/master.zip', 'GitHubArchive.zip')"
echo Downloading 7zip...
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://github.com/AlphaAtlas/VapourSynth-Super-Resolution-Helper/raw/master/bin/7za.exe', '7za.exe')"
echo Extracting portable Vapoursynth pack...
7za.exe x fatpack.7z -o.. -aoa
7za.exe x GitHubArchive.zip
rmdir /S /Q "VapourSynth-Super-Resolution-Helper-master/URLs"
rmdir /S /Q "VapourSynth-Super-Resolution-Helper-master/SetupScripts"
robocopy VapourSynth-Super-Resolution-Helper-master ..\VapourSynth64Portable /e /MOV /XO
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://raw.githubusercontent.com/AlphaAtlas/VapourSynth-Super-Resolution-Helper/master/URLs/SVN_URL', 'url.txt')"
set /p SVNURL=<url.txt
del url.txt
echo Downloading a portable SVN archive from %SVNURL%...
powershell -Command "(New-Object Net.WebClient).DownloadFile('%SVNURL%', 'Subversion.zip')"
echo Extracting Subversion...
7za.exe x Subversion.zip -o"..\VapourSynth64Portable\bin\PortableSub" -aoa
cd ..\VapourSynth64Portable\
echo Cleaning up.
rmdir /s /q "../download_temp"
start /wait "Even More Installing" cmd /c _install_and_update_everything.bat
echo Compressing...
compact /c /s * /i /q
timeout 10
