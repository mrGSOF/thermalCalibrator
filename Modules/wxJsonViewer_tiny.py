import wx
from Modules import fileLib
#import fileLib

class JSON_viewer_Box(wx.Dialog):
    def __init__(self, title="Viewer", data=None, size=[400,640], path="./"):
        self.data = data
        self.path = path
        self.initUI(title, size)
        self.genTree()

    def initUI(self, title, size):
        disp_size = [size[0], size[1]]
        if ( disp_size[1] > 700):
            disp_size[1] = 700

        wx.Dialog.__init__(self, None, -1, title,
            style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|
                wx.TAB_TRAVERSAL, size=disp_size)

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        window = wx.ScrolledWindow(self, -1, size=[size[0]-20, size[1]])
        window.SetScrollbars(1, 1, size[0]-50, size[1]-50)
        self.GUIobj = window

        DY = 30
        pos = [305, 10]
        RefreshBtn = wx.Button(window, -1, "Refresh", pos=pos )
        self.Bind(wx.EVT_BUTTON,  self.OnRefresh, RefreshBtn)

        pos[1] += DY
        FileReadBtn = wx.Button(window, -1, "Read File", pos=pos )
        self.Bind(wx.EVT_BUTTON,  self.OnFileRead, FileReadBtn)

        pos[1] += DY
        FileWriteBtn = wx.Button(window, -1, "Write File", pos=pos )
        self.Bind(wx.EVT_BUTTON,  self.OnFileWrite, FileWriteBtn)

        pos[1] += DY
        CloseBtn = wx.Button(window, -1, "Close", pos=pos )
        self.Bind(wx.EVT_BUTTON,  self.OnClose, CloseBtn)

    def genTree(self):
        tree = MyTreePanel(self.GUIobj, self.data)
        tree.SetSize([300,700])
        tree.tree.SetSize([300,600])
        self.tree = tree
        tree.SetFocus()
        
    def OnClose(self, event):
        self.Destroy()

    def OnRefresh(self, event):
        self.tree.update(self.data)

##    def OnAutoRefreshEn(self, event):
##        if self.AutoRefreshEn.GetValue():
##            t = threading.Thread(target=self.AutoRefreshWorker)
##            t.start()
##        
##    def AutoRefreshWorker(self):
##        while self.AutoRefreshEn.GetValue():
##            self.OnRefresh(1)
##            
##            period = float(self.AutoRefreshPeriod.GetValue())
##            time.sleep(period)

    def FileDialog(self, DialogType=wx.FD_OPEN, ext="*.json"):
        dlg = wx.FileDialog(self.GUIobj, "Choose a file", self.path, "", ext, DialogType)
        self.filename = ""
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.path = dlg.GetDirectory()
        dlg.Destroy()

    def OnFileRead(self, event):
        self.FileDialog(wx.FD_OPEN)
        if self.filename != "":
            data = fileLib.loadJsonFile(path=self.path, name=self.filename, ext="")
            self.tree.update(data)

    def OnFileWrite(self, event):
        self.FileDialog(wx.FD_SAVE)
        if self.filename != "":
            self.save()

    def save(self):
        fileLib.saveJsonFile(self.tree.data, path=self.path, name=self.filename, ext="")
        
