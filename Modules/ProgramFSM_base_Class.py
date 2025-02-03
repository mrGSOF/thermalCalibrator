import logging, time, json
from enum import Enum
from Modules import TEMP_conv
from Modules import threadBasic
from Modules import StopWatch_Class

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger()

def Prog(FreeMode, cycles) -> dict:
    """ Returns a dictionary with the proper program structure """
    return {"AUTO": 1,
            "FREE": int(freeMode),
            "CYCLES": int(cycles),
            "SEQ": []}

def Step(rateC_s, targetC, soak_m=25) -> dict:
    """ Returns a dictionary with the proper program step structure """
    return {"RATE":rateC_s,
            "TARGET":targetC,
            "SOAK":soak_m*60}

class Program():
    def __init__(self, path="", name="Default", seq=[], auto=1, free=0, cycles = 1):
        self.name = name
        self.auto = auto
        self.free = free
        self.cycles = cycles
        self.seq = seq

    def addStep(self, rate, targetC, soak_m, idx=None) -> int:
        """ Append or insert a new step to the program sequence """
        if idx == None:
            idx = len(self.seq) #< Default action is to add the new step last
        self.seq.insert( idx, Step(rate, targetC, soak_m) )
        return len(self.seq)
        
    def delStep(self, i) -> int:
        """ Delete a step from the program sequence """
        N = len(self.seq)
        if i < N:
            self.seq.pop(i)
            N -= 1
        return N

    def loadFromFile(self, filename, path="") -> bool:
        filename = (filename.split(".json"))[0] 
        with open(path +filename +".json") as file:
            prog = json.load(file)
            self.name = filename
            self.auto = prog["AUTO"]
            self.free = prog["FREE"]
            self.cycles = prog["CYCLES"]
            self.seq = prog["SEQ"]
            return True
        return False

    def toDict(self):
        return {"AUTO":self.auto, "FREE":self.free, "CYCLES":self.cycles, "SEQ":self.seq}
    
    def saveToFile(self, path="", filename=None) -> bool:
        if filename == None:
            filename = (filename.split(".json"))[0]
            self.name = filename
            filename = path +self.name +".json"
        with open(filename, 'w') as file:
            prog = self.toDict()
            json.dump(prog, file)
            return True
        return False

class State():
    IDLE = 0
    SETNEW = 1
    APPROACH = 2
    SOAK = 3
    COOLING = 4
    END = 5
    MONITOR = 6

    def __init__(self):
        self.state = self.IDLE
        self.cnt = 0
        super().__init__()

    def isState(self, state) -> bool:
        return self.state == state

    def set(self, state) -> None:
        self.state = state
        
    def get(self) -> int:
        return self.state

    def getStateText(self) -> str:
        ls = "-\|/"
        if self.cnt >= len(ls):
            self.cnt = 0
        ls = ls[self.cnt]
        self.cnt += 1

        if self.isState(self.IDLE):
            return ls+" IDLE / MONITOR"
        elif self.isState(self.SETNEW):
            return ls+" NEW TARGET PT"
        elif self.isState(self.APPROACH):
            return ls+" APPROACHING"
        elif self.isState(self.SOAK):
            return ls+" SOAKING"
        elif self.isState(self.COOLING):
            return ls+" COOLING"
        elif self.isState(self.END):
            return ls+" END / MONITOR"

class Program_FSM(threadBasic.BasicThread):
    def __init__(self, nameID = "FSM", unit=None, view=None):
        self.units = 'C'
        self.unit = unit
        self.view = view
        self.soak_s = -1 #< Unlimited soak time (sec)
        self.soakTimer = -1
        self.soakTime = -1
        self.targetC = 0.0
        self.printer = True
        self.prnUnits = 'F'
        self.program = None
        self.stop_watch = StopWatch_Class.StopWatch()
        self.state = State()
        super().__init__(nameID=nameID, Period=2.0)
        self.reset()

    def _print(self, text, font=0):
        print(text)
        if self.printer:
            self.unit.printLine(text, font)
            time.sleep(3.0)

    def _printReportHeader(self):
        title = {"CAL":"  CALIBRATION",
                 "STD":"STANDARDIZATION"}
                 #"MEAS":"RAMP AND SOAK"}

        hdr = {"CAL": "  STD     UNIT   DEV P/F",
               "STD": "  STD     UNIT    DEV"}
               #"MEAS":"  UUT    UNIT    DEV P/F"}

        report = self.report
        Type = report.getType()
        if self.printer and (Type in title):
            title = title[Type]
            hdr = hdr[Type]
            unit_id = report.getUnitID()
            model = report.getUnitModel()
            sprt_id = report.getRefID()
            sprt_model = report.getRefModel()
            date = report.getDate()

            self._print("%s"%(title), font=2)
            #self._print("NORMAL THERMOMETER", font=0)
            self._print("DATE:%19s"%(date), font=0)
            self._print("%s S/N: %s"%(model, unit_id), font=0)
            self._print("STD: %s"%(sprt_model), font=0)
            self._print("STD S/N: %s"%(sprt_id), font=0)
            self._print("UNITS: %s"%(self.prnUnits), font=0)
            self._print(hdr, font=0)

    def _printResLine(self, idx):
        report = self.report
        res = report.getResult(idx)
        units = self.prnUnits
        Type = report.getType()
        if self.printer:
            if Type == "STD":
                std = TEMP_conv.C_to_units(res["REF"], units)
                unit = TEMP_conv.C_to_units(res["UNIT"], units)
                dev = TEMP_conv.C_to_units_dev(res["DEV"], units)
                self._print("%7.2f %7.2f %6.2f"%(std, unit, dev), font=0)

            elif Type == "CAL":
                std = TEMP_conv.C_to_units(res["REF"], units)
                unit = TEMP_conv.C_to_units(res["UUT"], units)
                dev = TEMP_conv.C_to_units_dev(res["DEV"], units)
                mark = res["MARK"]
                self._print("%7.2f %7.2f %6.2f %c"%(std, unit, dev, mark[0]), font=0)

