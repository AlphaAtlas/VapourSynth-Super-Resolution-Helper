@echo off

echo Don't click on .bat files you don't trust!
echo.
echo.
echo This .bat file will download scripts from https://github.com/AlphaAtlas/VapourSynth-Super-Resolution-Helper
echo.
echo Which, in turn, will install Nvidia CUDA related files and download archives from other sources, if applicable.
echo. 
echo Make sure you have a at least 10GB free in this directory, some free space on C: for CUDA and an internet connection before continuing!
echo.

:choice1
set /P c=Do you want to continue[Y/N]?
if /I "%c%" EQU "Y" goto :CheckFreeSpace
if /I "%c%" EQU "N" goto :eof
goto :choice1

:CheckFreeSpace
for /f "usebackq delims== tokens=2" %%x in (`wmic logicaldisk where "DeviceID='%CD:~0,2%'" get FreeSpace /format:value`) do set FreeSpace=%%x
if %FreeSpace:~0,-6% LEQ 10000 (
    echo You need at least 10GB of free space!
    timeout 10
    goto :eof
)


cls
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
SET count=1
FOR /F "tokens=* USEBACKQ" %%F IN (`wmic path win32_VideoController get name`) DO (
  SET var!count!=%%F
  SET /a count=!count!+1
)

ECHO Currently Enabled Graphics Card: %var2%
ECHO.%var2% | FIND /I "Intel">Nul && (GOTO IntelText)
ECHO.%var2% | FIND /I "Nvidia">Nul && (GOTO NvidiaText)
ECHO.%var2% | FIND /I "AMD">Nul && (GOTO AMDText)
ECHO Error detecting graphics!
PAUSE
EXIT

:IntelText
cls
echo Intel graphics detected: %var2%
echo.
echo If you're on a laptop or an iMac-style all-in-one computer,
echo you should force enable your main Nvidia/AMD graphics card.
echo 
echo.
echo If you have no active dedicated graphics card,
echo upscaling will be VERY slow. 
echo.
pause
goto :VSCheck

:AMDText
cls
echo AMD graphics detected: %var2%
echo.
echo MXNet upscaling will only run on the CPU, which is VERY slow.
echo However, Waifu2X and GPU denoising will work fine, even on AMD integrated graphics.  
echo. 
echo If you just want to upscale videos with Waifu2X quickly,
echo I recommend trying Dandere2x or Video2X:
echo.
echo https://github.com/aka-katto/dandere2x
echo.
echo https://github.com/k4yt3x/video2x
echo.
echo You could also try setting up VapourSynth and AMD ROCm on Linux.
echo.
pause
goto :VSCheck

:NvidiaText
cls
echo Nvidia graphics detected and active: %var2%
timeout 5
goto :VSCheck

:VSCheck
echo.
echo Downloading the Vapoursynth FatPack Installer...
del DownloadVapoursynth.bat
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://raw.githubusercontent.com/AlphaAtlas/VapourSynth-Super-Resolution-Helper/master/SetupScripts/DownloadVapoursynth.bat', 'DownloadVapoursynth.bat')"
start "DownloadVapoursynth" cmd /c DownloadVapoursynth.bat
ENDLOCAL
echo Installers launched! Please check the other open cmd windows. 
timeout 10
