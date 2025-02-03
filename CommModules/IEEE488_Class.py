import pyvisa as visa
from . import COMM_base

class IEEE488(COMM_base.COMM_base):
    def __init__(self,
                 visa=False, coef={"ADDR":"GPIB0::6::INSTR"},
                 writeCallback=None, readCallback=None):
        self.visa = visa
        self.ad = coef["ADDR"]
        self.writeCallback = writeCallback
        self.readCallback = readCallback
        self.dev = None

    def _readline(self):
        res = b""
        if self.dev:
            res = self.dev.read().strip("\x00")
            if self.readCallback:
                self.readCallback(res)
        return res

    def open(self, rm=None, ad=None):
        if rm != None:
            self.visa = rm
        if ad != None:
            self.ad = ad

        if self.ad != None:
            if self.ad != "":
                try:
                    self.dev = self.visa.open_resource(self.ad)
                    print( "%s connected"%(self.ad) )
                    return True
                except visa.VisaIOError as e:
                    print(e.args)
                    return None
        self.dev = None
        return None

    def isConnected(self):
        if self.dev:
            return self.dev.last_status != visa.constants.StatusCode.error_no_listeners
        return False
    
    def disconnect(self):
        if self.isConnected():
            self.dev.close()
        print( "%s disconnected"%(self.ad) )
