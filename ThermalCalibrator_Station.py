import sys, argparse
import wx, wx.adv
import pyvisa as visa
from typing import List
from Modules import Station_Class as STN
from Modules import wxStation_Class as wxSTN
from Icons import AppIcon
from Icons import KncIcon

class MyFrame(wx.Frame):
    """ """
    def __init__(self, parent, title, cfgFile):
        super().__init__( parent, -1, title,
                          pos=(150, 150), size=(512, 870))

        self.window = wx.Window(self, -1)
        ### Init UI
        self.fileMenu = wx.Menu() #< Creat a menu (also for later access) 
        self.fileMenu.AppendSeparator()
        self.fileMenu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Exit this simple sample")
        self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT) #< bind the menu event to an event handler
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        aboutMenu = wx.Menu() #< Creat a menu 
        aboutMenu.Append(wx.ID_ABOUT, "&About", "Information about this program")
        self.Bind(wx.EVT_MENU, self.OnAbout, id=wx.ID_ABOUT)

        menuBar = wx.MenuBar() #< Create the menubar
        menuBar.Append(self.fileMenu, "&File") #< Add the file menu to the menubar
        menuBar.Append(aboutMenu, "&Help")     #< Add the help menu to the menubar

        self.menuBar = menuBar
        self.SetMenuBar(menuBar)
        
        self.CreateStatusBar()
        
        #self.SetIcon( wx.Icon('./Icons/AppIcon.ico', wx.BITMAP_TYPE_ICO) )
        self.SetIcon( AppIcon.AppIcon.GetIcon() )

        rm = visa.ResourceManager()

        pathStation = "./config/stations/"
        pathUnit    = "./config/devices/unit/"
        pathDmm     = "./config/devices/dmm/"
        pathPrt     = "./config/devices/prt/"
        pathProg    = "./config/prog/"
        pathReport  = "./reports/"

        ### THE GUI WILL BUILD THE STATION BY COMMAND AND IF POSSIBLE
        wxs = wxSTN.wxStation(self, rm,
                              path=pathStation,
                              pathReport=pathReport,
                              pathProg=pathProg,
                              pathUnit=pathUnit,
                              pathDmm=pathDmm,
                              pathPrt=pathPrt)
        wxs.show( devPos=(5,5), ctrlPos=(5,370), logPos=(5,640) )
        if len(cfgFile) > 5:
            wxs.load(path="", filename=cfgFile)
        self.wxs = wxs
        sys.stdout = wxs.log
        sys.stderr = wxs.log
        
    def OnAbout(self, event):
        description = """TBD"""

        licence = """The Thermo-Calibrator application is a free software; you can redistribute 
it and/or modify it.
The Thermo-Calibrator application is distributed with hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.""" 

        info = wx.adv.AboutDialogInfo()

        info.SetIcon( KncIcon.KncIcon.getIcon() )
        #info.SetIcon( wx.Icon("./Icons/GSOF.jpg", wx.BITMAP_TYPE_ANY) )
        info.SetName("3605A, 3604A, and 3604U Automatic Calibrator")
        version = "0.9\nRunning on:\nPython %s\nwx %s"%( sys.version[0:5],wx.version() )
        info.SetVersion(version)
        info.SetDescription(description)
        info.SetCopyright("(C) 2005 - 2022 Guy Soffer (GSOF)")
        info.SetWebSite("mailto:gsoffer@yahoo.com")
        info.SetLicence(licence)
        info.AddDeveloper("Unit's firmware: Guy Soffer\nPC software: Guy Soffer")

        wx.adv.AboutBox(info)

    def OnExit(self, evt):
        """Event handler for the EXIT menu"""
        print("Exit!")
        self.Close() #< Will cause an event that calls self.OnClose()

    def OnClose(self, evt):
        """Event handler for closing the window [X]"""
        print("Close!")
        self.wxs.close()
        self.Destroy()

class MyApp(wx.App):
    def __init__(self, redirect, cfgFile=""):
        self.cfgFile = cfgFile
        super().__init__(redirect)
        
    def OnInit(self):
        frame = MyFrame(None, "Thermo-Calibrtor KNC", self.cfgFile)
        self.SetTopWindow(frame)
        frame.Show(True)
        return True

def main(argv: List[str] = None) -> None:
    parser = argparse.ArgumentParser(
        description="Thermal calibrator. By Guy Soffer",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-file",
        metavar="Configuration file",
        default="",
        help="Station configuration full path and filename.",
    )
    args = parser.parse_args(argv)
    cfgFile = args.file

    app = MyApp(redirect=False, cfgFile=cfgFile)
    app.MainLoop()

if __name__ == "__main__":  # pragma: nocover
    main()
