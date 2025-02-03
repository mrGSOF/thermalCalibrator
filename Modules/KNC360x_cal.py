import threading

class KNC360x_cal_base(threading.Thread):
    def __init__(self, unit, prt, seq, soak, units='C'):
        self.unit = unit
        self.prt = prt
        self.units = units
        self.setSequence( seq, soak )
        super().__init__(self)
        
    def setSequence(self, seq, soak):
        self.seq = seq
        self.soak = soak
        
#    def start(self):
#        super().__init__(self)

        
    def run(self):
        self.unit.knc.print("** CALIBRATION **")
#        self.unit.knc.setCalMode()

        for pt in self.seq
        calibrating = True
        while (calibrating)
        
