import wx
from Modules import wxJsonViewer_tiny as wxJV
from Modules import TEMP_conv as T

class wxProgViewer(wxJV.JSON_viewer_Box):
    def __init__(self, title="Viewer", data=None, size=[400,640], path="./", units='F'):
        self.data = data
        self.path = path
        self.units = units #< Just add the units {C,F}
        self.initUI(title, size)
        self.genTree()

    def genTree(self):
        tree = wxReportTree(self.GUIobj, self.data, self.units) #< Build the report tree and pass the units
        tree.SetSize([300,700])
        tree.tree.SetSize([300,600])
        self.tree = tree
        tree.SetFocus()

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
                font = self.fontNumber

                if (key == "RATE")or (key == "PASS_THRES"):
                    val = None
                    if value != None:
                        T0 = T.C_to_units(0, self.units)
                        T1 = T.C_to_units(0 +value, self.units)
                        dev = T1 -T0
                        val = "%1.2f %s"%(dev, self.units)

                    if key == "PASS_THRES":
                        color = (200,0,0)
                        font = wx.Font(10, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
                    else:
                        val = "%s/MIN"%(val)
                        
                elif key == "SOAK":
                    val = None
                    if value != None:
                        val = "%1.1f MIN"%(value)

                elif key == "TARGET":
                    val = None
                    if value != None:
                        val = "%1.2f %s"%(T.C_to_units(value, self.units), self.units)

                else:
                    if value is None:
                        value = "None"
                    if type(value) == float:
                        val = "%1.8f"%(value)
                    else:
                        val = str(value)
                        font = self.fontString

                item = self.tree.AppendItem(parent,"%s: %s"%(key, val)) #< VALUE (GUI ACCESS)
                self.tree.SetItemFont(item, font)
                self.tree.SetItemTextColour(item, color)
