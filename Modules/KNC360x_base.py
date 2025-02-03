
class KNC360x():
    def __init__(self, comm=None, details={}):
        self.comm = comm
        self.details = details

    def open(self) -> None:
        if self.comm != None:
            self.comm.open()
            self.getId()
            #self.beep()
            #self.init()
        
    def close(self) -> None:
        if self.comm != None:
            self.comm.disconnect()

    def isConnected(self) -> bool:
        return self.comm.isConnected()

#    def setDispUnits(self, units) -> None:
#        return

    def setDispUnits(self, units) -> None:
        if units[0] == 'C':
            self.setDispToC()
        elif units[0] == 'F':
            self.setDispToF()
        else:
            print( "Wrong units <%s> use {C or F}"%(units) )

    def getMode(self) -> list:
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

    def setDispToF(self) -> None:
        self.comm._write( "MU1" )

    def setDispToC(self) -> None:
        self.comm._write( "MU2" )
