@echo off
call InstallerScripts/Install_MXNet.bat
cls
cd %~dp0
call InstallerScripts/Install_Neural_Networks.bat
cd %~dp0
cd VapourSynth64
python.exe ../InstallerScripts/Download.py -m
cd ../extras
start "Updating Vapoursynth Filters" _update_plugins_scripts_vsrepo.bat
echo Done!
