from Modules import KNC360x_base
from Modules import KNC3604U_scpi_api as SCPI
from Modules import KNC360x_knc_api as KNC
from Modules import TEMP_conv as CONV


class KNC3604U(KNC360x_base.KNC360x, SCPI.SCPI_api, KNC.Legacy_base_api):
    def startStd68(self, std, soak, units):
        seq = (95, 315, 535)           #< Standardization points in (C)
        self.std.setSequence(seq, soak, units)

    def startStd90(self, std, soak, units):
        seq = (80, 320, 560)           #< Standardization points in (C)
        self.std.setSequence(seq, soak, units)

##    def startCal(self, ref, soak, units, quick=False):
##        if units == 'C':
##            dT = 50
##            if quick:
##                dT *= 2
##            seq = list(range(50,650,dT))           #< Calibration points in (C)
##
##        elif units == 'F':
##            dT = 100
##            if quick:
##                dT *= 2
##            seq = list(range(100,1200,dT)) +[1150] #< Calibration points in (F)
##            seq = [ CONV.degF_to_degC(F) for F in seq]
##            
##        else:
##            print("Wrong units - only {C,F}")
##            return
##            
##        self.cal.setSequence(seq, soak, units)
