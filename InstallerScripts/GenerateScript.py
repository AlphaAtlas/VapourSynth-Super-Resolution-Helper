import glob, os, sys, math, time, pyperclip, fileinput, re

def clear():  
    if os.name == 'nt': 
        os.system('cls') 
    else: 
        os.system('clear') 

def list_columns(obj, cols=4, columnwise=True, gap=4):
    """
    Print the given list in evenly-spaced columns.

    Parameters
    ----------
    obj : list
        The list to be printed.
    cols : int
        The number of columns in which the list should be printed.
    columnwise : bool, default=True
        If True, the items in the list will be printed column-wise.
        If False the items in the list will be printed row-wise.
    gap : int
        The number of spaces that should separate the longest column
        item/s from the next column. This is the effective spacing
        between columns based on the maximum len() of the list items.
    """

    sobj = [str(item) for item in obj]
    if cols > len(sobj): cols = len(sobj)
    max_len = max([len(item) for item in sobj])
    if columnwise: cols = int(math.ceil(float(len(sobj)) / float(cols)))
    plist = [sobj[i: i+cols] for i in range(0, len(sobj), cols)]
    if columnwise:
        if not len(plist[-1]) == cols:
            plist[-1].extend(['']*(len(sobj) - len(plist[-1])))
        plist = zip(*plist)
    printer = '\n'.join([
        ''.join([c.ljust(max_len + gap) for c in p])
        for p in plist])
    print(printer)


#WIP. Rhis was written when I didn't know much python or any regex...
os.chdir(os.path.join(os.path.dirname(sys.executable()) , ".."))
print("This will update all .vpy files in the CustomScripts folder that end in 'Auto'.")
print("Super resolution arguments will also be copied to your clipboard.\n")
level1 = os.listdir("NeuralNetworks") 
i = 0
for d in os.listdir("NeuralNetworks"):
    if not os.path.isdir(os.path.join("NeuralNetworks", d)):
        del level1[i]
    elif d == ".git":
        del level1[i]
    else:
      i = i + 1

algorithm = ""
while True:
    clear()
    list_columns(level1)
    algorithm = input("Please Select an Algorithm: ")
    if(algorithm == ""):
        print("Exiting...")
        time.sleep(1)
        sys.exit()
    if(os.path.isdir(os.path.join("NeuralNetworks", algorithm))):
        break
s = """NeuralNetworks/""" + algorithm + """/**/info.md"""
os.system(r'echo Downloading Neural Networks. This could take awhile...')
os.system(r'call "bin/PortableSub/bin/svn.exe" update --set-depth infinity  NeuralNetworks/' + algorithm)
filelist = glob.glob(s, recursive=True)


argarray = []
choice = 0
clear()
for files in filelist:
    text_file = open(files, "r")
    lines = text_file.readlines()
    i = 0
    beginning = 0
    end = len(lines)
    try:
        beginning = lines.index("""```python\n""") + 1
    except ValueError:
        print("Error: Beginning Not Found!")
        print(str(files))
        sys.exit()
    try:
        end = lines.index("""```\n""")
    except ValueError:
        try:
            end = lines.index("""```""")
        except ValueError:
            try:
                end = lines.index("""'''\n""")
            except ValueError:
                print("Error: End Not Found!")
                print(str(files))
                sys.exit()
    del lines[:beginning]
    del lines[(end - beginning):]
    i = 0
    temp = lines
    for s in temp:
        if ((s == "") or (s.startswith("##"))):
            del lines[i]
        else:
            lines[i] = s.strip('\n')
            lines[i] = s.strip('\t')
            i = i + 1

    short = files.strip("NeuralNetworks/" + algorithm)
    short = short.strip("info.md")
    print("\t" + short)
    i = 0
    for s in lines:
        if s.startswith("#"):
            s = s.strip("\n")
            s = s.strip("#")
            s = s.strip(" ")           
            print(str(choice) + ": " + s)
            argument = lines[i + 1]
            a = argument.split("dict(")
            argument = "sr_args = dict(model_filename=r'../" + files.strip("info.md") + re.sub(r" ?\([^)]+\)", "", s) + "', device_id=0," + a[1].strip("\n")
            argarray.append(argument)
            choice = choice + 1
        i = i + 1
    print(" ")
    
while True:
    model = input("Please Select an Model Number: ")
    if (int(model) >= 0) and (int(model) <= choice) and model.isdigit():
        s = argarray[int(model)]
        pyperclip.copy(s)
        filelist = glob.glob('CustomScripts/*Auto.vpy')
        for files in filelist:
            for line in fileinput.input(files, inplace=True):
                if line.startswith("sr_args"):
                    print(s)
                else:
                    print(line.strip("\n"))
            fileinput.close()
        print(" " , "VapourSynth arguments copied to clipboard, and inserted into the example scripts!")
        time.sleep(1)
        break
    else:
        print("Exiting...")
        time.sleep(2)
        sys.exit()


        
    
            

 