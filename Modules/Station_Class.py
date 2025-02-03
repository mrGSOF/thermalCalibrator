import time, json, logging

from CommModules import COMM_base as COMM
from CommModules import RS232_Class as RS
from CommModules import IEEE488_Class as IEEE

from Modules import fileLib as FILE
from Modules import ITS68, ITS90
from Modules import ITS_conversion as ITS

from Modules import KNC3604U, KNC3604A, KNC3605A, KNC360x_base
from Modules import PRT_device as PRT
from Modules import HP34401_device as DMM

from Modules import RampAndSoak_FSM as RS_FSM
from Modules import Standard_FSM as STD_FSM
from Modules import Manual_FSM as MAN_FSM
from Modules import Monitor_FSM as MON_FSM
from Modules import StdCal_FSM as STDCAL_FSM

class Config():
    def __init__(self, filename=None, contant=None, cfg=None):
        self.filename = filename
        self.contant = contant
        self.cfg = cfg
        if filename:
            self.loadStationCfg(filename)

    def loadStationCfgFile(self, filename=None) -> None:
        if filename != None:
            self.filename = filename

        try:
            self.contant = FILE.loadJsonFile(name=filename.split('.json')[0])
            print("Found file <%s>"%(filename))
        except ValueError:
            print("Error loading the station configuration file")
            raise ValueError

    def loadStationCfg(self, filename=None) -> None:
        try:
            self.loadStationCfgFile(filename)
            uutCfg = self.loadUutCfg()
            print( "UUT configuration file loaded")
            
            unitCfg = self.loadUnitCfg()
            print( "UNIT configuration file loaded")
            
            progFilename = self.loadProgFilename()
            print( "Ramp and Soak program loaded")

            soak = 25.0 #< Minutes
            if "SOAK" in self.contant:
                soak = self.contant["SOAK"]
            else:
                self.contant["SOAK"] = soak

            self.cfg = {"SOAK":soak, "UUT":uutCfg, "UNIT":unitCfg, "PROG":progFilename}
            print("Station configuration files load complete")

        except:
            print("Error loading one devices configuration file")
            raise ValueError
                
    def saveStationCfg(self, path, filename,
                       desc = "No description",
                       soak = 25.0,
                       unitFile = "",
                       dmmFile = "",
                       prtFile = "",
                       rsFile = "") -> None:

        self.updateStationCfg(desc, soak, unitFile, dmmFile, prtFile, rsFile)
        self.save(path=path, name=filename)

    def updateStationCfg(self, desc, soak, unitFile, dmmFile, prtFile, rsFile):
        self.contant = {"DESC":desc,
                        "SOAK":soak, #< Soak time for STD
                        "UNIT":unitFile,
                        "UUT":{"DMM":dmmFile, "PRT":prtFile},
                        "PROG":rsFile}

    def save(self, path, filename):
        FILE.saveJsonFile(dat=self.contant, path=path, name=filename, ext="")

    def loadUutCfg(self, dmmFile=None, prtFile=None) -> dict:
        """ """
        dmmCfg = self.loadDmmCfg(dmmFile)
        prtCfg = self.loadPrtCfg(prtFile)
        return {"PRT":prtCfg, "DMM":dmmCfg}

    def loadDmmCfg(self, filename=None) -> dict:
        """ """
        if filename != None:
            self.contant["UUT"]["DMM"] = filename
        filename = self.contant["UUT"]["DMM"]
        print("Opening <%s>"%(filename))
        return FILE.loadJsonFile(name=filename, ext='')

    def loadPrtCfg(self, filename=None) -> dict:
        """ """
        if filename != None:
            self.contant["UUT"]["PRT"] = filename
        filename = self.contant["UUT"]["PRT"]
        print("Opening <%s>"%(filename))
        return FILE.loadJsonFile(name=filename, ext='')
    
    def loadUnitCfg(self, filename=None) -> dict:
        """ """
        if filename != None:
            self.contant["UNIT"] = filename
        filename = self.contant["UNIT"]
        print("Opening <%s>"%(filename))
        return FILE.loadJsonFile(name=filename, ext='')

    def loadProgFilename(self, filename=None) -> str:
        """ """
        if "PROG" not in self.contant:
            self.contant["PROG"] = None

        if filename != None:
            self.contant["PROG"] = filename

        filename = self.contant["PROG"]
        print("Ramp and Soak program loaded <%s>"%(filename))
        return filename

