class HP34401():
    FlukeCmd = { 'AAC' : 'F6',
                 'ADC' : 'F5',
                 'Res4Wire' : 'F4',
                 'Res2Wire' : 'F3',
                 'VAC' : 'F2',
                 'VDC' : 'F1',
                 'Sample' : '?',
                 'Reset' : '*',
                 'ID' : 'G8',
                 }

    SCPICmd = { 'AAC' : 'CONF:CUR:AC',
                 'ADC' : 'CONF:VOLT:DC',
                 'Res4Wire' : 'CONF:FRES',
                 'Res2Wire' : 'CONF:RES',
                 'VAC' : 'CONF:VOLT:AC',
                 'VDC' : 'CONF:VOLT:DC',
                 'Sample' : 'READ?',
                 'Reset' : '*RST',
                 'ID' : '*IDN?',
                 }

    def __init__( self, comm, lang="Fluke", details={} ):
        self.comm = comm
        self.details = details
        self.Cmd = self.FlukeCmd
        if lang == 'SCPI':
            self.Cmd = self.SCPICmd

    def open(self):
        if self.comm != None:
            self.comm.open()
        
    def close(self):
        if self.comm != None:
            self.comm.disconnect()

    def isConnected(self):
        return self.comm.isConnected()

    def Reset(self):
        if self.comm != None:
            self.comm._write( self.Cmd['Reset'] )

    def GetId(self):
        if self.comm != None:
            res = self.comm._queryString( self.Cmd['ID'] )
            return str(res)

    def Sample(self):
        if self.comm != None:
            return self.comm._queryFloat( self.Cmd['Sample'] )

    def VoltDcCfg(self):
        if self.comm != None:
            self.comm._write( self.Cmd['VDC'] )

    def CurDcCfg(self):
        if self.comm != None:
            self.comm._write( self.Cmd['ADC'] )

    def Res4wireCfg(self):
        if self.comm != None:
            self.comm._write( self.Cmd['Res4Wire'] )

    def Res2wireCfg(self):
        if self.comm != None:
            self.comm._write( self.Cmd['Res2Wire'] )