class MyTreePanel(wx.Panel):  
    def __init__(self, parent, data=None): 
        # Create Tree Control
        wx.Panel.__init__(self, parent) 
        self.tree = wx.TreeCtrl(self, wx.ID_ANY,
                           wx.DefaultPosition,
                           wx.DefaultSize,
                           wx.TR_HAS_BUTTONS) 
        self.tree.SetForegroundColour('#000000')
        self.tree.SetBackgroundColour('#ffffff')
        self.fontRoot = wx.Font(13, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.fontFolder = wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.fontItem = wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.fontNumber = wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.fontString = wx.Font(10, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

        self.root = None              #< self.refresh() will ad the root
        self.update(data)
        self.tree.Expand(self.root)   #< Expand whole tree
        self.tree.SetSize(270,500)

##        self.btn = wx.Button(self, 1, "Collapse") #< Add button in frame 
##
##        # Bind event function with button 
##        self.btn.Bind(wx.EVT_BUTTON, self.OnClick) 
##        
##        sizer = wx.BoxSizer(wx.VERTICAL) 
##        sizer.Add(self.tree, 1, wx.EXPAND) 
##        sizer.Add(self.btn, 0, wx.EXPAND)
##        self.SetSizer(sizer)

    def update(self, data=None):
        if data == None:
            data = {}
        self.data = data
        
        if self.root:
            self.tree.Delete(self.root)

        self.root = self.tree.AddRoot('Root')     #< Add root to Tree Control 
        self.tree.SetItemFont(self.root, self.fontRoot)
        self.json_tree(self.root, data)

    def OnClick(self, event): 
        # Collapse all children of itm recursively 
        self.tree.CollapseAllChildren(self.root) 

    def json_tree(self, parent, dictionary):
        for key in dictionary:
            #print(key)
            if isinstance(dictionary[key], dict):
                #print("dict")
                folder = self.tree.AppendItem(parent, key)                #< GUI ACCESS
                self.tree.SetItemFont(folder, self.fontFolder)
                self.json_tree(folder, dictionary[key])
            elif isinstance(dictionary[key], (tuple, list)):
                #print("list")
                folder = self.tree.AppendItem(parent, key + "[..]")         #< GUI ACCESS
                self.tree.SetItemFont(folder, self.fontFolder)
                self.json_tree(folder,
                          dict([(str(i), x) for i, x in enumerate(dictionary[key])]))
            else:
                #print("value")
                value = dictionary[key]
                if value is None:
                    value = "None"
                #tree = self.tree.AppendItem(parent, key)               #< GUI ACCESS
                #item = self.tree.AppendItem(tree, str(value))                 #< GUI ACCESS
                if type(value) == float:
                    val = "%1.8f"%value
                    font = self.fontNumber
                else:
                    val = str(value)
                    font = self.fontString
                item = self.tree.AppendItem(parent,"%s: %s"%(key, val)) #< GUI ACCESS
                self.tree.SetItemFont(item, font)

if __name__ == "__main__":
    #---------------------------------------------------------------------------
    class MyFrame(wx.Frame):
        def __init__(self, parent, id, title, data): 
            super().__init__(parent, -1, title)  

            #self.SetIcon(wx.Icon('./icons/wxwin.ico', wx.BITMAP_TYPE_ICO))
            panel = MyTreePanel(self, data)

            self.Show() #< Show frame 
            
    #---------------------------------------------------------------------------
    class MyApp(wx.App):
        def OnInit(self):
            data = {"TYPE": "CAL", "UID": "A1001",
             "DATE": {"DAY": 11, "MONTH": 3, "YEAR": 2022},
             "UUT": {"MFR": "KNC", "MODEL": "3604U", "UID": "A1001",
                     "EXP_DATE": {"YEAR": 2022, "MONTH": 6, "DAY": 19},
                     "COEF": {"TYPE": "IEEE488", "ADDR": "GPIB0::1::INSTR"}},
             "DMM": {"MFR": "HP", "MODEL": "HP34401A", "SN": "4886",
                    "EXP_DATE": {"YEAR": 22, "MONTH": 5, "DAY": 19},
                    "COEF": {"TYPE": "IEEE488", "LANG": "Fluke", "ADDR": "GPIB0::6::INSTR"}},
             "REF": {"MFR": "Fluke", "MODEL": "5628", "SN": "2011",
                     "EXP_DATE": {"YEAR": 22, "MONTH": 5, "DAY": 19},
                     "COEF": {"TYPE": "ITS90", "RTPW": 24.492, "a4": -0.017702, "b4": 0.011854, "a7": -0.01843, "b7": -0.001073193, "c7": 0.0005989515}},
             "COEF": {"TYPE": "ITS27", "R0": 200.0, "Alpha": 0.00395, "Delta": 1.5, "AMB": 25.0},
                      "RESULTS": {"UNITS": "C", "AMB": 29.166666666666668,
                      "DEVTBL": [{"UNIT": 36.51, "REF": 36.607497234238, "UUT": 36.51, "UNITS": "C", "DEV": -0.0974972342379985, "AMB": 28.94, "SOAK": 0.5, "MARK": "PASS"},
                                 {"UNIT": 40.237, "REF": 40.5195480433066, "UUT": 40.237, "UNITS": "C", "DEV": -0.28254804330659766, "AMB": 29.37, "SOAK": 0.5, "MARK": "PASS"},
                                 {"UNIT": 40.424, "REF": 40.66152564587861, "UUT": 40.424, "UNITS": "C", "DEV": -0.23752564587861258, "AMB": 29.19, "SOAK": 1.0, "MARK": "PASS"}]}
            }
            frame = MyFrame(None, -1, "wx.TreeCtrl (CollapseAllChildren)", data)
            frame.Show(True)
            #self.SetTopWindow(frame)
            return True

    #---------------------------------------------------------------------------
        
    app = MyApp(0)
    app.MainLoop()