##            elif report.getType() == "MEAS":
##                ref = res["REF"]
##                uut = res["UUT"]
##                dev = res["DEV"]
##                mark = ""#res["MARK"]
##                self.print("%7.2f %7.2f %6.2f %c"%(ref, uut, dev, mark[0]), font=0)
##    
##            else:
##                self.print("N.A.", font=0)

    def start(self, Type="DFLT") -> None:
        logger.info( "STARTING - %s"%(Type) )
        self.reset()
        super().start()

    def reset(self) -> None:
        logger.info( "RESET" )
        self.state.set(State.IDLE)
        self.soaking = False
        self.started = False

    def skip(self):
        self.soak_s = 1 #< This will end the SOAK state after 1 second
        self.state.set(State.SOAK)

    def sampleEveryCycle(self) -> None:
        return

    def idleState(self) -> bool:
        return True

    def setNewStepState(self) -> bool:
        return True

    def approachState(self) -> bool:
        return True

    def soakEnded(self) -> None:
        return

    def autoCooldown(self, targetC, thresC) -> bool:
        return True

    def fsmEnded(self) -> None:
        return

    def process(self) -> None:
        state = self.state
        self.sampleEveryCycle()

        if state.isState( State.IDLE ):
            logger.info( "IDLE" )
            if self.idleState():
                print(self.targetC)
                if self.targetC != None:
                    state.set( State.SETNEW )

        elif state.isState( State.SETNEW ):
            logger.info( "SETNEW" )
            if self.unit:
                self.unit.setDispToC()
            if self.setNewStepState():
                if self.program:
                    if self.program.free:
                        state.set( State.SOAK )
                    else:
                        state.set( State.APPROACH )
            else:
                state.set( State.COOLING )

        elif state.isState( State.APPROACH ):
            if self.targetC:
                logger.info( "APPROACH TO %1.2f C (UUT/REF AT %1.2f C)"%(self.targetC, self.uutT) )
            else:
                logger.info( "APPROACH TO N.A. (UUT/REF AT %1.2f C)"%(self.uutT) )

            if self.approachState():
                state.set( State.SOAK )

        elif state.isState( State.SOAK ):
            self.soakTime = self.stop_watch.getTime()
            if self.soak_s > 0:
                self.soakTimer = int( self.soak_s -self.soakTime )
                logger.info( "SOAK %d"%(self.soakTimer) )
                if self.soakTimer <= 0:
                    self.soakEnded()
                    state.set( State.SETNEW )
            else:
                logger.info( "SOAKING FOR %d sec"%(self.soakTime) )

        elif state.isState( State.COOLING ):
            logger.info( "AUTOMATIC COOL-DOWN" )
            if self.autoCooldown(35, 40):
                state.set( State.END )

        elif state.isState( State.END ):
            logger.info( "END" )
            if self.unit:
                self.unit.setOff()
            self.fsmEnded()
            state.set( State.MONITOR )

        elif state.isState( State.MONITOR ):
            logger.info( "MONITOR" )

        else:
            logger.info( "STATE-ERROR" )
 
    def getState(self) -> int:
        return self.State.get()

    def getStep(self) -> tuple:
        totalSteps = -1
        if self.program:
            totalSteps = len(self.program.seq)
        return (self.step +1, totalSteps)

    def isDone(self) -> bool:
        return self.state == State.END
