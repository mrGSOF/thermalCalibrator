from Modules import KNC360x_base
from Modules import KNC360x_knc_ext_api as KNC
from Modules import TEMP_conv as CONV

class KNC3605A(KNC360x_base.KNC360x, KNC.Legacy_ext_api):
    ...
##    def startStd68(self, std, soak, units):
##        seq = (95, 315, 535)                               #< Standardization points in (C)
##        self.std.setSequence(seq, soak, units)
##
##    def startStd90(self, std, soak, units):
##        seq = (80, 320, 560)                               #< Standardization points in (C)
##        self.std.setSequence(seq, soak, units)

##    def startCal(self, ref, soak, units, quick=False):
##        if units == 'C':
##            if quick:
##                seq = (-20, 25, 70, 120)                   #< Calibration points in (C)
##            else:
##                seq = (-20, 0, 40, 60, 80, 100, 120)       #< Calibration points in (C)
##
##        elif units == 'F':
##            if quick:
##                seq = range(-20, 50, 150, 250)             #< Calibration points in (F)
##            else:
##                seq = range(-20,0,50,100,150,200,250)      #< Calibration points in (F)
##            seq = [ CONV.degF_to_degC(F) for F in seq]     #< Recalculate to (C)
##
##        else:
##            print( "Wrong units - only {C,F}" )
##            return
##
##        self.cal.setSequence(seq, soak, units)
