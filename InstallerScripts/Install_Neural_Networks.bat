@set gitdir=PortableGit
@set path=%gitdir%\cmd;%path%
@if exist NeuralNetworks\ goto :Update else goto :Install

:Install
@echo Downloading Neural Networks...
@cls
git clone https://github.com/WolframRhodium/Super-Resolution-Zoo.git NeuralNetworks
@goto :eof

:Update
@echo Updating Neural Networks...
@cd NeuralNetworks
@set gitdir="..\PortableGit"
@set path=%gitdir%\cmd;%path%
@git fetch origin
@git reset --hard origin/master
@git pull
