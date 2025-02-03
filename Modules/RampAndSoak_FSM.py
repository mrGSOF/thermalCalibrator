import logging, time, os
from Modules import ProgramFSM_base_Class as FSM
from Modules import Report_Class
from Modules import ITS_conversion as ITS

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger()

class RampAndSoak(FSM.Program_FSM):
    def __init__(self, unit=None, ref_uut=None, program=None, view=None):
        self.ref_uut = ref_uut
        self.path = ""
        self.reportFile = "%s/%s_temp.json"%(self.path,"RS")
        super().__init__(nameID="RampAndSoak_FSM", unit=unit, view=view)
        if program == None:
            program = FSM.Program()
        
        self.program = program
        self.reset(Type="MEAS")

    def _stableCntReset(self):
        self.stableCnt = 5

    def loadProg(self, filename) -> bool:
        return True

    def start(self, Type="CAL", path="") -> None:
        super().start(Type)
        self.path = path
        self.reportFile = "%s/%s_temp.json"%(path,Type)
        self.targetC = 25.0
        self.reset(Type)
        self._printReportHeader()
    
    def reset(self, Type="CAL") -> None:
        super().reset()
        self.Type = Type
        self.unitT = 0.0
        self.uutT = 0.0
        self.ambT = 0.0
        self.step = 0
        self._stableCntReset()
        self.report = None
        self.passThres = None #< Will not add the Pass / Fail value to the result
        if self.unit:
            if Type == "CAL":
                self.report = Report_Class.Report(Type = Type,
                                     units = self.units,
                                     date = Report_Class.getDate(),
                                     unit = self.unit.details,
                                     dmm = self.ref_uut.comm.details,
                                     uut = self.unit.details,
                                     ref = self.ref_uut.details,
                                     filename = self.reportFile
                                     )
            else:
                self.report = Report_Class.Report(Type = Type,
                                     units = self.units,
                                     date = Report_Class.getDate(),
                                     unit = self.unit.details,
                                     dmm = self.ref_uut.comm.details,
                                     uut = self.ref_uut.details,
                                     ref = self.unit.details,
                                     filename = self.reportFile
                                     )

    def skip(self):
        self.soak_s = 1
        self.state.set(self.state.SOAK)
        
    def sampleEveryCycle(self) -> None:
        if self.ref_uut:
            self.uutT = self.ref_uut.measTemp()
        else:
            self.uutT = None

        if self.unit:
            self.targetC = self.unit.getTctrl() #< The target temp
            time.sleep(0.2)
            self.unitT = self.unit.measTwell()
            time.sleep(0.2)
            self.ambT = self.unit.measTamb()

        if self.view:
            self.view(Tctrl=self.targetC, Tunit=self.unitT, Tuut=self.uutT,
                      soak=self.soakTimer, state=self.state.getStateText())

    def idleState(self) -> bool:
        """ Will return True to continue to next step """
        if self.program != None:
            logger.info( "DETECTED PROG <%s>"%(self.program.name) )
            if len(self.program.seq) > 0:
                logger.info( "STARTING <%s>"%(self.program.name) )
                if self.unit:
                    #self.unit.setDispUnits(self.units)
                    self.unit.setOn()
                    coef = self.unit.getITS68()
                    amb = None
                    if len(coef) > 3:
                        amb = coef[3]
                    self.report.refresh( date = Report_Class.getDate(),
                                  its = ITS.ITS_to_DICT( 68, coef, amb=amb, tc=None ))
                return True
        return False
    
    def setNewStepState(self) -> bool:
        """ Will return True to continue to next step """
        self._stableCntReset()                
        if self.step < len(self.program.seq):                     #< Gather step information
            self.rateC_s = self.program.seq[self.step]["RATE"]    #< C per second
            self.soak_s = self.program.seq[self.step]["SOAK"]*60  #< Convert soak time from miniutes to seconds
            self.targetC = self.program.seq[self.step]["TARGET"]  #< C
            if "PASS_THRES" in self.program.seq[self.step]:       #< Check for the Paas/Fail threshold value
                self.passThres = abs(self.program.seq[self.step]["PASS_THRES"])
            else:
                self.passThres = None #< Will not add the Pass / Fail value to the result
                    
            if self.unit:
                self.unit.setTctrl( self.targetC )
            self.stop_watch.reset()
            return True
        return False

    def approachState(self) -> bool:
        """ Will return True to continue to next step """
        if self.unit:
            #self.targetC = self.unit.getTctrl() #< The target temp
            if self.unit.isStable():
                self.stableCnt -= 1
                if self.stableCnt <= 0:
                    self.stop_watch.reset()
                    return True
            else:
                self._stableCntReset()                
        else:
            return True
        return False

    def soakEnded(self) -> None:
        retry = 5
        while ( (self.unitT == None) or (self.uutT == None) or (self.ambT == None) ) and (retry > 0):
            logger.warning( " Unit or DMM communication error (about in %d attempts)"%retry )
            self.sampleEveryCycle()
            retry -= 1
            time.sleep(0.5)
            
        if self.Type == "CAL":
            self.report.addResultCal( self.unitT, self.uutT, 'C', self.soak_s/60.0, self.passThres, self.ambT)
        else:
            if self.program.free:
                self.report.addResultFree(self.unitT, self.targetC, 'C', self.soak_s/60.0, self.passThres, self.ambT)
            else:
                self.report.addResultMeas(self.unitT, self.uutT, 'C', self.soak_s/60.0, self.passThres, self.ambT)
        self.report.save()
        self._printResLine(-1)
        self.soak = -1
        self.soakTimer = -1
        self.step += 1

    def autoCooldown(self, targetC, thresC) -> bool:
        """  """
        if self.unit:
            self.targetC = targetC
            self.unit.setTctrl( self.targetC )
            if self.unitT > thresC:
                return False #< Not cold enough yet
        return True          #< Cold enough or unit not connected

    def finalizeReport(self):
        self._print("")             #< Advance paper to show last line 
        self._print("")
        report = self.report
        report.refresh()            #< To update the average ambient temperature
        filename = "%s_%s_%s_%s.json"%(self.Type,
                                       report.getUnitModel(),
                                       report.getUnitID(),
                                       report.getDate())
        
        self.reportFile = os.path.join(self.path, filename)
        report.save(self.reportFile, overWrite=False) #< Rename the file if already exists
        report.delete()

    def fsmEnded(self) -> None:
        self.finalizeReport()

if  __name__ == "__main__":
    program = Program(name="Test")
    program.addStep(rate=1.2, targetC=35, soak_m=0.1)
    program.addStep(rate=1.2, targetC=45, soak_m=0.1)
    program.addStep(rate=1.2, targetC=55, soak_m=0.1)
    
    p = RampAndSoak(program=program)
