@echo off
start "Updating Vapoursynth Filters" _update_plugins_scripts_vsrepo.bat
call VapourSynth64/python.exe VapoursynthScripts/HelperScripts/SetupScripts.py -m
