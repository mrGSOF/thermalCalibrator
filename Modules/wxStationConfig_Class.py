import os, wx
from Modules import fileLib
from Modules import Station_Class as STN
class wxStationConfigDialog(wx.Dialog):
    def __init__(self, model):
        wx.Dialog.__init__(self, None, -1, "Station configuration",
            style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|
                wx.TAB_TRAVERSAL, size=(400,260))

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        dialog = wx.Window(self, -1, size=(400,260))
        self.dialog = dialog
        self.model = model.model
        self.wxModel = model
        
        DV = 25
        pos = [10,10]
        if self.model:
            cfg = self.model.config.contant
            desc = str(cfg["DESC"])
            soakTime = str(cfg["SOAK"])
            unitFile = str(cfg["UNIT"])
            dmmFile = str(cfg["UUT"]["DMM"])
            prtFile = str(cfg["UUT"]["PRT"])
            progFile = str(cfg["PROG"])
        else:
            desc = "No description"
            soakTime = "25.0"
            unitFile = self.wxModel.pathUnit
            dmmFile = self.wxModel.pathDmm
            prtFile = self.wxModel.pathPrt
            progFile = self.wxModel.pathProg

        wx.StaticText(dialog, -1, "Description", pos=(pos[0], pos[1] +4) )
        self.stnDesc = wx.TextCtrl(dialog, -1, pos=(pos[0] +60, pos[1] +0), size=(300,-1) )
        self.stnDesc.SetValue( desc )

        pos[1] += DV
        wx.StaticText(dialog, -1, 'STD SOAK', pos=(pos[0], pos[1] +4) )
        wx.StaticText(dialog, -1, '(Minutes)', pos=(pos[0] +100, pos[1] +4) )
        self.stdSoak = wx.TextCtrl(dialog, -1, pos=(pos[0] +60, pos[1] +0), size=(35,-1) )
        self.stdSoak.SetValue( soakTime )

        pos[1] += DV
        self.unitFile = self._devicePathLine("UNIT file", unitFile, pos, self.OnUnitBrowes)

        pos[1] += DV
        self.dmmFile = self._devicePathLine("DMM file", dmmFile, pos, self.OnDmmBrowes)

        pos[1] += DV
        self.prtFile = self._devicePathLine("PRT file", prtFile, pos, self.OnPrtBrowes)

        pos[1] += DV
        self.progFile = self._devicePathLine("PROG file", progFile, pos, self.OnProgBrowes)

        pos[1] += DV
        buttonSave = wx.Button(dialog, -1, "Save", pos=(pos[0], pos[1]) )
        self.Bind(wx.EVT_BUTTON,  self.OnSave, buttonSave)

        pos[1] += DV
        buttonOK = wx.Button(dialog, -1, "OK", pos=(pos[0], pos[1]) )
        self.Bind(wx.EVT_BUTTON,  self.OnOK, buttonOK)
        
        self.SetFocus()

    def _devicePathLine(self, title, path, pos, btnEvent):
        dialog = self.dialog
        wx.StaticText(dialog, -1, title, pos=(pos[0], pos[1] +4) )
        txtCtrl = wx.TextCtrl(dialog, -1, pos=(pos[0] +60, pos[1] +0), size=(250,-1) )
        txtCtrl.SetValue( path )
        browseBtn = wx.Button(dialog, -1, "Browse", pos=(pos[0] +310, pos[1]), size=(50,-1) )
        self.Bind(wx.EVT_BUTTON,  btnEvent, browseBtn)
        return txtCtrl

    def _browesDialog(self, textCtrl):
        path = textCtrl.GetValue()
        dlg = wx.FileDialog(self.dialog, "Choose a file", path, "", "*.json", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.GetFilename()
            path = dlg.GetDirectory()
            try:
                path = os.path.relpath( path, os.getcwd())
                path = os.path.join(".", path)
            except ValueError:
                pass
            fullName = os.path.join(path, name)
            textCtrl.SetValue(fullName)
        dlg.Destroy()

    def OnUnitBrowes(self, event):
        self._browesDialog( self.unitFile )

    def OnDmmBrowes(self, event):
        self._browesDialog( self.dmmFile )

    def OnPrtBrowes(self, event):
        self._browesDialog( self.prtFile )

    def OnProgBrowes(self, event):
        self._browesDialog( self.progFile )

    def OnClose(self, event):
        self.Destroy()

    def OnOK(self, event):
        cfg = self.Update()
        self.Destroy()

    def OnSave(self, event):
        cfg = self.update() #< Build a new Config object with GUI parameters
        dlg = wx.FileDialog(self.dialog, "Choose a file", self.wxModel.path, "", "*.json", wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            path = dlg.GetDirectory()
            cfg.save(path=path, filename=filename)            #< Save to file
            self.wxModel.load( path=path, filename=filename ) #< Update the model
        dlg.Destroy()

    def update(self):
        ### Read the values from the GUI
        desc = self.stnDesc.GetValue()
        soak = float( self.stdSoak.GetValue() )
        unitFile = self.unitFile.GetValue()
        dmmFile = self.dmmFile.GetValue()
        prtFile = self.prtFile.GetValue()
        progFile = self.progFile.GetValue()

        ### Build a new Config object
        cfg = STN.Config()
        cfg.updateStationCfg(desc, soak, unitFile, dmmFile, prtFile, progFile)
        return cfg
