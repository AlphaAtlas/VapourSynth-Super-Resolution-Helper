# vs_mxnet_helper_helper
A fast, easy way to get started with neural network image/video processing in Windows.

*WIP*

Requirements:
- A Kepler (GTX 600 series+) or better Nvidia GPU.
- Plenty of free disk space (at least 10 GB anywhere you want, plus ~2GB in C:/Program Files for CUDA).
- An internet connection than can handle several gigabytes of downloads. 
- Windows 10 (recommended), 8.1, or 7.

Instructions: 

- Download this .bat file: 
- Put it somewhere you have space.
- Double click it it.
- Wait. 

Usage Instructions:

*Under Construction*

- "install_and_update_everything.bat" does just what it says. 

- You can run "select_neural_network.bat" at any time, as long as the scripts aren't open in an editor. Every .vpy script that ends in "Auto" will automatically be updated. MSRN is selected by default, but you can choose from any of the scripts in WolframRhodium's Super Resolution Zoo repo, and it'll automatically change the algorithm in the processing scripts. If you're interested in learning more about each algorithm, you can look through the "NeuralNetworks" folder, or poke through the repo here: https://github.com/WolframRhodium/Super-Resolution-Zoo

- To run a script, click the "VapourSynth Editor.exe" shortcut. Some premade scripts are in the "CustomScripts" folder. 

- Video encoding .bat files under construction

- Batch image processing .bat files are under construction. 



Known Issues:

- ProSR isn't being parsed by "select_neural_network.bat" correctly, fix coming soon. 

- Some neural networks bug out if the resolution is too low. Non RGB ones are particularly prone to this.

- The installer script isn't particularly fault tolerant. 

- Tons of features are missing *shrug* 



TODO:

- Finish tons of stuff for a initial installer release

- Link all the software in this readme.

- Get the installer to check for an existing CUDA installation. 

- Clean up the offensively hacky neural network parser.

- Possibly separate RGB and non-RGB filters, or label them.
 
- Investigate OpenCV scalers See https://github.com/WolframRhodium/muvsfunc/tree/master/Collections/examples
 
- Investigate the Intel MKL version of MxNet, or the hybrid CUDA/MKL versions. 
 
- Add more example scripts and encoding options
 
 
