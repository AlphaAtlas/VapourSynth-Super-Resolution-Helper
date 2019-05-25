@echo off
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


del DownloadCUDA.bat
del DownloadVapoursynth.bat
cls
echo Here we go!
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://raw.githubusercontent.com/AlphaAtlas/vs_mxnet_helper_helper/master/Scripts/DownloadCUDA.bat', 'DownloadCUDA.bat')"
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://raw.githubusercontent.com/AlphaAtlas/vs_mxnet_helper_helper/master/Scripts/DownloadVapoursynth.bat', 'DownloadVapoursynth.bat')"
start "DownloadCUDA" cmd /c DownloadCUDA.bat
start "DownloadVapoursynth" cmd /c DownloadVapoursynth.bat
