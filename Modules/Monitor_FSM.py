import logging, time
from Modules import ProgramFSM_base_Class as FSM

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger()

class Monitor(FSM.Program_FSM):
    """ MONITOR THE UUT/SPRT ONLY """
    def __init__(self, uut=None, units='C', view=None):
        self.uut = uut
        super().__init__(nameID="Monitor_FSM", view=view)
        self.reset()

    def start(self, Type="MON", path="") -> None:
        self.path = path
        self.reportFile = "%s/%s_temp.json"%(path,Type)
        super().start(Type)

    def reset(self) -> None:
        super().reset()
        self.Type = "MON"
        self.uutT = 0.0
        self.report = None

    def monitor(self) -> None:
        return

    def poweroff(self) -> None:
        return

    def poweron(self) -> bool:
        return False
    
    def setTarget(self, targetC) -> bool:
        return True

    def sampleEveryCycle(self) -> None:
        if self.uut:
            time.sleep(0.1)
            self.uutT = self.uut.measTemp()
            if self.view:
                self.view(Tctrl=-999, Tunit=-999, Tuut=self.uutT, state="SPRT MONITOR")

    def idleState(self) -> bool:
        """ Will return True to continue to next step """
        return True

    def setNewStepState(self) -> bool:
        """ Will return True to continue to next step """
        return True

    def approachState(self) -> bool:
        """ Will return True to continue to next step """
        return False

if  __name__ == "__main__":
    p = Monitor()
