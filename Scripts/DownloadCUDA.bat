@echo off
setlocal EnableDelayedExpansion
echo Please give this console admin rights to install CUDA
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


rmdir /s /q CUDA_temp
cls
mkdir CUDA_temp
cd CUDA_temp
echo Fetching CUDA Download URL.
for /f "tokens=4-5 delims=. " %%i in ('ver') do set VERSION=%%i.%%j
if "%version%" == "10.0" (
    powershell -Command "(New-Object Net.WebClient).DownloadFile('https://raw.githubusercontent.com/AlphaAtlas/vs_mxnet_helper_helper/master/CUDA_Win10_URL', 'url.txt')"   
) ELSE (
    powershell -Command "(New-Object Net.WebClient).DownloadFile('https://raw.githubusercontent.com/AlphaAtlas/vs_mxnet_helper_helper/master/CUDA_Win_URL', 'url.txt')"
)
set /p URL=<url.txt
del url.txt
echo Downloading Nvidia CUDA archive from %URL%...
powershell -Command "Import-Module BitsTransfer; Start-BitsTransfer %URL% CUDA.exe"
echo Installing CUDA...
echo This won't touch your Nvidia graphics driver, make sure you update it or let Windows do it!
start /I /WAIT /B CUDA.exe -s nvcc_10.0 cuobjdump_10.0 nvprune_10.0 cupti_10.0 gpu_library_advisor_10.0 memcheck_10.0 nvdisasm_10.0 nvprof_10.0 visual_profiler_10.0 visual_studio_integration_10.0 demo_suite_10.0 documentation_10.0 cublas_10.0 cublas_dev_10.0 cudart_10.0 cufft_10.0 cufft_dev_10.0 curand_10.0 curand_dev_10.0 cusolver_10.0 cusolver_dev_10.0 cusparse_10.0 cusparse_dev_10.0 nvgraph_10.0 npp_10.0 npp_dev_10.0 nvrtc_10.0 nvrtc_dev_10.0 nvml_dev_10.0
echo CUDA Installed! 
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://raw.githubusercontent.com/AlphaAtlas/vs_mxnet_helper_helper/master/cuDNN_URL', 'urlc.txt')"
set /p URLC=<urlc.txt
del urlc.txt
echo Downloading ~200MB cuDNN archive...
powershell -Command "Import-Module BitsTransfer; Start-BitsTransfer %URLC% cuDNN.tar.bz2"
echo Installing CUDNN.
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://github.com/AlphaAtlas/vs_mxnet_helper_helper/raw/master/7za.exe', '7za.exe')"
7za.exe x cuDNN.tar.bz2
7za.exe x cuDNN.tar
robocopy Library "%programfiles%\NVIDIA GPU Computing Toolkit\CUDA\v10.0" /e /MOV /XO
echo cuDNN installed! Cleaning up.
cd ..
rmdir /s /q CUDA_temp
echo Compressing...
compact /c /s:"%programfiles%\NVIDIA GPU Computing Toolkit\CUDA\v10.0" /i /q
cls
echo MXNET MIGHT NOT RUN UNTIL YOU RESTART YOUR COMPUTER
pause
