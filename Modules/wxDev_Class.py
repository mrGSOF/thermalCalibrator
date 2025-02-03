import wx
from Modules import File_Class as F
from Modules import fileLib
from Modules import Date

def floatToStr( f ) -> str:
    return "%1.8f"%f

class wxDev():
    def __init__(self, GUIobj, Type, title="TBD", data=None, path="./", savePW=None):
        self.GUIobj = GUIobj
        self.Type = Type
        self.title = title
        self.data = data
        self.file = F.File(path)
        self.savePW = savePW
        self.pos = None

    def _readBackDev(self) -> None:
        """ Update the self.data device information with the latest GUI values """
        data = self.data
        data["MODEL"] = self.model.GetValue()
        data["MFR"] = self.mfr.GetValue()
        if "UID" in data:
            data["UID"] = self.uid.GetValue()
        else:
            data["SN"] = self.uid.GetValue()
        try:
            date = Date.toDict(self.date.GetValue())
        except ValueError:
            date = Date.date(month=1, day=1, year=2020)
        data["EXP_DATE"] = date
            

    def _readBackCoef(self) -> None:
        """ Update the self.data coefficients with the latest GUI values """
        Type = self.Type
        data = self.data["COEF"]
        if (Type == "ITS27") or (Type == "ITS67"):
            data["R0"] = float( self.coef[0].GetValue() )
            data["Alpha"] = float( self.coef[1].GetValue() )
            data["Delta"] = float( self.coef[2].GetValue() )
                                  
        elif (Type == "ITS90"):
            data["RTPW"] = float( self.coef[0].GetValue() )
            data["a4"] = float( self.coef[1].GetValue() )
            data["b4"] = float( self.coef[2].GetValue() )
            data["a7"] = float( self.coef[3].GetValue() )
            data["b7"] = float( self.coef[4].GetValue() )
            data["c7"] = float( self.coef[5].GetValue() )
            
        elif (Type == "IEEE") or (Type == "IEEE488") or (Type == "GPIB"):
            data["ADDR"] = self.coef[0].GetValue()
            
        elif (Type == "RS232"):
            data["COM"] = self.coef[0].GetValue()
            data["BAUD"] = int( self.coef[1].GetValue() )
            
        else:
            print("Wrong type of coef")

    def _updateDev(self) -> None:
        """ Update the device parameters after data was loaded and GUI was generated (show)"""
        data = self.data
        self.model.SetValue( str(data["MODEL"]) )
        self.mfr.SetValue( str(data["MFR"]) )
        if "UID" in data:
            self.uid.SetValue( str(data["UID"]) )
        else:
            self.uid.SetValue( str(data["SN"]) )

        if "EXP_DATE" in data:
            expDate = data["EXP_DATE"]
            self.date.SetValue( Date.toStr(expDate) )
            if Date.isPassed(expDate):
                self.date.SetForegroundColour(wx.WHITE)
                self.date.SetBackgroundColour(wx.RED)
            else:
                self.date.SetForegroundColour(wx.BLACK)
                self.date.SetBackgroundColour(wx.WHITE)
                
        else:
            self.date.SetValue( "   /   /   " )

    def _updateCoef(self) -> None:
        """ Update the device coefficients after data was loaded and GUI was generated (show)"""
        Type = self.Type
        data = self.data["COEF"]
        if (Type == "ITS27") or (Type == "ITS67"):
            self.coef[0].SetValue( floatToStr(data["R0"]) )
            self.coef[1].SetValue( floatToStr(data["Alpha"]) )
            self.coef[2].SetValue( floatToStr(data["Delta"]) )
                                  
        elif (Type == "ITS90"):
            self.coef[0].SetValue( floatToStr(data["RTPW"]) )
            self.coef[1].SetValue( floatToStr(data["a4"]) )
            self.coef[2].SetValue( floatToStr(data["b4"]) )
            self.coef[3].SetValue( floatToStr(data["a7"]) )
            self.coef[4].SetValue( floatToStr(data["b7"]) )
            self.coef[5].SetValue( floatToStr(data["c7"]) )
            
        elif (Type == "IEEE") or (Type == "IEEE488") or (Type == "GPIB"):
            self.coef[0].SetValue( str(data["ADDR"]) )
            
        elif (Type == "RS232"):
            self.coef[0].SetValue( str(data["COM"]) )
            self.coef[1].SetValue( str(data["BAUD"]) )
            
        else:
            print("Wrong type of coef")

    def _showDev(self, pos) -> None:
        """ Generate the device parameters GUI """
        GUIobj = self.GUIobj
        DY = 25
        wx.StaticText(GUIobj, -1, "MODEL", pos=(pos[0], pos[1] +3) )
        self.model = wx.TextCtrl( GUIobj, -1, "",
                                  pos=(pos[0] +45, pos[1]),
                                  size=(85,-1) )

        pos[1] += DY
        wx.StaticText(GUIobj, -1, "SN", pos=(pos[0], pos[1] +3) )
        self.uid = wx.TextCtrl( GUIobj, -1, "",
                                  pos=(pos[0] +45, pos[1]),
                                  size=(85,-1) )

        pos[1] += DY
        wx.StaticText(GUIobj, -1, "MFR", pos=(pos[0], pos[1] +3) )
        self.mfr = wx.TextCtrl( GUIobj, -1, "",
                                  pos=(pos[0] +45, pos[1]),
                                  size=(85,-1) )
        pos[1] += DY

        wx.StaticText(GUIobj, -1, "DATE", pos=(pos[0], pos[1] +3) )
        self.date = wx.TextCtrl( GUIobj, -1, "",
                                  pos=(pos[0] +45, pos[1]),
                                  size=(85,-1) )
        pos[1] += DY

    def _showCoef(self, pos, labels=None) -> None:
        """ Generate the device coefficients GUI """
        GUIobj = self.GUIobj
        Type = self.Type
        DY = 25
        wx.StaticText(GUIobj, -1, "%s Parameters:"%(Type), pos=(pos[0], pos[1] +3) )
        pos[1] += DY
        self.coef = []

        if labels == None:
            if (Type == "ITS27") or (Type == "ITS67"):
                labels = ("R0","Alpha","Delta")
            elif (Type == "ITS90"):
                labels = ("RTPW","a4","b4","a7","b7","c7")
            elif (Type == "IEEE") or (Type == "IEEE488") or (Type == "GPIB"):
                labels = ["ADDRESS"]
            elif (Type == "RS232"):
                labels = ("COM", "BAUD")

        for label in labels:
            wx.StaticText(GUIobj, -1, label, pos=(pos[0], pos[1] +3) )
            self.coef.append( wx.TextCtrl( GUIobj, -1, "",
                                      pos=(pos[0] +55, pos[1]),
                                      size=(75,-1) ) )
            pos[1] += DY

    def show(self, dataPos=(0,0), btnPos=(0,230)) -> None:
        """ Generate the device GUI and update the values """
        GUIobj = self.GUIobj
        self.dataPos = dataPos
        self.btnPos = btnPos
        
        wx.StaticBox(GUIobj, -1, self.title, pos=dataPos, size=(150, 12*25 +1*30) )
        dataPos = [dataPos[0] +10, dataPos[1] +20]
        if (dataPos != False):
            self._showDev(dataPos)
            self._showCoef(dataPos)

        if (btnPos != False):
            DX = 60
            pos = [btnPos[0], btnPos[1]]
            loadBtn = wx.Button(GUIobj, -1, "LOAD", pos=pos, size=(50,-1) )
            loadBtn.Bind(wx.EVT_BUTTON, self.onLoad)

            pos[0] += DX
            saveBtn = wx.Button(GUIobj, -1, "SAVE", pos=pos, size=(50,-1) )
            saveBtn.Bind(wx.EVT_BUTTON, self.onSaveAs)
        self.update()

    def update(self, filename=None, data=None) -> None:
        """ Update the GUI information with the model data """
        if filename:
            self.file.filename = filename
        if data:
            self.data = data

        if self.data:
            print("wxDev.update(): Data exists")
            self._updateDev()  #< Update the device information part
            self._updateCoef() #< Update the coefficiant part
        else:
            print("wxDev.update(): Data is empty")

    def readBack(self) -> None:
        """ Update the GUI information with data """
        self._readBackDev()
        self._readBackCoef()

    def onSaveAs(self, event) -> None:
        self.readBack()
        dlg = wx.FileDialog(self.GUIobj, "Choose a file", self.file.path, "", "*.json", wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            self.file.filename = dlg.GetFilename()
            self.file.path = dlg.GetDirectory()
            self.data = fileLib.saveJsonFile(self.data, path=self.file.path, name=self.file.filename, ext="")
        dlg.Destroy()

    def onLoad(self, event) -> None:
        """Choose file"""
        dlg = wx.FileDialog(self.GUIobj, "Choose a file", self.file.path, "", "*.*", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.file.filename = dlg.GetFilename()
            self.file.path = dlg.GetDirectory()
            self.load(path=self.file.path, filename=self.file.filename)
        dlg.Destroy()

    def load(self, path, filename) -> None:
        """Choose file"""
        self.data = fileLib.loadJsonFile(path=path, name=filename, ext="")
        self.update()
