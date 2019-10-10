@ECHO OFF
setLocal EnableDelayedExpansion


echo Starting x265 10 bit encode 
echo.


set out=gpuencode.mkv

set vs="..\VapourSynth64\vspipe.exe"
set script="ExampleAuto.vpy"
set encbin=..\bin


%vs% --y4m %script% - | %encbin%\ffmpeg.exe -i pipe: %out% -c:v hevc_nvenc -profile:v main10 -preset slow

pause