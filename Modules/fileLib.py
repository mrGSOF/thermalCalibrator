import json, os

def splitFilename(filename) -> list:
    return os.path.splitext(filename)

def suggestName(path, name, ext=".json") -> str:
    i = 1
    fileNames, nameList = listFiles(path, ext)
    newName = name
    while ( newName in nameList ):
        newName = "%s_%d"%(name,i)
        i += 1
    return newName

def listFiles(path = "./", extList=[".json"]) -> list:
##    files = os.listdir(path)
##    fileNames = []
##    for fn in files:
##        for ext in extList:
##            if ( fn.endswith(ext) ):
##                fileNames.append(fn)
    fileNames = [fn for fn in os.listdir(path)
                  if any(fn.endswith(ext) for ext in extList)]

    nameList = []
    for fileName in fileNames:
        name, ext = fileName.split('.')
        nameList.append(name)
    return fileNames, nameList

def testFolderStruct(root, folderList) -> bool:
    err = False
    for folder in folderList:
        path = root+folder
        if (isFileExists(path, ext="")):
            print(path +' - OK')
        else:
            os.makedirs(path)
            print(path +' - Created')
            err = True
    return err

def isFileExists(path = "", name="" ,ext=".json") -> bool:
    path = os.path.join(path,name+ext)
    return os.path.exists(path)

def loadJsonFile(path="", name="", ext=".json") -> dict:
    filename = os.path.join(path,name+ext)
    fd = open(filename)
    try:
        dat=json.load(fd)
    except ValueError:
        print("Error loading JSON file <%s>"%(filename))
        dat=None
    fd.close()
    return dat

def decodeJsonString(s)-> dict:
    dat = json.loads(s)
    return dat

def deleteFile(path = "", name="", ext=".json") -> None:
    filename = os.path.join(path,name+ext)
    if isFileExists(path,name,ext):
        print("<%s> found and deleted"%(filename))
        os.remove(filename)
    else:
        print("<%s> could not be found and deleted"%(filename))

def saveJsonFile(dat, path = "", name = "", ext=".json") -> None:
    filename = os.path.join(path,name+ext)
    print("File saved: %s"%(filename))
    fd = open(filename,'w')
    try:
        dat=json.dump(dat, fd)
    except ValueError:
        print("Error saving JSON file <%s>"%(filename))
        dat=None
    fd.close()
