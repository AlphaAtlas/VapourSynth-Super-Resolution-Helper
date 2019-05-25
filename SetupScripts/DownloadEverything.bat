@echo off

echo "Don't click on .bat files you don't trust!""
echo " "
echo "This .bat file will download scripts from https://github.com/AlphaAtlas/VapourSynth-Super-Resolution-Helper"
echo "Which, in turn, will install Nvidia CUDA related files and download archives from other sources"
echo "into a folder in this directory. Make sure you have a couple of Gigabytes free on C: and in this"
echo "directory before continuing."
echo " "
pause
cls
del DownloadCUDA.bat
del DownloadVapoursynth.bat
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://raw.githubusercontent.com/AlphaAtlas/VapourSynth-Super-Resolution-Helper/master/Scripts/DownloadCUDA.bat', 'DownloadCUDA.bat')"
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://raw.githubusercontent.com/AlphaAtlas/VapourSynth-Super-Resolution-Helper/master/Scripts/DownloadVapoursynth.bat', 'DownloadVapoursynth.bat')"
cls
echo "If you already have all the necessary CUDA and cuDNN dependancies installed, just close this and" 
echo "run the DownloadVapoursynth.bat file. Otherwise you should uninstall anything that says CUDA" 
echo "in the Windows Control Panel before continuing. You can also run the DownloadCUDA.bat file to"
echo "just install/reinstall the Nvidia dependancies" 
echo " "
:choice
set /P c=Are you sure you want to continue[Y/N]?
if /I "%c%" EQU "Y" goto :install
if /I "%c%" EQU "N" goto :eof
goto :choice

:install
cls
echo Please give this console window admin rights to install CUDA
:: BatchGotAdmin
:-------------------------------------
REM  --> Check for permissions
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"

REM --> If error flag set, we do not have admin.
if '%errorlevel%' NEQ '0' (
    echo Requesting administrative privileges...
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    set params = %*:"=""
    echo UAC.ShellExecute "cmd.exe", "/c %~s0 %params%", "", "runas", 1 >> "%temp%\getadmin.vbs"

    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    pushd "%CD%"
    CD /D "%~dp0"
:--------------------------------------

start "DownloadCUDA" cmd /c DownloadCUDA.bat
start "DownloadVapoursynth" cmd /c DownloadVapoursynth.bat
