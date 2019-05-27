import glob
import functools
import os
import shutil
import sys
from PIL import Image
from itertools import groupby
from importlib.machinery import SourceFileLoader
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from ImageFetcher import remove_prefix
Script = SourceFileLoader('Script', os.path.dirname(os.path.realpath(__file__)) + '\\..\\ProcessImagesAuto.vpy').load_module()


def GetImageList(ifolder, iformat, hRes = 0, vRes = 0):
	#Generate a list of image paths inside a folder and its subfolders, filtered by size and format
	#If the resolution is 0 or unspecified, the image size filter will be skipped. 
    rawlist = glob.glob(ifolder + "/**/*." + iformat, recursive=True)
    filelist=[]
    if hRes == 0 and vRes == 0:
        sizelist = []                   #Size matters
        for imagedir in rawlist:        #Get a list of image sizes
            im = Image.open(imagedir)
            width, height = im.size
            im.close()
            sizelist.append([width,height])
        reslist =  [k for k,v in groupby(sorted(sizelist))]         #sort and remove duplicates
        for res in reslist:             #Turn the image directories into clips grouped by resolution
            n = 0
            for size in sizelist:
                if size == res:
                    filelist.append(rawlist[n])
                n = n+1
    else:
        for imagedir in rawlist:
            im = Image.open(imagedir)
            width, height = im.size
            im.close()
            if (width == hRes) and (height == vRes):
                filelist.append(imagedir)
    return filelist

filelist = GetImageList(Script.ImageFolder, Script.ImageFormat, Script.Horizontal_Resolution, Script.Vertical_Resolution)
if len(filelist) > 0:
    for x in range(0, len(filelist)):
        if os.path.isfile(Script.ImageFolder + r"/../VapourSynth_Image_Buffer/image" + str(x) + "." + Script.OutputFormat):
            shutil.move(Script.ImageFolder + r"/../VapourSynth_Image_Buffer/image" + str(x) + "." + Script.OutputFormat, Script.ImageFolder + r"/../Processed_Images/" + remove_prefix(filelist[x], Script.ImageFolder)[:-len(Script.ImageFormat)] + Script.OutputFormat)
        else:
            print("Error, file not found!")

