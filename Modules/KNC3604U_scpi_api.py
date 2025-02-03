
class SCPI_api():
    ### SCPI-STYLE COMMANDS
    def beep(self):
        self.comm._write( "SYSTem:BEEPer" )

    def reset(self):
        self.comm._write( "SYSTem:UNIT:RESET" )

    def abort(self):
        self.comm._write( "ABORt" )

    def getId(self):
        return self.comm._queryString("*IDN?")

    def getVer(self):
        return self.comm._queryFloat("SYSTem:VERSion?")

    def measRwell(self, units = "R"):
        return self.comm._queryFloat("SOUR:SENS:RES? 1%s"%units)
    
    def measTwell(self, units="CEL"):
        return self.comm._queryFloat("SOUR:SENS:TEMP? 1%s"%units)

    def getTctrl(self, units="CEL"):
        return self.comm._queryFloat("UNIT:TEMP? 1%s"%units)

    def isStable(self):
        sts = self.comm._queryString("")
        return 0x1&ord(sts[0])
        #return int(self.comm._queryFloat("SOUR:STAB:TEST?")) #< Does not work FW bug

    def isSwClosed(self):
        return int(self.comm._queryFloat("INP:SWIT:CLOS?"))

    def measRMU(self, units="R"):
        return self.comm._queryFloat("MEAS:DMM? 1%s"%units)

    def getUUT(self, units="CEL"):
        return self.comm._queryFloat("MEAS:UUT? 1%s"%units)

    def getITS(self):
        return self.comm._queryFloat("CONFigure?")

    def isOn(self):
        return self.comm._queryFloat("OUTput:STATE?")

    def getITS68(self):
        return self.comm._queryArray("CONF:TEMP:ITS27:C0?")

    def setITS68(self, R0, Alpha, Delta, degC):
        self.comm._write( "CONF:TEMP:ITS27:C0 (%1.6f,%1.6f,%1.6f,%1.1f)"%(R0,Alpha,Delta,degC) )
        
    def getITS90(self):
        coef =  self.comm._queryArray("CONF:TEMP:ITS90:C0?")
        coef += self.comm._queryArray("CONF:TEMP:ITS90:C1?")
        return coef
            
    def setITS90(self, R0, RTPW, a4, b4, a7, b7, c7, degC):
        self.comm._write( "CONF:TEMP:ITS90:C0 (%1.6f,%1.6f,%1.6f)"%(RTPW,a4,b4) )
        self.comm._write( "CONF:TEMP:ITS90:C1 (%1.6f,%1.6f,%1.6f,%1.1f)"%(a7,b7,c7,degC) )

    def setTctrl(self, value, units="CEL"):
        self.comm._write( "UNIT:TEMP %1.2f %s"%(value, units) )

    def setRate(self, minRate, maxRate, units="CPM" ):
        self.comm._write( "SOUR:RATE %1.2f %s, %1.2f %s"%(minRate, units, maxRate, units) )

    def _setState(self, s):
        self.comm._write( "OUTput:STATE %s"%(s) )

    def setState(self, s):
        if s:
            self.SetOn()
        else:
            self.SetOff()

    def setOn(self):
        self._setState(1)

    def setOff(self):
        self._setState(0)

    def dispCLS(self, text):
        self._write( "DISP:CLE" )

    def dispLine(self, text):
        self.comm._write( 'DISP:TEXT "%s"'%(text) )

    def dispAt(self, loc, text):
        self.comm._write( 'DISP:AT %d,"%s"'%(loc,text) )
        
    def printLine(self, text, font=0):
        self.comm._write( 'PRIN:TEXT "%s",%d'%(text, font) )

    def printSkipLine(self, font=0):
        self.printLine("", font)
