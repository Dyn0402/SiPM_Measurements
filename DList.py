import os
from Tkinter import Tk
from tkFileDialog import askdirectory
from tkFileDialog import askopenfilename
from tkMessageBox import *
from Tkinter import *
import shutil
import winsound
import random
import time

#Prompts user to browse and select a directory.
#All .rpt files in selected directories are compiled to a list.
#That list is then returned.
def ListRptsInDirectory(Directory):
    DirectoryContents = os.listdir(Directory)
    GoodDirectoryContents = []

    for name in DirectoryContents:
        if(name.find(".rpt")!=-1):
            GoodDirectoryContents.append(name)
    return GoodDirectoryContents

def ListFilesInDirectory(Directory):
    DirectoryContents = os.listdir(Directory)
    
    return DirectoryContents

#Same as ListRpts, but manually enter file type without the ".".
def ListFileTypeInDirectory(Directory, FileType):
    DirectoryContents = os.listdir(Directory)
    GoodDirectoryContents = []

    for name in DirectoryContents:
        if(name.find("." + str(FileType))!=-1):
            GoodDirectoryContents.append(Directory + "/" + name)
    return GoodDirectoryContents    


def ListFileTypeInSubDirs(MainDir, FileType = 'txt'):
    FileList = ListFileTypeInDirectory(MainDir, FileType)
    DirList = ListDirsInDirectory(MainDir)
    for Dir in DirList:
        FileList.extend(ListFileTypeInSubDirs(Dir, FileType = FileType))
    
    return(FileList)


def ListTxtsInDirectory(Directory):
    DirectoryContents = os.listdir(Directory)
    GoodDirectoryContents = []

    for name in DirectoryContents:
        if(name.find(".txt")!=-1):
            GoodDirectoryContents.append(name)
    return GoodDirectoryContents

def ListDirsInDirectory(Directory, DirName = False):
    DirectoryContents = os.listdir(Directory)
    GoodDirectoryContents = []
    GoodDirectoryNames = []

    for name in DirectoryContents:
        if(os.path.isdir(Directory + "/" + name)):
            GoodDirectoryContents.append(Directory + "/" + name)
            GoodDirectoryNames.append(name)
            
    if(DirName):
        return(GoodDirectoryContents, GoodDirectoryNames)
    else:
        return(GoodDirectoryContents)

def GetFileType(File):
    Index = File.find(".")
    Extension = File[Index + 1:]
    return Extension

def ChooseDirectory():
    Tk().withdraw()
    Directory = askdirectory()
    return Directory

def ChangeDirectory(Path = "Choose"):
    if(Path == "Choose"):
        Tk().withdraw()
        Directory = askdirectory()
    else:
        Directory = Path
    os.chdir(Directory)

def ChooseFile():
    Tk().withdraw()
    FileName = askopenfilename()
    return FileName
    
def CopyFile(File, NewDirectory, NewName):
    shutil.copyfile(File, NewDirectory + "/" + NewName)
    
def CheckForFile(Path):
    return(os.path.exists(Path))
    
def CopyDirectory(Directory, NewDirectory, NewDirectoryName):
    shutil.copytree(Directory, NewDirectory + "/" + NewDirectoryName)
    
def CreateFolder(FolderName, ParentDirPath):
    newpath = ParentDirPath + "/" + FolderName
    while(os.path.exists(newpath)): 
        print("Path {0} exists! Cannot create new path.").format(newpath)
        newpath=raw_input("Please Type new path:")   
    os.mkdir(newpath)
    return(newpath)

def GetFolder(FolderName, ParentDirPath):
    newpath = ParentDirPath + "/" + FolderName
    if(not(os.path.exists(newpath))):
        os.mkdir(newpath)
    return(newpath)
    
def TruncatePath(FolderPath):
    FolderPath = FolderPath.split("/")
    FolderName = FolderPath[-1]
    
    return(FolderName)
    
def StatusBox(*StatusList):
    StatusBox = Tk()
    StatusBox.title("Status")
    StatusString = ""
    StatusBarLen = 20
    BarTickChar = "x"
    BarNoTickChar = " "
    BarSideChar = "|"
    for Status in StatusList:
        PercentDone = float(Status[0]) / Status[1]
        if(PercentDone >= 0 and PercentDone <= 1):
            Ticks = int(StatusBarLen * PercentDone)
        else:
            Ticks = StatusBarLen
            BarTickChar = "?"
            BarNoTickChar = "?"
        StatusString += str(Status[0]) + "/" + str(Status[1]) + "     " + BarSideChar + \
                        BarTickChar * Ticks + BarNoTickChar * (StatusBarLen - Ticks) + \
                        BarSideChar + "     " + str(int(PercentDone * 100 + 0.5)) + "%\n"
    #showinfo("Status", StatusString)
    Status = Canvas(StatusBox, height=200, width=400)

    Status.create_text(200,100,text=StatusString)

    Status.pack()    
    
    StatusBox.mainloop()
    
def donzo():
    audio = ["cantina", "peanuts", "pirate"]
    Path = ""
    if(os.path.exists("F:/Research")):
        Path = "F:/Research/Programs/Audio Files/"
    elif(os.path.exists("G:/Research")):
        Path = "G:/Research/Programs/Audio Files/"
    elif(os.path.exists("I:/Research")):
        Path = "I:/Research/Programs/Audio Files/"
    elif(os.path.exists("//cosfs.science.purdue.edu/UserData/neff6/Desktop/Programs")):
        Path = "//cosfs.science.purdue.edu/UserData/neff6/Desktop/Programs/Audio Files/"
    sound = Path + random.choice(audio) #change path to location of audio files
    winsound.PlaySound(sound, winsound.SND_FILENAME)
#    time.clock()
#    KillSound = False
#    while(not(KillSound)):
#        KillSound = raw_input()
#        if(KillSound )
    print("donzo")
    
    
