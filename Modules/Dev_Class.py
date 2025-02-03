from Modules import Date
from Modules import ITS_conversion

def Dev(Type):
    dev = {"MODEL":"",
           "MFR":"",
           "SN":"",
           "EXP_DATE":Date.date(1,1,2020)}

    if (Type == "UNIT") or (Type == "DMM"):
        dev["COEF"] = {"TYPE":"IEEE",
                       "ADDR":1,      #< For IEEE or GPIB
                       "COM":1,       #< For RS232
                       "BAUD":115200  #< For RS232
                       }

    elif Type == "PRT":
        dev["COEF"] = ITS_conversion.ITS90_DICT()

    else:
        dev["COEF"] = {}

    return dev
