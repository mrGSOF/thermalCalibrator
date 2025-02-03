import logging, time
from Modules import threadBasic
from Modules import ProgramFSM_base_Class as FSM
from Modules import StopWatch_Class

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger()

class State():
    IDLE = 0
    STD_RUN = 1
    COOL = 2
    COOL_END = 3
    CAL_RUN = 4
    CAL_END = 5
    OFF = 6

    def __init__(self):
        self.state = self.OFF

    def isState(self, state) -> bool:
        return self.state == state

    def set(self, state) -> None:
        self.state = state
        
    def get(self) -> int:
        return self.state

    def getStateText(self) -> str:
        if self.isState(self.IDLE):
            return "IDLE"
        elif self.isState(self.STD_RUN):
            return "STD RUNNING"
        elif self.isState(self.COOL):
            return "COOLING"
        elif self.isState(self.COOL_END):
            return "STARTING CAL"
        elif self.isState(self.CAL_RUN):
            return "CAL RUNNING"
        elif self.isState(self.CAL_END):
            return "CAL ENDED"
        elif self.isState(self.OFF):
            return "OFF"
        else:
            return "INVALIDE STATE"


class Manager(threadBasic.BasicThread):
    def __init__(self, stn, stdPath="./", calPath="./"):
        super().__init__("StdCalAuto", Period=2.0)
        self.stn = stn           #< The STATION object
        self.stdPath = stdPath   #< The path for the STD report
        self.calPath = calPath   #< The path for the CAL report
        self.stop_watch = StopWatch_Class.StopWatch()
        self.state = State()

    def start(self, stdPath=None, calPath=None):
        if stdPath:
            self.stdPath = stdPath   #< The path for the STD report

        if calPath:
            self.calPath = calPath   #< The path for the CAL report

        self.state.set(State.IDLE)
        super().start()

    def process(self) -> None:
        #print( "%s: %s"%(self.name, self.state.getStateText()) )
        
        if self.state.isState(State.IDLE):
            self.stn.startStd(self.stdPath)     #< Start the STD FSM
            self.enable = True
            self.state.set(State.STD_RUN)
            
        elif self.state.isState(State.STD_RUN):
            if not self.stn.isStdRunning():
                self.stop_watch.reset()
                self.state.set(State.COOL)

        elif self.state.isState(State.COOL):
            print( self.stop_watch.getTime() )
            if self.stop_watch.getTime() > 2.5*60:
                self.stn.std.pause()            #< Pause the STD FSM
                self.state.set(State.COOL_END)

        elif self.state.isState(State.COOL_END):
            self.stn.startCal(self.calPath)     #< Start the CAL FSM
            self.enable = True
            self.state.set(State.CAL_RUN)

        elif self.state.isState(State.CAL_RUN):
            if not self.stn.isCalRunning():
                #self.stn.rs.pause()            #< Keep the procedure running for monitor
                self.state.set(State.CAL_END)

        elif self.state.isState(State.CAL_END):
            self.state.set(State.OFF)

        elif self.state.isState(State.OFF):
            self.pause()                        #< Pause the AUTO-STD-CAL FSM

        else:
            print("%s: INVALIDE STATE"%(self.name))
            self.state.set(State.OFF)
