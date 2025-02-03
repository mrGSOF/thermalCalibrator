import datetime, logging, copy, time
from Modules import fileLib
from Modules import Date
from Modules import TEMP_conv as T

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger()

def getDate() -> dict:
    date = datetime.date.today()
    return {"DAY":date.day, "MONTH":date.month, "YEAR":date.year}

class Report():
    def __init__(self, Type=None, units=None, date=None, unit=None, dmm=None, uut=None, ref=None, filename=None, t=None ):
        self.filename = filename
        self.T0 = None
        uid = ""
        if unit:
            uid = unit["UID"]

        self.dat = {
            "TYPE":str(Type),
            "UID":uid,
            "DATE":date,
            "UUT":uut,
            "DMM":dmm,
            "REF":ref,
            "COEF":"",
            "RESULTS":{
                "UNITS":units,
                "AMB":0.0,
                "DEVTBL":[]}
            }

    def _result(self, unit, ref, uut, units, soak, passThres=None, amb=None) -> dict:
        if self.T0 == None:
            self.T0 = time.time()
        dev = uut -ref
        mark = ""
        if passThres:
            mark = "PASS"
            if abs(dev) > passThres:
                mark = "FAIL"
        return {"TIME":int(time.time() -self.T0),
                "UNIT":unit,
                "REF":ref,
                "UUT":uut,
                "UNITS":units,
                "DEV":dev,
                "AMB":amb,
                "SOAK":soak,
                "MARK":mark,
                "THRS":passThres,
                "THRS_MIN":ref -passThres,
                "THRS_MAX":ref +passThres}

    def _resultAdd(self, result) -> int:
        self.dat["RESULTS"]["DEVTBL"].append( result )
        return len( self.dat["RESULTS"]["DEVTBL"] ) 

    def addResultMeas(self, unit, uut, units, soak, passThres=None, amb=None) -> int:
        result = self._result(unit=unit, ref=unit, uut=uut, units=units, soak=soak, passThres=passThres, amb=amb)
        logger.info( "MEAS-PT: %s"%(str(result)) )
        return self._resultAdd( result )

    def addResultFree(self, unit, ref, units, soak, passThres=None, amb=None) -> int:
        result = self._result(unit=unit, ref=ref, uut=unit, units=units, soak=soak, passThres=passThres, amb=amb)
        logger.info( "FREE-PT: %s"%(str(result)) )
        return self._resultAdd( result )

    def addResultCal(self, unit, ref, units, soak, passThres=None, amb=None) -> int:
        result = self._result(unit=unit, ref=ref, uut=unit, units=units, soak=soak, passThres=passThres, amb=amb)
        logger.info( "CAL-PT: %s"%(str(result)) )
        return self._resultAdd( result )

    def addResultStd(self, unitT, unitR, refT, units, soak, amb=None) -> int:
        if self.T0 == None:
            self.T0 = time.time()
        dev = unitT -refT
        result = {"TIME":int(time.time() -self.T0),
                  "UNIT":unitT,
                  "RES":unitR,
                  "REF":refT,
                  "DEV":dev,
                  "UNITS":units,
                  "AMB":amb,
                  "SOAK":soak,
                  "THRS":0.0}
        
        logger.info( "STD-PT: %s"%(str(result)) )
        return self._resultAdd( result )

    def getResult(self, i) -> dict:
        if i > len(self.dat["RESULTS"]["DEVTBL"]):
            i = -1
        return self.dat["RESULTS"]["DEVTBL"][i]

    def refresh(self, date = None, its = None, newIts = None):
        avgAmb = 0.0
        n = 0
        results = self.dat["RESULTS"]
        for step in results["DEVTBL"]:
            avgAmb += step["AMB"]
            n += 1
        if n > 0:
            results["AMB"] = avgAmb/n
        else:
            results["AMB"] = avgAmb

        if date:
            self.dat["DATE"] = date

        if its:
            self.dat["COEF"] = its

        if newIts:
            results["NEW_COEF"] = newIts

    def getType(self) -> str:
        return self.dat["TYPE"]

    def getUnitID(self) -> str:
        return self.dat["UID"]

    def getUnitModel(self) -> str:
        return self.dat["UUT"]["MODEL"]

    def getRefID(self) -> str:
        return self.dat["REF"]["SN"]

    def getRefModel(self) -> str:
        return "%s-%s"%(self.dat["REF"]["MFR"], self.dat["REF"]["MODEL"])

    def getDate(self) -> str:
        return Date.toStr(self.dat["DATE"])

    def getReport(self) -> dict:
        return self.dat

    def convTo(self, units="F") -> dict:
        data = copy.deepcopy(self.dat)
        resC = data["RESULTS"]
        resC["UNITS"] = units
        resC["AMB"] = T.C_to_units(resC["AMB"], units)
        for res in resC["DEVTBL"]:
            for key in res:
                if (key == "UNIT") or (key == "UUT") or (key == "REF") or (key == "AMB") or (key == "THRS_MIN") or (key == "THRS_MAX"):
                    res[key] = T.C_to_units(res[key], units)
                elif (key == "DEV") or (key == "RATE") or (key == "THRS"):
                    res[key] = T.C_to_units_dev(res[key], units)
                elif key == "UNITS":
                    if res[key] in ("C","F"):
                        res[key] = units
        return data

    def save(self, filename=None, overWrite=True) -> None:
        if filename == None:
            filename = self.filename

        if overWrite == False:
            #print( "Check if file <%s> exists" )
            while fileLib.isFileExists(path="", name=filename, ext=""):
                print( "Renaming the file name" )
                name, ext = fileLib.splitFilename(filename)
                name = "%s_"%name
                filename = "%s%s"%(name,ext)
        fileLib.saveJsonFile(self.dat, path="", name=filename, ext="")

    def delete(self):
        print(self.filename)
        fileLib.deleteFile(path="", name=self.filename, ext="") 
