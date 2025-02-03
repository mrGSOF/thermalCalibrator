import time
import json
import pyvisa as visa
from Modules import Station_Class as STN

"""
### Physical layer configurations
its68Cfg={"COEF":{"TYPE":"ITS68", "R0":200.0, "Alpha":0.00363, "Delta":1.49}}

its90Cfg={"COEF":{"TYPE":"ITS90", "RTPW":200.0, "a4":0.0, "b4":0.0,
                  "a7":0.0, "b7":0.0, "c7":0.0}}

rsCfg =  {"COEF":{"TYPE":"SERIAL", "LANG":"Fluke", "COM":"COM1", "BAUD":4800,
          "PARITY":0, "DATA":8}
         }

ieeeCfg= {"COEF":{"TYPE":"IEEE488", "LANG":"Fluke", "ADDR":"GPIB0::6::INSTR"}}

### Instrument (device) configurations
dmmCfg1= {"MFR":"KNC", "MODEL":"4201", "SN":"72634",
          "EXP_DATE":{"YEAR":23, "MONTH":5, "DAY":19},
          "COEF":rsCfg["COEF"]
          }

dmmCfg2= {"MFR":"KNC", "MODEL":"HP34401A", "SN":"453579",
          "EXP_DATE":{"YEAR":23, "MONTH":5, "DAY":19},
          "COEF":ieeeCfg["COEF"]
          }

prtCfg = {"SPRT":{"MFR":"KNC", "MODEL":"4201", "SN":"72634",
          "EXP_DATE":{"YEAR":23, "MONTH":5, "DAY":19},
          "COEF":its68Cfg["COEF"]},
          "DMM":dmmCfg2
          }

unitCfg = {"MFR":"KNC", "MODEL":"3604A", "SN":"A1001",
           "EXP_DATE":{"YEAR":2022, "MONTH":6, "DAY":19},
           "COEF":{"TYPE":"IEEE488", "ADDR":"GPIB0::1::INSTR"}
#         or   "COEF":{"TYPE":"SERIAL", "COM":"COM1", "BAUD":115200}
          }
"""
rm = visa.ResourceManager()

pathStation = "./config/stations/"
pathProg = "./config/prog/"

#s1 = STN.Station( rm=rm, cfgFile= pathStation +"station_3604U.json" )
#s1.rs.program.loadFromFile( path=pathProg, filename="RS_TEST" )

try:
    #s1 = STN.Station( rm=rm, cfgFile= pathStation +"station_3604U.json" )
    s1 = STN.Station( rm=rm, cfgFile= pathStation +"station_3605A.json" )
except ValueError:
    s1 = None
    print( "Error creating the station" )

if s1:
    s1.connect()
"""
s1.rs.program.addStep(rate=1.2, targetC=35, soak_m=0.1)
s1.rs.program.addStep(rate=1.2, targetC=45, soak_m=0.1)
s1.rs.program.addStep(rate=1.2, targetC=55, soak_m=0.1)
"""
#s2 = Station(rm=rm, cfgFile=path+"station_3605A")

#    s.scanGPIB()
#    s._connectDMM( rsCfg )
#    s._connectDMM( ieeeCfg )

#    s.connectPRT( prtCfg )

#    s.connectUnit( unitCfg )

