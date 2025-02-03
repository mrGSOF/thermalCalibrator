import os, wx
from Modules import Report_Class
from Modules import wxJsonViewer_tiny as wxJV
from Modules import TEMP_conv as T
from Modules import ReportToExcel_lib as XLS

class wxReportViewer(wxJV.JSON_viewer_Box):
    def __init__(self, title="Viewer", data=None, size=[400,640], path="./", units='F'):
        self.data = data
        self.path = path
        self.units = units #< Just add the units {C,F}
        self.initUI(title, size)
        self.genTree()

    def initUI(self, title, size):
        super().initUI(title, size)
        pos = [305, 150]
        exportBtn = wx.Button(self.GUIobj, -1, "Export .xlsx", pos=pos )
        self.Bind(wx.EVT_BUTTON, self.onExportToExcel, exportBtn)

    def genTree(self):
        tree = wxReportTree(self.GUIobj, self.data, self.units) #< Build the report tree and pass the units
        tree.SetSize([300,700])
        tree.tree.SetSize([300,600])
        self.tree = tree
        tree.SetFocus()

    def onExportToExcel(self, event):
        self.FileDialog(wx.FD_SAVE, ext="*.xlsx")
        if self.filename:
            report = Report_Class.Report()
            report.dat = self.tree.data
            print(self.units)
            data = report.convTo(self.units)
            XLS.export( report=data, filename=os.path.join(self.path, self.filename) )
            print("EXPORT TO .XLSX")

        
        
class wxReportTree(wxJV.MyTreePanel):  
    def __init__(self, parent, data=None, units='F'): 
        self.units = units
        super().__init__(parent, data)

    def json_tree(self, parent, dictionary):
        for key in dictionary:
            if isinstance(dictionary[key], dict):
                folder = self.tree.AppendItem(parent, key)              #< DICTIONARY (GUI ACCESS)
                self.tree.SetItemFont(folder, self.fontFolder)
                self.json_tree(folder, dictionary[key])
            elif isinstance(dictionary[key], (tuple, list)):
                folder = self.tree.AppendItem(parent, key + "[..]")     #< LIST (GUI ACCESS)
                self.tree.SetItemFont(folder, self.fontFolder)
                self.json_tree(folder,
                    dict([(str(i), x) for i, x in enumerate(dictionary[key])]))
            else:
                color = (0,0,0)
                value = dictionary[key]
                if key == "AMB":
                    font = self.fontNumber
                    val = None
                    if value != None:
                        val = "%1.2f"%(T.C_to_units(value, self.units))

                elif (key == "UNIT") or (key == "REF") or (key == "UUT") or (key == "THRS_MIN") or (key == "THRS_MAX"):
                    font = self.fontNumber
                    val = None
                    if value != None:
                        val = "%1.8f"%(T.C_to_units(value, self.units))

                elif key == "MARK":
                    val = str(value)
                    if value == "FAIL":
                        color = (200,0,0)
                        font = wx.Font(10, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
                    else:
                        color = (0,170,0)
                        font = wx.Font(10, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

                elif (key == "DEV") or (key == "THRS"):
                    font = self.fontNumber
                    val = None
                    if value != None:
                        T0 = T.C_to_units(25.0, self.units)
                        T1 = T.C_to_units(25.0 +value, self.units)
                        dev = T1 -T0
                        val = "%1.2f"%(dev)

                elif key == "UNITS":
                    font = self.fontString
                    val = self.units

                else:
                    if value is None:
                        value = "None"
                    if type(value) == float:
                        val = "%1.8f"%(value)
                        font = self.fontNumber
                    else:
                        val = str(value)
                        font = self.fontString
                item = self.tree.AppendItem(parent,"%s: %s"%(key, val)) #< VALUE (GUI ACCESS)
                self.tree.SetItemFont(item, font)
                self.tree.SetItemTextColour(item, color)
