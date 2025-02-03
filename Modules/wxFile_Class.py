import os
from Modules import File_Class as F

try:
    import wx
except ImportError:
    print('No wxPython support')

if wx:
    class wxFile(F.File_base):
        def __init__(self, Model=False):
            self.Model = Model

        def Show(self, GUIobj, BtnPos=False, PathPos=False, StsPos=False):
            self.GUIobj = GUIobj
            DY = 20
            if (BtnPos != False):
                pos = [BtnPos[0], BtnPos[1]]
                self.DispBox = wx.CheckBox(self.GUIobj.window, -1 ,self.BtnName+' Disp', pos=pos )
                self.DispBox.Bind(wx.EVT_CHECKBOX, self.OnCheck)
                #self.DispBox.SetValue(self.Viewer.RealTimePrint)

                pos[1] += DY
                LogBtn = wx.Button(self.GUIobj.window, -1, self.BtnName, pos=pos )
                LogBtn.Bind(wx.EVT_BUTTON, self.OnClick)

            if (StsPos != False):
                pos = [StsPos[0], StsPos[1]]
                self.StsBox = wx.TextCtrl(self.GUIobj.window, -1 ,self.Model.TextComment, pos=(pos[0]+10, pos[1]), size=(90,-1), style=wx.TE_READONLY )

            if (PathPos != False):
                pos = [PathPos[0], PathPos[1]]
                self.PathBox = wx.TextCtrl(self.GUIobj.window, -1
                                           ,os.path.join(self.Model.Path, self.Model.FileName),
                                           pos=pos, size=(120,-1),
                                           style = wx.TE_PROCESS_ENTER)
                self.PathBox.Bind(wx.EVT_TEXT_ENTER, self.OnPathChange)

        def OnLoad(self, event):

        def OnSave(self, event):
            self.OpenCloseFileToggle()

        def OnPathChange(self, event):
            path = self.PathBox.GetValue()
            if (path == ''):
                self.ChooseFile()
            else:
                self.Model.FileName = os.path.basename( path )
                self.Model.Path = os.path.dirname( path )
                self.PathBox.SetValue( os.path.join(self.Model.Path, self.Model.FileName) )

        def OnCheck(self, event):
            return

        def ChooseFile(self, Path='./', Name='*.*'):
            """Choose file"""
            dlg = wx.FileDialog(self.GUIobj, "Choose a file", Path, "", Name, wx.FD_SAVE)
            if dlg.ShowModal() == wx.ID_OK:
                self.Model.FileName = dlg.GetFilename()
                self.Model.Path = dlg.GetDirectory()
                self.Model.OpenFile()
                self.Model.CloseFile()
            dlg.Destroy()
            self.PathBox.SetValue( os.path.join(self.Model.Path, self.Model.FileName) )

        def OpenCloseFileToggle(self):
            if (self.Model.OpenCloseFileToggle() == False):
                dlg = wx.MessageDialog( self.GUIobj, "Select a File and try again...", "Can't find the file", wx.OK)
                dlg.ShowModal() # Show it
                dlg.Destroy() # finally destroy it when finished.
                self.ChooseFile()
            self.StsBox.SetValue( self.Model.TextComment )

        def OpenFile(self):
            if (self.Model.OpenFile() == False):
                dlg = wx.MessageDialog( self.GUIobj, "Can't find the file. Select a new one...", "File open", wx.OK)
                dlg.ShowModal() # Show it
                dlg.Destroy() # finally destroy it when finished.
                self.ChooseFile()
            self.StsBox.SetValue( self.Model.TextComment )

        def CloseFile(self):
            if (self.Model.CloseFile() == False):
                dlg = wx.MessageDialog( self.GUIobj, "File wasn't found...", "Can't close the file", wx.OK)
                dlg.ShowModal() # Show it
                dlg.Destroy() # finally destroy it when finished.
            self.StsBox.SetValue( self.Model.TextComment )
