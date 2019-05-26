@echo off

echo Don't click on .bat files you don't trust!
echo.
echo This .bat file will download scripts from https://github.com/AlphaAtlas/VapourSynth-Super-Resolution-Helper
echo Which, in turn, will install Nvidia CUDA related files and download archives from other sources
echo Make sure you have a couple of Gigabytes free on C: and in this directory before continuing.
echo.
pause
cls
del DownloadCUDA.bat
del DownloadVapoursynth.bat
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://raw.githubusercontent.com/AlphaAtlas/VapourSynth-Super-Resolution-Helper/master/SetupScripts/DownloadCUDA.bat', 'DownloadCUDA.bat')"
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://raw.githubusercontent.com/AlphaAtlas/VapourSynth-Super-Resolution-Helper/master/SetupScripts/DownloadVapoursynth.bat', 'DownloadVapoursynth.bat')"
cls
echo If you already have all the necessary CUDA and cuDNN dependancies installed, just close this and
echo run the DownloadVapoursynth.bat file. Otherwise you should uninstall anything that says CUDA
echo in the Windows Control Panel before continuing. You can also run the DownloadCUDA.bat file to
echo just install/reinstall the Nvidia dependancies at any time.
echo.
:choice
set /P c=Are you sure you want to continue[Y/N]?
if /I "%c%" EQU "Y" goto :install
if /I "%c%" EQU "N" goto :eof
goto :choice
:install
start "DownloadCUDA" cmd /c DownloadCUDA.bat
start "DownloadVapoursynth" cmd /c DownloadVapoursynth.bat
