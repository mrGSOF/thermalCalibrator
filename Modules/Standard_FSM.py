import logging, time, os
from Modules import ProgramFSM_base_Class as FSM
from Modules import Report_Class
from Modules import ITS_conversion as ITS

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger()

class Standardization(FSM.Program_FSM):
    def __init__(self, unit=None, sprt=None, soak=None, view=None):
        self.sprt = sprt
        self.path = ""
        self.reportFile = "%s/%s_temp.json"%(self.path,"RS")
        super().__init__(nameID="Std_FSM", unit=unit, view=view)
        self.program = FSM.Program(path="", name="Standardisation", seq=[], auto=1, free=0, cycles=1)
        self.soak = soak*60.0 #< The FSM measures seconds
        self.soak_s = self.soak
        self.reset()

    def start(self, Type="STD", path="") -> None:
        self.path = path
        self.reportFile = "%s/%s_temp.json"%(path,Type)
        super().start(Type)
        #self.Period = 2.0
        self._printReportHeader()
        
    def skip(self):
        logger.info( "STD: SKIP (ADV) TO NEXT POINT" )
        self.soak_s = 1
        self.state.set(self.state.SOAK)
        #print("Skip is N.A. during STD")

    def reset(self) -> None:
        super().reset()
        self.Type = "STD"
        self.unitT = 0.0
        self.unitR = 0.0
        self.sprtT = 0.0
        self.ambT = 0.0
        self.step = 0
        self.steps = 3 #< Three steps for any standardization
        self.report = None
        if self.unit:
            self.report = Report_Class.Report(Type = self.Type,
                                 units = self.units,
                                 date = Report_Class.getDate(),
                                 unit = self.unit.details,
                                 dmm = self.sprt.comm.details,
                                 uut = self.unit.details,
                                 ref = self.sprt.details,
                                 filename = self.reportFile
                                 )

    def sampleEveryCycle(self) -> None:
        #self.sprtT = None
        #self.uutT = None
        if self.sprt:
            self.sprtT = self.sprt.measTemp()
            self.uutT = self.sprtT  #< For the base class

        if self.unit:
            self.targetC = self.unit.getTctrl() #< The unit desides on the target temp
            time.sleep(0.1)
            self.unitT = self.unit.measTwell()
            time.sleep(0.1)
            self.unitR = self.unit.measRwell()
            time.sleep(0.1)
            self.ambT = self.unit.measTamb()

        if self.view:
            self.view(Tctrl=self.targetC, Tunit=self.unitT, Tuut=self.uutT,
                      soak=self.soakTimer, state=self.state.getStateText())

    def idleState(self) -> bool:
        """ Will return True to continue to next step """
        if self.step == 0:
            if self.unit:
                self.unit.setStdMode() #< Will also turn on the power
                self.unit.setOn()
                #self.unit.setDispUnits(self.units)
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
        mode, self.step = self.unit.getMode()
        logger.info( "STD: SETNEW <%s>, Idx:%d"%(mode, self.step) )
        self.soak_s = self.soak

        if mode == "Idle": #self.step < self.steps:
            return False
        else:
            if self.unit:
                self.targetC = self.unit.getTctrl() #< The unit desides on the target temp
            self.stop_watch.reset()
            return True

    def approachState(self) -> bool:
        """ Will return True to continue to next step """
        if self.unit:
            if self.unit.isStable():
                self.stop_watch.reset()
                return True
        else:
            return True
        return False

    def soakEnded(self) -> None:
        retry = 5
        while ( (self.unitT == None) or (self.unitR == None) or (self.sprtT == None) or (self.ambT == None) ) and (retry > 0):
            logger.warning( " Unit or DMM communication error (about in %d attempts)"%retry )
            self.sampleEveryCycle()
            retry -= 1
            time.sleep(0.5)

        self.report.addResultStd( self.unitT, self.unitR, self.sprtT, 'C', self.soak_s/60.0, self.ambT)
        self.report.save()
        self._printResLine(-1)
        self.unit.setDispToC()           #< Make sure we are in C units
        self.unit.setRefMeas(self.sprtT) #< Todo: Convert the T units
        time.sleep(0.5)
        if self.step >= 2:
            logger.info( "STD: END OF SEQUENCE" )
##            if self.prnUnits == 'F':
##                logger.info( "STD: CHANGE DISP TO (F)" )
##                self.unit.setDispToF()     #< Print in the correct units
##                time.sleep(0.5)
            logger.info( "STD: CALCULATE AND PRINT COEF'" )
            time.sleep(2.0)
            self.unit.advPoint()
            time.sleep(15)                 #< Wait for unit's printer to finish
            logger.info( "STD: CHANGE DISP TO (C)" )
##            self.unit.setDispToC()         #< Back to C units
            logger.info( "STD: LINE FEED" )
            self._print("")                #< Advance the paper to show the last line
            logger.info( "STD: LINE FEED" )
            self._print("")
            self.finalizeReport()
        else:
            self.unit.advPoint()
        self.soakTimer = -1                #< Important for proper status display

    def autoCooldown(self, targetC, thresC) -> bool:
        """  """
        if self.unit:
            self.targetC = targetC
            self.unit.setTctrl( self.targetC )
            if self.unitT > thresC:
                return False #< Not cold enough yet
        return True          #< Cold enough or unit not connected

    def finalizeReport(self):
        coef = self.unit.getITS68()
        logger.info( "STD: NEW COEF: %s"%str(coef) )
        amb = None
        if len(coef) > 3:
            amb = coef[3]
        
        report = self.report
        report.refresh( newIts = ITS.ITS_to_DICT( 68, coef, amb=amb, tc=None ))
        filename = "%s_%s_%s_%s.json"%(self.Type,
                                       report.getUnitModel(),
                                       report.getUnitID(),
                                       report.getDate())
        
        self.reportFile = os.path.join(self.path, filename)
        report.save(self.reportFile, overWrite=False) #< Rename the file if exists
        report.delete()

    def fsmEnded(self) -> None:
        logger.info( "STD: ENDDED" )

if  __name__ == "__main__":
    p = Standardization(soak=0.1)
