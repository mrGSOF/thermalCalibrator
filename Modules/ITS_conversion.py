from . import ITS27, ITS68, IPTS68, ITS90

def ITS_to_DICT( its, c, amb=None, tc=None ):
    if (its == 68) or (its == 27):
        d = {"TYPE": "ITS27", "R0": c[0], "Alpha": c[1], "Delta": c[2]}
    if (its == 90):
        d = {"TYPE": "ITS90", "RTPW": c[0], "a4":c[1], "b4": c[2],
                   "a7":c[3], "b7":c[4], "c7":c[5]}
    if amb:
        d["AMB"] = amb
    if tc:
        d["TC"] = tc
    return d
    
def ITS27_DICT():
    return {"TYPE": "ITS27", "R0": 0.0, "Alpha": 0.0, "Delta": 0.0}
    
def ITS90_DICT():
    return {"TYPE": "ITS90", "RTPW": 0.0, "a4":0.0, "b4": 0.0,
                   "a7":0.0, "b7":0.0, "c7":0.0}

def ITS( itsCoef ) -> dict:
##      {"TYPE": "ITS27", "R0": 198, "Alpha": 0.00363, "Delta": 1.5}
##   or {"TYPE": "ITS68", "R0": 198, "Alpha": 0.00363, "Delta": 1.5}
##   or {"TYPE": "ITS90", "RTPW": 198, "a4":0.0, "b4": 0.0,
##                        "a7":0.0, "b7":0.0, "c7":0.0}
##
    Type = itsCoef["TYPE"]
    its = None
    if Type == "ITS27":
        its = ITS27.ITS27( itsCoef )
    elif Type == "ITS68":
        its = ITS68.ITS68( itsCoef )
    elif Type == "ITS90":
        its = ITS90.ITS90( itsCoef )
    return its

def ITS27_to_ITS68(its27):
    return ITS68.ITS68({"R0":its27.R0, "Alpha":its27.Alpha, "Delta":its27.Delta})
    
def ITS68_to_ITS27(its68):
    return ITS27.ITS27({"R0":its68.R0, "Alpha":its68.Alpha, "Delta":its68.Delta})

def ITS27_to_ITS90(its27, stdListR=[176, 200, 230, 260, 300]):
    its68 = ITS27_to_ITS68(its27)
    its90 = ITS90.ITS90()
    stdTbl = []
    for ohm in stdListR:
        stdTbl.append(ITS90.stdPoint(ohm=ohm, degC=its68.T(ohm)))
    its90.solveCoef(stdTbl, its27.R0)
    return its90

def ITS90_to_ITS27(its90, stdListR=[176, 230, 300]):
    its27 = ITS27.ITS27()
    for ohm in stdListR:
        temp = its90.T(ohm)         #< The precise temperature at this resistance
        temp -= IPTS68.ipts68(temp) #< Minus the IPTS68 correction
        stdTbl.append(ITS90.stdPoint(ohm=ohm, degC=temp)) #< Store the virtual STD point
    its27.solveCoef(stdTbl)
    return its27

if __name__ == '__main__':
    stdTbl = []
#    stdTbl.append(ITS27.stdPoint(ohm=176, degC=-30.693))
#    stdTbl.append(ITS27.stdPoint(ohm=200, degC=-0.976))
#    stdTbl.append(ITS27.stdPoint(ohm=300, degC= 126.189))

    its68 = ITS({"TYPE":"ITS68", "R0":202, "Alpha":0.0035, "Delta":1.55})
    R1 = 263 #275
    R2 = 444 #441
    R3 = 612 #595
    
    stdTbl.append(ITS27.stdPoint( ohm=150, degC= its68.T(150)) )
    stdTbl.append(ITS27.stdPoint( ohm=200, degC= its68.T(200)) )
    stdTbl.append(ITS27.stdPoint( ohm=R1, degC= its68.T(R1)) )
    stdTbl.append(ITS27.stdPoint( ohm=R2, degC= its68.T(R2)) )
    stdTbl.append(ITS27.stdPoint( ohm=R3, degC= its68.T(R3)) )

    for row in stdTbl:
        print("%f, %f"%(row.ohm, row.degC))
    
    its27 = ITS27.ITS27()
    its27.solveCoef(stdTbl)
    print('\n *** Original ITS27 (Van-Dusen) ***')
    print('R0: %f'%(its27.R0))
    print('Alpha: %f'%(its27.Alpha))
    print('Delta: %f'%(its27.Delta))
    
    its90 = ITS27_to_ITS90(its27, stdListR=[176, 200, 230, 260, 300])
    print('\n *** ITS27 to ITS90 ***')
    print('RTPW: %f'%(its90.RTPW))
    print('a4: %f'%(its90.a4))
    print('b4: %f'%(its90.b4))
    print('a7: %f'%(its90.a7))
    print('b7: %f'%(its90.b7))
    print('c7: %f'%(its90.c7))

    its27 = ITS90_to_ITS27(its90, stdListR=[176, its90.RTPW, 300])
    print('\n *** Back to ITS27 (Van-Dusen) ***')
    print('R0: %f'%(its27.R0))
    print('Alpha: %f'%(its27.Alpha))
    print('Delta: %f'%(its27.Delta))
