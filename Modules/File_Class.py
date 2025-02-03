import os

class File_base():
    def __init__(self, path="./"):
        self.fd = None
        self.filename = ""
        self.error = None
        self.path = path
        self.comment = "No file selected"

    def openFile(self) -> bool:
        return False

    def CloseFile(self) -> bool:
        return True

    def getPathName(self) -> str:
        return "%s/%s"%(self.path, self.filename)
    
class File(File_base):
    def openFile(self) -> bool:
        try:
            self.fd = open(os.path.join(self.path, self.filename), 'w') #Open the file for read and write
            self.comment = "open %s"%(self.filename)
            error = False

        except: # IOError
            self.file = None
            self.comment = "Open Error %s"%(self.filename)
            error = True
            self.fd = None
        return not error

    def closeFile(self) -> bool:
        try:
            self.fd.close()
            self.comment = "Closed %s"%(self.filename)
            error = False
        except: # IOError:
            self.comment = "Close Error %s"%(self.filename)
            error = True
        self.fd = None
        return not error
