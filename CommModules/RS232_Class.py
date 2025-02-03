import serial
from . import COMM_base

class SERIAL(COMM_base.COMM_base):
    def __init__(self, coef={"COM":1, "BAUD":9600}, writeCallback=None, readCallback=None):
        COMM_base.COMM_base.__init__(self, None, writeCallback, readCallback)
        self.baud = coef["BAUD"]
        self.com = coef["COM"]
        self.dev = None
        #self.open()

    def _write(self, s):
        if self.dev:
            s = f"{s}\r\n"
            s = s.encode('utf-8')
            self.dev.flushInput()
            COMM_base.COMM_base._write(self, s)

    def _readline(self):
        res = b""
        if self.dev:
            res = self.dev.readline().decode('utf-8').strip()
            if self.readCallback:
                self.readCallback(res)
        return res

    def open(self):
        if self.dev == None:
            try:
                self.dev = serial.Serial(self.com, baudrate=self.baud, timeout=7.0)
                print( "%s connected"%( self.com) )
            except serial.serialutil.SerialException as e:
                self.dev = None

    def disconnect(self):
        if self.dev != None:
            self.dev.close()
            print( "%s disconnected"%( self.com) )
