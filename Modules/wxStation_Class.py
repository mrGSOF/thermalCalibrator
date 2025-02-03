import os, logging
import wx
#import wx.richtext as rt
from Modules import Station_Class as STN
from Modules import wxStationConfig_Class as wxSTNCFG
from Modules import Dev_Class as DEV
from Modules import wxDev_Class
from Modules import TEMP_conv as T
from Modules import fileLib
from Modules import wxJsonViewer_tiny as wxJV
from Modules import wxReportViewer as wxRV
from Modules import wxProgViewer as wxPV
from Modules import wxManualViewer as wxMV

class CustomConsoleHandler(logging.StreamHandler):
    """"""
    def __init__(self, textctrl):
        """  """
        logging.StreamHandler.__init__(self)
        self.textctrl = textctrl
        
    def emit(self, record):
        """  """
        msg = self.format(record)
        self.textctrl.WriteText( "--LOG: %s\n"%(msg) )
        self.flush()

class wxStation():
    def __init__(self, GUIobj, rm,
                 title="TBD",
                 path="./", pathReport="./", pathProg="./",
                 pathUnit="./", pathDmm="./", pathPrt="./",
                 savePW=None):
        self.GUIobj = GUIobj
        self.title = title
        self.path = path
        self.pathReport = pathReport
        self.pathProg = pathProg
        self.pathUnit = pathUnit
        self.pathDmm = pathDmm
        self.pathPrt = pathPrt
        self.pathProg = pathProg
        
        self.rm = rm
        self.model = None
        self.connected = False
        self.units = 'C'

    def show(self, devPos=(5,5), ctrlPos=(0,350), logPos=(0,700)) -> None:
        """ Generate the device GUI and update the values """
        GUI = self.GUIobj.window
        menu = self.GUIobj.fileMenu
        self.devPos = devPos
        self.ctrlPos = ctrlPos
        self.logPos = logPos
        load = menu.Insert(0, wx.ID_ANY, "L&oad program\tAlt-P", "Load ramp-and-soak program")
        self.GUIobj.Bind(wx.EVT_MENU, self.onLoadProg, load)
        load = menu.Insert(0, wx.ID_ANY, "L&oad station\tAlt-L", "Load station configuration")
        self.GUIobj.Bind(wx.EVT_MENU, self.onLoad, load)
        save = menu.Insert(1, wx.ID_ANY, "S&ave station\tAlt-S", "Save station configuration")
        self.GUIobj.Bind(wx.EVT_MENU, self.onSaveAs, save)

        debugMenu = wx.Menu()  #< Create a menu 
        manual = debugMenu.Insert(0, wx.ID_ANY, "Manual control", "Open the manual control dialog box")
        self.GUIobj.Bind(wx.EVT_MENU, self.onManualDialog, manual)

        cfg = debugMenu.Insert(0, wx.ID_ANY, "Station configuration", "View / edit the station's configuration file and soak time")
        self.GUIobj.Bind(wx.EVT_MENU, self.onConfig, cfg)

        scan = debugMenu.Insert(0, wx.ID_ANY, "Scan for devices", "Scan for devices on the IEEE488 bus")
        self.GUIobj.Bind(wx.EVT_MENU, self.onScanGPIB, scan)

        self.GUIobj.menuBar.Insert(1, debugMenu, "&Config")  #< Add the help menu to the menubar
        
        self.fontLabel = wx.Font(12, family = wx.FONTFAMILY_MODERN, style = wx.FONTSTYLE_NORMAL, weight = wx.FONTWEIGHT_NORMAL, 
                      underline = False, faceName ="", encoding = wx.FONTENCODING_DEFAULT)

        self.fontTele = wx.Font(18, family = wx.FONTFAMILY_MODERN, style = wx.FONTSTYLE_NORMAL, weight = wx.FONTWEIGHT_BOLD, 
                      underline = False, faceName ="", encoding = wx.FONTENCODING_DEFAULT)

        if (devPos != False):
            DX = 155
            wx.StaticBox(GUI, -1, "Station Configuration", pos=devPos, size=(480, 12*25 +1*30 +30) )
            posX, posY = [devPos[0] +10, devPos[1] +20]
            Type = "UNIT"
            unit = wxDev_Class.wxDev(GUI, data=DEV.Dev(Type), Type="GPIB", title=Type, path=self.pathUnit)
            unit.show( dataPos=(posX,posY), btnPos=(posX+10,posY+300) )
            self.unit = unit

            posX += DX
            Type = "DMM"
            dmm = wxDev_Class.wxDev(GUI, data=DEV.Dev(Type), Type="GPIB", title=Type, path=self.pathDmm)
            dmm.show( dataPos=(posX,posY), btnPos=(posX+10,posY+300) )
            self.dmm = dmm

            posX += DX
            Type = "PRT"
            prt = wxDev_Class.wxDev(GUI, data=DEV.Dev(Type), Type="ITS90", title=Type, path=self.pathPrt)
            prt.show( dataPos=(posX,posY), btnPos=(posX+10,posY+300) )
            self.prt = prt

        if (ctrlPos != False):
            wx.StaticBox(GUI, -1, "Status and control", pos=ctrlPos, size=(480, 265) )
            posX, posY = [ctrlPos[0] +10 +110, ctrlPos[1] +20]

            DY = 45
            #wx.StaticText(GUI, -1, "STATE", pos=(posX, posY +3) )
            self.state = wx.TextCtrl( GUI, -1, "OFF",
                                      pos=(posX, posY),
                                      size=(240,35) )
            self.state.SetFont(self.fontTele)

            posY += DY
            wx.StaticText(GUI, -1, "TARGET", pos=(posX, posY +3) )
            self.Tctrl = wx.TextCtrl( GUI, -1, "XXXX.XX",
                                      pos=(posX +60, posY),
                                      size=(110,35) )
            self.Tctrl.SetFont(self.fontTele)
            self.Tctrl.SetBackgroundColour( [0,160,160])

            posY += DY
            wx.StaticText(GUI, -1, "UNIT", pos=(posX, posY +3) )
            self.Tunit = wx.TextCtrl( GUI, -1, "XXXX.XX",
                                      pos=(posX +60, posY),
                                      size=(110,35) )
            self.Tunit.SetFont(self.fontTele)

            posY += int(DY/2) +7
            wx.StaticText(GUI, -1, "+/-DEV", pos=(posX +185, posY -20) )
            self.Tdev = wx.TextCtrl( GUI, -1, "XX.XX",
                                      pos=(posX +180, posY),
                                      size=(50,20) )

            posY += int(DY/2) -7
            wx.StaticText(GUI, -1, "SPRT/UUT", pos=(posX, posY +3) )
            self.Tuut = wx.TextCtrl( GUI, -1, "XXXX.XX",
                                      pos=(posX +60, posY),
                                      size=(110,35) )
            self.Tuut.SetFont(self.fontTele)

            posX, posY = [ctrlPos[0] +10, ctrlPos[1] +20]
            conBtn = wx.Button(GUI, -1, "Connect", pos=(posX, posY), size=(85,30) )
            conBtn.Bind(wx.EVT_BUTTON, self.onConnect)
            conBtn.Disable()
            self.connectBtn = conBtn

            DY = 35
            posY += DY
            btnSize = (90,30)
            monBtn = wx.Button(GUI, -1, "MONITOR", pos=(posX, posY), size=btnSize )

            posY += DY
            stdBtn = wx.Button(GUI, -1, "STANDARD", pos=(posX, posY), size=btnSize )
            stdBtn.Bind(wx.EVT_BUTTON, self.onStandard)

            posY += DY
            calBtn = wx.Button(GUI, -1, "CALIBRATION", pos=(posX, posY), size=btnSize )
            calBtn.Bind(wx.EVT_BUTTON, self.onCalibration)

            posY += DY
            stdCalBtn = wx.Button(GUI, -1, "AUTO STD-CAL", pos=(posX, posY), size=btnSize )
            stdCalBtn.Bind(wx.EVT_BUTTON, self.onAutoStdCal)

            posY += DY
            rampBtn = wx.Button(GUI, -1, "RAMP n SOAK", pos=(posX, posY), size=btnSize )
            rampBtn.Bind(wx.EVT_BUTTON, self.onRampAndSoak)

            posY += DY
            abortBtn = wx.Button(GUI, -1, "ABORT", pos=(posX, posY), size=btnSize )
            abortBtn.SetBackgroundColour( [220,0,0])
            abortBtn.Bind(wx.EVT_BUTTON, self.onAbort)
            abortBtn.SetForegroundColour( [200,200,200] )

            #posY += DY
            posY += 5
            posX += 100
            beepBtn = wx.Button(GUI, -1, "BEEP", pos=(posX, posY), size=(35,-1) )
            beepBtn.Bind(wx.EVT_BUTTON, self.onBeep)

            self.prn = wx.CheckBox(GUI, label="Print", pos=(posX +45, posY +5))
            self.prn.SetValue(True)
            self.prn.Bind(wx.EVT_CHECKBOX, self.onPrinter)

            posX, posY = [ctrlPos[0] +10 +380, ctrlPos[1] +20 +0]
            DY = 60

            lblList = ("F", "C") 
            self.rbox = wx.RadioBox(GUI, label = "Units",
                                    pos = (posX +10, posY),
                                    choices = lblList,
                                    majorDimension = 1,
                                    style = wx.RA_SPECIFY_ROWS) 
            self.rbox.Bind(wx.EVT_RADIOBOX,self.onUnits)
            self.onUnits(None)

            posY += DY
            skipBtn = wx.Button(GUI, -1, "SKIP", pos=(posX, posY), size=(85,40) )
            skipBtn.Bind(wx.EVT_BUTTON, self.onSkip)

            DY = 45
            posY += DY
            reportBtn = wx.Button(GUI, -1, "REPORT", pos=(posX, posY), size=(85,40) )
            reportBtn.Bind(wx.EVT_BUTTON, self.onReport)

            posY += DY
            reportBtn = wx.Button(GUI, -1, "PROGRAM", pos=(posX, posY), size=(85,40) )
            reportBtn.Bind(wx.EVT_BUTTON, self.onProgram)

            self.monBtn = monBtn
            self.abortBtn = abortBtn
            
            self.ctrlBtnList = (monBtn,
                                stdBtn,
                                calBtn,
                                stdCalBtn,
                                rampBtn,
                                beepBtn,
                                abortBtn,
                                skipBtn)
            self._disableAllCtrlBtn()

        if (logPos != False):
            wx.StaticBox(GUI, -1, "Messages", pos=logPos, size=(480, 150) )
            pos = [logPos[0] +10, logPos[1] +20]
            style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL|wx.TE_RICH
            self.log = wx.TextCtrl(GUI, wx.ID_ANY, pos=pos, size=(460,120), style=style)

            #style = rt.RE_MULTILINE|rt.RE_READONLY
            #self.log = rt.RichTextCtrl(GUI, wx.ID_ANY, pos=pos, size=(460,120), style=style)

            logger = logging.getLogger()        
            handler = CustomConsoleHandler(self.log)
            logger.addHandler(handler)

            self.updateDetails()

    def onManualDialog(self, event):
        """  """
        unit = None
        if self.model:
            unit = self.model.unit
        dlg = wxMV.wxManualViewer(title="Manual control",
                                  unit=unit,
                                  units=self.units)
        dlg.Show()
        
    def _disableAllCtrlBtn(self) -> None:
        for btn in self.ctrlBtnList:
            btn.Disable()

    def _disableModeBtn(self) -> None:
        n = 5
        for btn in self.ctrlBtnList[0:n]:
            btn.Disable()
        
    def _enableAllCtrlBtn(self) -> None:
        for btn in self.ctrlBtnList:
            btn.Enable()

    def _enableRampAndSoakBtn(self) -> None:
        for btn in [self.ctrlBtnList[0], self.ctrlBtnList[4], self.ctrlBtnList[5]]:
            btn.Enable()

    def _enableModeBtn(self) -> None:
        n = 5
        for btn in self.ctrlBtnList[0:n]:
            btn.Enable()
            btn.SetBackgroundColour((225, 225, 225))
            btn.SetForegroundColour( [0,0,0] )

    def close(self) -> None:
        if self.model:
            self.model.close()

    def updateDetails(self) -> None:
        """ Update the GUI information with data """
        print("Station configuration update")
        mdl = self.model
        if mdl:
            if mdl.unit:
                self.unit.update(filename = mdl.config.contant["UNIT"],
                                 data = mdl.unit.details) #< Update the unit wxGUI object

            if mdl.dmm:
                self.dmm.update(filename = mdl.config.contant["UUT"]["DMM"],
                                data = mdl.dmm.details)   #< Update the DMM wxGUI object

            if mdl.prt:
                self.prt.update(filename=mdl.config.contant["UUT"]["PRT"],
                                data = mdl.prt.details)   #< Update the PRT wxGUI object

    def readBack(self) -> None:
        """ Update the GUI information with data """
        return

    def toUnits(self, C):
        """ Converts degC to user units (F or C) """
        return T.C_to_units(C, self.units)
        
    def updateRealTimeDisplay(self,
                              Tctrl=None,
                              Tunit=None,
                              Rwell=None,
                              Tuut=None,
                              soak=None,
                              state=None) -> None:
        if Tctrl != None:
            if Tctrl == -999.0:
                Tctrl = None
                self.Tctrl.SetValue( "xxxx.xx" )
            else:
                self.Tctrl.SetValue( "%1.2f"%(self.toUnits(Tctrl)) )
        
        if Tunit != None:
            if Tunit == -999.0:
                Tunit = None
                self.Tunit.SetValue( "xxxx.xx" )
            else:
                self.Tunit.SetValue( "%1.2f"%(self.toUnits(Tunit)) )

        if Tuut != None:
            self.Tuut.SetValue( "%1.2f"%(self.toUnits(Tuut)) )

        if (Tuut != None) and (Tunit != None):
            self.Tdev.SetValue( "%+1.2f"%(self.toUnits(Tunit)-self.toUnits(Tuut)) )

        if soak == None:
            soak = -1
        if soak > -1:
            soak = int(soak)
            Sec = soak%60
            Min = int((soak -Sec)/60)
            self.state.SetValue( "SOAK: %d:%02d"%(Min,Sec) )
        elif state:
            self.state.SetValue( state )

    def onUnits(self, event) -> None:
        self.units = self.rbox.GetStringSelection()
        #self.model.setUnits(self.units)

    def onChgToC(self, event) -> None:
        self.units = 'C'
        
    def onChgToF(self, event) -> None:
        self.units = 'F'
        
    def onBeep(self, event) -> None:
        self.model.unit.beep()

    def onPrinter(self, event) -> None:
        if self.model:
            enPrinter = bool(self.prn.GetValue())
            self.model.std.printer = enPrinter
            self.model.rs.printer = enPrinter
        
    def onSkip(self, event) -> None:
        self.model.rs.skip()
        self.model.std.skip()

    def onReport(self, event) -> None:
        report = [None]
        if self.model:
            report=self.model.report.getReport(),
            
        dlg = wxRV.wxReportViewer(title="Report viewer",
                                  data=report[0],
                                  path=self.pathReport,
                                  units=self.units)
        dlg.Show()
        
    def onProgram(self, event) -> None:
        program = {}
        if self.model:
            program = self.model.rs.program.toDict()
            
        dlg = wxPV.wxProgViewer(title="Ramp and Soak program viewer",
                                  data=program,
                                  path=self.pathProg,
                                  units=self.units)
        dlg.Show()

    def onAbort(self, event) -> None:
        if self.connected:
            dlg = wx.MessageDialog( self.GUIobj.window,
                                    "Are you sure you want to abort and stop the unit?", #< Message
                                    "Abort operation",             #< Title
                                    wx.OK|wx.CANCEL)                     #< Buttons
            ok = dlg.ShowModal() #< Show it
            dlg.Destroy()        #< Destroy it when finished.
            if ok == wx.ID_OK:
                if self.model:
                    self.model.stop()
                self._enableModeBtn()

    def _start(self, proc, path) -> None:
        self.model.unit.details["UID"] = self.unit.uid.GetValue()
        proc(path)
        self._disableModeBtn()
        
    def onMonitor(self, event) -> None:
        self._start(self.model.startMon, path="")
        self.ctrlBtnList[0].SetBackgroundColour( (0,100,0) )

    def onManual(self, event) -> None:
        self._start(self.model.startMan, path=os.path.join(self.pathReport, "meas"))
        self.ctrlBtnList[0].SetBackgroundColour( (0,100,0) )

    def onStandard(self, event) -> None:
        dlg = wx.MessageDialog( self.GUIobj.window,
                                "Make sure the UNIT is in CAL mode", #< Message
                                "Start standardization",             #< Title
                                wx.OK|wx.CANCEL)                     #< Buttons
        ok = dlg.ShowModal() #< Show it
        dlg.Destroy()        #< Destroy it when finished.
        if ok == wx.ID_OK:
            self.model.std.prnUnits = self.units
            self._start(self.model.startStd, path=os.path.join(self.pathReport, "std"))
            self.ctrlBtnList[1].SetBackgroundColour( (0,100,0) )

    def onCalibration(self, event) -> None:
        self.model.rs.prnUnits = self.units
        self._start(self.model.startCal, path=os.path.join(self.pathReport, "cal"))
        self.ctrlBtnList[2].SetBackgroundColour( (0,100,0) )

    def onAutoStdCal(self, event) -> None:
        self.model.std.prnUnits = self.units
        self.model.rs.prnUnits = self.units
        self.model.unit.details["UID"] = self.unit.uid.GetValue()
        self.model.startStdCal(stdPath=os.path.join(self.pathReport, "std"),
                               calPath=os.path.join(self.pathReport, "cal")
                               )
        self.ctrlBtnList[3].SetBackgroundColour( (0,100,0) )
        self._disableModeBtn()

    def onRampAndSoak(self, event) -> None:
        self._start(self.model.startRs, path=os.path.join(self.pathReport, "meas"))
        self.ctrlBtnList[4].SetBackgroundColour( (0,100,0) )

    def onClose(self, event) -> None:
        self.close()
        
    def onConnect(self, event) -> None:
        if self.connected:
            self.model.stop()
            self.model.disconnect()
            self.connected = False
            self.connectBtn.SetLabel("CONNECT")
            self._disableAllCtrlBtn()
        else:
            self.model.connect()
            if self.model.dmm.isConnected():
                self.connected = True
                self.connectBtn.SetLabel("DISCONNECT")
                if self.model.unit.isConnected():
                    print("Station will run using UNIT and DMM/PRT")
                    self.monBtn.Bind(wx.EVT_BUTTON, self.onManual)
                    self._enableAllCtrlBtn()
                else:
                    print("Station will only monitor the DMM/PRT")
                    self.monBtn.Bind(wx.EVT_BUTTON, self.onMonitor)
                    self.monBtn.Enable()
                    self.abortBtn.Enable()
            else:
                print("Station will run without DMM")
                if self.model.unit.isConnected():
                    self.connected = True
                    self.connectBtn.SetLabel("DISCONNECT")
                    self.monBtn.Bind(wx.EVT_BUTTON, self.onManual)
                    self._enableRampAndSoakBtn()
                    self.abortBtn.Enable()

    def scanGPIB(self) -> list[int]:
        print("Scanning for device on GPIB...")
        unitsOnBus = self.rm.list_resources()     #<Slow function
        s = "Devices found on bus:\n"
        i = 0
        for dev in unitsOnBus:
            s += "%d - %s\n"%(i, dev)
            i += 1
        print(s)
        return s

    def onConfig(self, event):
        """  """
        dlg = wxSTNCFG.wxStationConfigDialog(self)
        dlg.Show() #< Show it
        #ok = dlg.ShowModal() #< Show it
        #dlg.Destroy()        #< Destroy it when finished.

    def onScanGPIB(self, event):
        """  """
        dlg = wx.MessageDialog( self.GUIobj.window,
                                self.scanGPIB(),              #< Message
                                "IEEE488 (VISA/GPIB) scan",   #< Title
                                wx.OK)                        #< Buttons
        ok = dlg.ShowModal() #< Show it
        dlg.Destroy()        #< Destroy it when finished.
            
    def onSaveAs(self, event) -> None:
        self.readBack()
        saveAs()

    def saveAs(self) -> None:
        dlg = wx.FileDialog(self.GUIobj, "Choose a file", self.path, "", "*.json", wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            path = dlg.GetDirectory()
            self.model.config.saveStationCfg(path=path, filename=filename,
                                             unitFile = self.unit.file.getPathName(),
                                             dmmFile = self.dmm.file.getPathName(),
                                             prtFile = self.prt.file.getPathName()
                                             )
        dlg.Destroy()

    def onLoad(self, event) -> None:
        """Choose file"""
        dlg = wx.FileDialog(self.GUIobj, "Choose a file", self.path, "", "*.json", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            path = dlg.GetDirectory()
            self.load(path, filename)
        dlg.Destroy()

    def load(self, path, filename) -> None:
        """Choose file"""
        filename = os.path.join( path, filename )
        self.model = STN.Station( rm=self.rm, cfgFile=filename, view=self.updateRealTimeDisplay )
        self.updateDetails()
        if self.model:
            self.connectBtn.Enable()
            self.model.rs.program.loadFromFile( path="", filename=self.model.config.cfg["PROG"] )

    def onLoadProg(self, event):
        """Choose file"""
        dlg = wx.FileDialog(self.GUIobj, "Choose program", self.pathProg, "", "*.json", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            path = dlg.GetDirectory()
            progFilename = os.path.join( path, filename )
            if self.model:
                self.model.config.cfg["PROG"] = progFilename
                self.model.rs.program.loadFromFile( path="", filename=progFilename )
        dlg.Destroy()
        self.updateDetails() #< Update the GUI with the data of the station model

##    def load(self, path, filename) -> None:
##        """Load a configuration file"""
##        self.data = fileLib.loadJsonFile(path=path, name=filename, ext="")
##        self.updateDetails()