class Station():
    def __init__(self, rm, cfgFile=None, view=None):
        self.rm = rm
        self.dmm = None
        self.prt = None
        self.unit = None
        self.config = None
        self.view = view
        self.units = 'C'
        self.gpibList = []
        self.configStation(cfgFile)
        stdSoak = self.config.cfg["SOAK"]
        rsProg = self.config.cfg["PROG"]
        self.rs = RS_FSM.RampAndSoak(unit=self.unit, ref_uut=self.prt, view=view)
        self.rs.program.loadFromFile( path="", filename=rsProg )
        self.std = STD_FSM.Standardization(unit=self.unit, sprt=self.prt, soak=stdSoak, view=view)
        self.man = MAN_FSM.Manual(unit=self.unit, uut=self.prt, view=view)
        self.mon = MON_FSM.Monitor(uut=self.prt, view=view)
        self.stdCal = STDCAL_FSM.Manager(self)
        self.report = self.rs.report
        
    def configStation(self, filename=None):
        if filename:
            try:
                self.config = Config(filename=filename)
                try:
                    self.configPRT(self.config.cfg["UUT"])
                    print( "DMM/PRT configuration complete" )

                    self.configUnit(self.config.cfg["UNIT"])
                    print( "UNIT configuration complete" )
                except:
                    print("Error configuring one of the station devices")
            except:
                self.config = None
                print("Error in station configuration file")
                raise ValueError

    def connect(self):
        try:
            self.connectPRT()
        except:
            #raise ValueError
            print("Error connecting to PRT/DMM devices")

        try:
            self.connectUnit()
        except:
            #raise ValueError
            print("Error connecting UNIT")

    def disconnect(self):
        try:
            self.dmm.close()
        except:
            print("Error connecting to PRT/DMM devices")

        try:
            self.unit.close()
        except:
            print("Error connecting UNIT")

    def scanGPIB(self) -> list[int]:
        print("Scanning for device on GPIB...")
        unitsOnBus = self.rm.list_resources() #<Slow function
        s = "Devices found on bus: (unitsOnBus[])"
        self.gpibList = []
        for dev in unitsOnBus:
            s += "%d - %s\n"%(len(self.gpibList),dev)
            self.gpibList.append(dev)
        print(s)
        return self.gpibList

    def _configDMM(self, dmmCfg) -> COMM.COMM_base:
        """
        Connects to a DMM over RS232 or IEEE488 BUS
        dmmCfg = {"COEF":{"TYPE":"SERIAL", "LANG":"Fluke", "COM":"COM1", "BAUD":4800,
                          "PARITY":0, "DATA":8}
               or "COEF":{"TYPE":"IEEE488", "LANG":"SCPI", "ADDR":"GPIB0::6::INSTR"}}
         """
        if self.dmm:
            self.dmm.close()
            self.dmm = None

        coef = dmmCfg["COEF"]
        comm = None
        if coef["TYPE"] == "SERIAL":
            comm = RS.SERIAL( coef )

        elif coef["TYPE"] == "IEEE488":
            comm = IEEE.IEEE488( self.rm, coef )

        if comm:
            self.dmm = DMM.HP34401( comm=comm, lang=coef["LANG"], details=dmmCfg )
        else:
            self.dmm = None
        return self.dmm

    def _connectDMM(self) -> COMM.COMM_base:
        """ """
        if self.dmm:
            self.dmm.open()
            if self.unit.comm.isConnected != True:
                raise ValueError

    def configPRT(self, prtCfg) -> PRT.PRT_dev:
        """
        Build the COMM object and PRT devices and prepare them for sampling.
        Return True if ready.
        False if error.
        """
        if self.prt != None:
            self.prt.close()
            self.prt = None
        dmmCfg = prtCfg["DMM"]
        self._configDMM(dmmCfg)

        prtCfg = prtCfg["PRT"]
        its = ITS.ITS( prtCfg["COEF"] )
        self.prt = PRT.PRT_dev( comm=self.dmm, its=its, details=prtCfg )
        return self.prt

    def connectPRT(self) -> PRT.PRT_dev:
        """ """
        if self.prt:
            self.prt.open()

    def configUnit(self, unitCfg) -> KNC360x_base.KNC360x:
        """
        Build the COMM object and UNIT device.
        Return True if ready.
        None if error.
        unitCfg = {"MFR":"KNC", "MODEL":"3604A", "SN":"A1001",
                  "EXP_DATE":{"YEAR":2022, "MONTH":6, "DAY":19}
                  {"COEF":{"TYPE":"IEEE488", "ADDR":"GPIB0::1::INSTR"}}
              or  {"COEF":{"TYPE":"SERIAL", "COM":"COM1", "BAUD":115200}
                  }
        """
        coef = unitCfg["COEF"]
        if coef["TYPE"] == "SERIAL":
            comm = RS.SERIAL( coef )

        elif coef["TYPE"] == "IEEE488":
            comm = IEEE.IEEE488( self.rm, coef )

        if comm:
            ### Select the proper system-model objecct
            if unitCfg["MODEL"] == "3604U":
                self.unit = KNC3604U.KNC3604U( comm=comm, details=unitCfg )
            elif unitCfg["MODEL"] == "3604A":
                self.unit = KNC3604A.KNC3604A( comm=comm, details=unitCfg )
            elif unitCfg["MODEL"] == "3605A":
                self.unit = KNC3605A.KNC3605A( comm=comm, details=unitCfg )
            else:
                print("UNIT MODEL %s NOT RECOGNIZED - USING BASE CLASS!"%(unitfg["MODEL"]))
                self.unit = KNC360x_base.KNC360x( comm=comm, details=unitCfg )
        else:
            self.unit = None
        return self.unit

    def connectUnit(self) -> None:
        """ """
        if self.unit:
            self.unit.open()
            self.setUnits(self.units)
            if self.unit.isConnected() != True:
                raise ValueError

    def _startProcedure(self, proc, Type, path):
        self.stop()
        self.setUnits(self.units)
        proc.start(Type, path)
        self.report = proc.report

    def setUnits(self, units):
        if self.unit:
            self.units = units
            self.unit.setDispUnits(units)
        
    def startMon(self, path="./") -> None:
        self._startProcedure(self.mon, Type="Monitor", path=path)

    def startMan(self, path="./") -> None:
        self._startProcedure(self.man, Type="Manual", path=path)

    def startStd(self, path="./") -> None:
        self._startProcedure(self.std, Type="STD", path=path)

    def isStdRunning(self) -> bool:
        return not self.std.state.isState(self.std.state.MONITOR)

    def startCal(self, path="./") -> None:
        self._startProcedure(self.rs, Type="CAL", path=path)

    def isCalRunning(self) -> bool:
        return not self.rs.state.isState(self.rs.state.MONITOR)

    def startRs(self, path="./") -> None:
        self._startProcedure(self.rs, Type="MEAS", path=path)

    def isRsRunning(self) -> bool:
        return not self.rs.state.isState(self.rs.state.MONITOR)

    def startStdCal(self, stdPath="./", calPath="./") -> None:
        self.stop()
        self.setUnits(self.units)
        self.stdCal.start(stdPath=stdPath, calPath=calPath)

    def stop(self):
        self.mon.pause()
        self.man.pause()
        self.std.pause()
        self.rs.pause()
        self.stdCal.pause()
        if self.unit.isConnected():
            for i in range(0,3):
                time.sleep(0.2)
                self.unit.setOff()

    def close(self):
        print("Stoping all active threads")
        self.mon.stop()
        self.man.stop()
        self.std.stop()
        self.rs.stop()
        self.stdCal.stop()

        if self.mon.started:
            self.mon.join()

        if self.man.started:
            self.man.join()

        if self.std.started:
            self.std.join()

        if self.rs.started:
            self.rs.join()

        self.disconnect()

    def StdCal_Process(self):
        ...
        
logging.basicConfig(level = logging.DEBUG)
logger = logging.getLogger()
