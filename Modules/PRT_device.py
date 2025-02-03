from . import ITS68, ITS90, TEMP_conv

class PRT_dev():
    def __init__( self, comm, its, details={} ):
        self.comm = comm
        self.its = its
        self.details = details
        self.ohm = -1
        self.degC = -999
        print("""
PRT device:\n\
Name - %s\n\
Serial# - %s\n\
Type %s\n\
Connection - %s\n"""%
                  (details["MODEL"],
                  details["SN"],
                  str(type(its)),
                  str(type(comm))))

        if its == None:
            raise ValueError("Missing ITS coefficients")

        if comm == None:
            raise IOError("Missing DMM object")
#        else:
#            self.open()

    def init( self ):
        if self.comm != None:
            self.comm.Res4wireCfg()

    def open(self):
        if self.comm != None:
            self.comm.open()
            self.init()
        
    def close(self):
        if self.comm != None:
            self.comm.close()

    def isConnected(self):
        if self.comm != None:
            return self.comm.isConnected()
        return False

    def getRes( self ):
        return self.ohm

    def measRes( self ):
        if self.isConnected():
            return self.comm.Sample()
        return 0

    def measTemp( self, units='C', ohm=None ):
        if ohm == None:
            ohm = self.measRes()
        self.ohm = ohm

        if ohm > 10:
            #print("OK")
            self.degC = self.its.T(ohm)
        else:
            print("BAD PRT CONNECTION")
            self.degC = -999
        return self.getTemp(units)

    def getTemp( self, units='C' ):
        return TEMP_conv.C_to_units(self.degC, units)

if __name__ == '__main__':
    class dummyDmm():
        def open(self):
            print("Dummy DMM port is open")
            
        def close(self):
            print("Dummy DMM port is closed")

        def Res4wireCfg(self):
            print("Dummy DMM in 4-wire mode")

        def Sample(self):
            print("Dummy DMM sampler (220 ohm)")
            return 220.0

    try:
        prt = PRT_dev(comm=dummyDmm(),
                       its=ITS68.ITS68({"R0":200, "Alpha":0.00363, "Delta":1.5}),
                       name="SPRT#1",
                       sn="A1048")
        print("*** PRT device is ready")
    except IOError as e:
        print("*** IOError exception detected")

    try:
        prt1 = PRT_dev(comm=None,
                       its=ITS68.ITS68({"R0":200, "Alpha":0.00363, "Delta":1.5}),
                       name="SPRT#1",
                       sn="A1048")
    except IOError as e:
        print("IOError exception detected")

    try:
        prt2 = PRT_dev(comm=None,
                       its=None,
                       name="SPRT#1",
                       sn="A1048")
    except ValueError as e:
        print("*** ValueError exception detected")
