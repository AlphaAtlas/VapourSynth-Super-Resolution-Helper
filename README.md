A set of scripts that automate the process of installing Vapoursynth, MXNet, various python modules and pre-trained image upscalers in a portable folder, as well as CUDA and/or cuDNN if you don't have them. Just download the latest release, and run it!

ONLY supports Windows.

It's basically a installer for ChaosKing's portable vapoursynth fatpack and WolframRhodium's super resolution stuff.
https://github.com/theChaosCoder/vapoursynth-portable-FATPACK/
https://github.com/WolframRhodium/Super-Resolution-Zoo

But it also includes an image processing script. Unlike the standard IMWRI plugin, it can search a directory for images, run them through vapoursynth functions just like a regular video, and then write the processed images to a seperate directory with a mirrored file structure. It also supports processing alpha layers seperately, as well as directories with multiple sizes/types of images, which tends to break regular vapoursynth scripts. Open "ProcessImagesAuto.vpy" in VSEdit to try this out. 

Scripts under construction. Some of the project works now, but the Nvidia installer and CUDA stuff is untested, and it's still missing documentation on a wiki, batch scripts for encoding, and... a decent readme, among other things. If you don't know anything about VapourSynth, don't download this yet!

![WzLvUe.gif](https://i.lensdump.com/i/WzLvUe.gif)
![WzLMZk.gif](https://i.lensdump.com/i/WzLMZk.gif)



