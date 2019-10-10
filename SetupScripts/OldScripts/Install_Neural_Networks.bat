@echo off
cls
if exist NeuralNetworks\ goto :Update else goto :Install
:Install
echo Setting Up Neural Network Folders.
echo Algorithms will be downloaded as needed by Generate_Script.py
call "bin/PortableSub/bin/svn.exe" checkout --depth immediates https://github.com/WolframRhodium/Super-Resolution-Zoo/trunk NeuralNetworks
goto:eof

:Update
call "bin/PortableSub/bin/svn.exe" update --set-depth immediates NeuralNetworks