import time
import wx, threading
from Modules import TEMP_conv as T

class wxManualViewer(wx.Dialog):
    def __init__(self, title="Viewer", unit=None, size=[250,160], units='F'):
        self.unit = unit
        self.units = units #< Just add the units {C,F}
        self.initUI(title, size)

    def initUI(self, title, size):
        disp_size = [size[0], size[1]]
        if ( disp_size[1] > 700):
            disp_size[1] = 700

        wx.Dialog.__init__(self, None, -1, title,
            style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|
                wx.TAB_TRAVERSAL, size=disp_size)

        #self.Bind(wx.EVT_CLOSE, self.OnClose)

        GUI = wx.ScrolledWindow(self, -1, size=[size[0]-20, size[1]])
        GUI.SetScrollbars(1, 1, size[0]-50, size[1]-50)
        GUI = GUI
        fontTele = wx.Font(18, family = wx.FONTFAMILY_MODERN, style = wx.FONTSTYLE_NORMAL, weight = wx.FONTWEIGHT_BOLD, 
                      underline = False, faceName ="", encoding = wx.FONTENCODING_DEFAULT)

        posX = 15
        posY = 15
        
        wx.StaticText(GUI, -1, "SET PT", pos=(posX, posY +9) )
        self.Tctrl = wx.TextCtrl( GUI, -1, "XXXX.XX",
                                  pos=(posX+50, posY),
                                  size=(110,35) )

        setBtn = wx.Button(GUI, -1, "set", pos=(posX +170, posY), size=(40,35) )
        self.Bind(wx.EVT_BUTTON, self.onSetTarget, setBtn)

        self.Tctrl.SetFont(fontTele)
        self.Tctrl.SetBackgroundColour( [0,200,0])
        #self.Tctrl.Bind(wx.EVT_TEXT_ENTER, self.onSetTarget)

        DY = 40
        posY += DY
        lblList = ("F", "C") 
        self.units = wx.RadioBox(GUI, label = "Units",
                                pos = (posX, posY),
                                choices = lblList,
                                majorDimension = 1,
                                style = wx.RA_SPECIFY_ROWS) 

        posY += 10
        onBtn = wx.Button(GUI, -1, "ON", pos=(posX +90, posY), size=(40,35) )
        self.Bind(wx.EVT_BUTTON, self.onPowerOn, onBtn)
        onBtn.SetBackgroundColour( (0,200,0) )

        offBtn = wx.Button(GUI, -1, "OFF", pos=(posX +140, posY), size=(40,35) )
        self.Bind(wx.EVT_BUTTON, self.onPowerOff, offBtn)
        offBtn.SetBackgroundColour( (200,0,0) )

    def onPowerOn(self, event):
        if self.unit:
            self.unit.setOn()

    def onPowerOff(self, event):
        if self.unit:
            self.unit.setOff()

    def onSetTarget(self, event):
        """
        Check for numeric entry and limit to 2 decimals
        accepted result are sent to the unit (if connected)
        """
        rawValue = self.Tctrl.GetValue().strip()
        ### numeric check
        error = True
        if rawValue and all(x in '0123456789.+-' for x in rawValue):
            try:  #< Convert to float and limit to 2 decimals
                value = round(float(rawValue), 2)
                self.Tctrl.ChangeValue(str(value))
                error = False
            except ValueError:
                pass

        if error == False:
            if self.unit:
                units = self.units.GetStringSelection()
                sp = T.units_to_C(value, units)
                self.unit.setTctrl( sp )
        else:
            self.Tctrl.ChangeValue("  ERR  ")
            t = threading.Thread(target=self.restoreValue, args=(rawValue, 0.5)).start()

    def restoreValue(self, value, delay):
        time.sleep(delay)
        self.Tctrl.ChangeValue(value)
