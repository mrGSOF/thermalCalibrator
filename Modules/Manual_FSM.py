import logging, time
from Modules import ProgramFSM_base_Class as FSM
from Modules import Report_Class
from Modules import ITS_conversion as ITS

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger()

class Manual(FSM.Program_FSM):
    """ MONITOR THE UNIT AND UUT/SPRT """
    def __init__(self, unit=None, uut=None, units='C', view=None):
        self.uut = uut
        super().__init__(nameID="Manual_FSM", unit=unit, view=view)
        self.reset()

    def start(self, Type="MAN", path="") -> None:
        self.path = path
        self.reportFile = "%s/%s_temp.json"%(path,Type)
        super().start()
        if self.unit:
            #self.unit.setDispUnits(self.units)
            coef = self.unit.getITS68()
            amb = None
            if len(coef) > 3:
                amb = coef[3]
            self.report.refresh( date = Report_Class.getDate(),
                          its = ITS.ITS_to_DICT( 68, coef, amb=amb, tc=None ))

    def reset(self) -> None:
        super().reset()
        self.Type = "MEAS"
        self.targetC = None
        self.unitT = 0.0
        self.unitR = 0.0
        self.uutT = 0.0
        self.ambT = 0.0
        self.report = None
        if self.unit:
            self.report = Report_Class.Report(Type = self.Type,
                                 units = self.units,
                                 date = Report_Class.getDate(),
                                 unit = self.unit.details,
                                 dmm = self.uut.comm.details,
                                 uut = self.unit.details,
                                 ref = self.uut.details
                                 )
        
    def monitor(self) -> None:
        self.poweroff()

    def poweroff(self) -> None:
        if self.unit:
            self.unit.setOff()

    def poweron(self) -> bool:
        if self.unit:
            self.unit.setOn()
            return True
        return False
    
    def setTarget(self, targetC) -> bool:
        self.targetC = targetC
        self.state.set( FSM.State.SETNEW )
        return True

    def measure(self, val=None) -> None:
        if val == None:
            val = self.uutT
        self.report.addResultStd( self.unitT, self.unitR, val, 'C', self.soak_s/60.0, self.ambT)
    
    def sampleEveryCycle(self) -> None:
        if self.uut:
            self.uutT = self.uut.measTemp()
            time.sleep(0.1)
        else:
            self.uutT = None

        if self.unit:
            targetC = self.unit.getTctrl() #< The target temp
            time.sleep(0.1)
            self.unitT = self.unit.measTwell()
            time.sleep(0.1)
            self.unitR = self.unit.measRwell()
            time.sleep(0.1)
            self.ambT = self.unit.measTamb()

        if self.view:
            self.view(Tctrl=targetC,
                      Tunit=self.unitT,
                      Tuut=self.uutT,
                      soak=self.soakTime,
                      state=self.state.getStateText()
                      )

    def idleState(self) -> bool:
        """ Will return True to continue to next step """
        return True

    def setNewStepState(self) -> bool:
        """ Will return True to continue to next step """
        if self.unit:
            if self.targetC:
                self.poweron()
                self.unit.setTctrl( self.targetC )
        self.stop_watch.reset()
        self.soakTime = -1
        return True

    def approachState(self) -> bool:
        """ Will return True to continue to next step """
        if self.unit:
            self.targetC = self.unit.getTctrl() #< The target temp
            if self.unit.isStable():
                self.stop_watch.reset()
                return True
        else:
            return True
        return False

    def fsmEnded(self):
        self.poweroff()

if  __name__ == "__main__":
    p = Manual()
