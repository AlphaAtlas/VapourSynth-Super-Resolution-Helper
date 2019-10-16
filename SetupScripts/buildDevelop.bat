@REM Makes FatDownloader portable! Downloads from develop branch
python.exe -m pip install pySmartDL pyinstaller --upgrade
pyinstaller FatDownloader_develop.py -F
RD /S /Q __pycache__
RD /S /Q build
DEL /Q FatDownloader_develop.spec