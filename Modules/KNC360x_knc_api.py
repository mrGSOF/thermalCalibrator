#!/usr/bin/env python

class Legacy_base_api():

    ### LEGACY COMMANDS
    def setStdMode(self):
        self.comm._write( "MS" )

    def setCalMode(self):
        self.comm._write( "MC" )

    def getStdStatus(self):
        return self.comm._queryString( "MCP?" )

    def measTamb(self):
        return self.comm._queryFloat( "MEA:TAMB" )

    def advPoint(self):
        self.comm._write( "MA" )

    def setRefMeas(self, ref):
        self.comm._write( "MM%8.3f"%(ref) )

    def setDispUnits(self, units):
        if units[0] == 'C':
            self.setDispToC()
        elif units[0] == 'F':
            self.setDispToF()
        else:
            print( "Wrong units <%s> use {C or F}"%(units) )

    def getMode(self):
        retry = 2
        while retry:
            try:
                rsp = self.getStdStatus()
                print(rsp)
                rsp = rsp.split(',')
                mode = rsp[0]
                print(mode)
                idx = int(rsp[1].split(':')[1])
                print(idx)
                return (mode, idx)
            except:
                retry -= 1
        return ("NA", None)

    def setDispToF(self):
        self.comm._write( "MU1" )

    def setDispToC(self):
        self.comm._write( "MU2" )

    def setOn(self):
        self.comm._write( "MR" )

    def setOff(self):
        self.comm._write( "MD" )

    def print_(self, value, disp=True):
        self.comm._write( "MP%s"%(value) )

    def read(self):
        return self.comm._readline()
