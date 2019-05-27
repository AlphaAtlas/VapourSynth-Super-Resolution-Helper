@echo off
echo Running ProcessImagesAuto.vpy
"../VapourSynth64/vspipe.exe" -a nopreview=1 -p ProcessImagesAuto.vpy .
"../VapourSynth64/python.exe" HelperScripts/ImageMover.py
pause