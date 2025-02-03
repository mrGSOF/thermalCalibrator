import datetime

def date(month, day, year):
    return {"MONTH":month, "DAY":day, "YEAR":year}
    
def toStr(date, style="MDY") -> str:
    if style == "MDY":
        return "M%s_D%s_Y%s"%(date["MONTH"],
                           date["DAY"],
                           date["YEAR"])
    if style == "DMY":
        return "D%s_M%s_Y%s"%(date["DAY"],
                           date["MONTH"],
                           date["YEAR"])
    else:
        return toStrMDY(date)

def toStrMDY(date) -> str:
    return "%s/%s/%s"%(date["MONTH"],
                       date["DAY"],
                       date["YEAR"])

def toStrDMY(date) -> str:
    return "%s/%s/%s"%(date["DAY"],
                       date["MONTH"],
                       date["YEAR"])

def toDict(strDate) -> dict:
    strDate = strDate.split('_')
    _date = date(1, 1, 2020)
    for v in strDate:
        if v[0] == 'M':
            _date["MONTH"] = int(v[1:])
        
        elif v[0] == 'D':
            _date["DAY"] = int(v[1:])

        elif v[0] == 'Y':
            _date["YEAR"] = int(v[1:])
    return _date

def isPassed(_date) -> bool:
    # date in yyyy/mm/dd format
    d = datetime.date.today()
    today = datetime.datetime(d.year, d.month, d.day)
    d1 = datetime.datetime(_date["YEAR"], _date["MONTH"], _date["DAY"])
    return today >= d1
