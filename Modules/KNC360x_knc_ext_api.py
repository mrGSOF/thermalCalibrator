#!/usr/bin/env python
import time
from CommModules import COMM_base

class Legacy_ext_api():

    def reset(self):
        self.DEV.write( "*RST" )

    def getId(self):
        return self.comm._queryString( "*IDN?" )

    def setPrnEn(self, en=True):
        cmd = "PRN0"
        if en == True:
            cmd = "PRN1"
        self.comm._write( cmd )

    def beep(self):
        self.comm._write( "BEEP" )

    def setToITS90(self):
        self.comm._write( "ITS90" )

    def setToITS68(self):
        self.comm._write( "ITS68" )

    def back(self):
        self.comm._write( "*ESC" )

    def measBwell(self):
        return self.comm._queryFloat( "MEA:BWEL" )

    def measRwell(self):
        return self.comm._queryFloat( "MEA:RWEL" )
    
    def measTwell(self):
        retry = 3
        while retry > 0:
            res =  self.comm._queryFloat( "MEA:TWEL" )
            if res != None:
                return res
            retry -= 1
        return None

    def measBamb(self):
        return self.comm._queryFloat( "MEA:BAMB" )

    def measRamb(self):
        return self.comm._queryFloat( "MEA:RAMB" )
    
    def measTamb(self):
        return self.comm._queryFloat( "MEA:TAMB" )

    def getITS(self):
        return self.comm._queryString( "ITS?" )

    def measTwell_NoFilter(self):
        return self.comm._queryFloat( "MEA:TWEL_NOFLT" )

    def getTctrl(self):
        return self.comm._queryFloat( "MEA:TTRG" )

    def setRate(self, minRate, maxRate, units="CPM" ):
        return

    def getITS68(self):
        retry = 5
        while retry > 0:
            retry -= 1
            res = self.comm._queryString( "ITS68_C?" )
            res = res.replace('\x00',' ')
            print("------\n%s\n------"%res)
            res = res.split((":"))[-1].split(',')
            a = []
            for s in res:
                a.append( COMM_base.try_parse_float(s) )

            if len(a) >= 3:
                retry = 0
            else:
                time.sleep(0.5)
        return a

    def getITS90(self):
        coef =  self.comm._queryString( "ITS68_C0?" )
        coef += self.comm._queryString( "ITS68_C1?" )
        return coef

    def getStdStatus(self):
        return self.comm._queryString( "MCP?" )

    def setTctrl(self, value):
        self.comm._write( "MT%8.3f"%(value) )

    def isOn(self):
        return self.comm._queryFloat( "PID?" )

    def setStdMode(self):
        self.comm._write( "MS" )

    def setCalMode(self):
        self.comm._write( "MC" )

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
                #print(rsp)
                rsp = rsp.split(',')
                mode = rsp[0]
                #print(mode)
                idx = int(rsp[1].split(':')[1])
                #print(idx)
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

    def printLine(self, value, font=0):
        self.comm._write( "MP%s"%(value) )

    def printSkipLine(self, font=0):
        self.printLine(" ", font)

    def isStable(self):
        sts = self.read()
        return ord(sts[0])&1

    def read(self):
        return self.comm._readline()
