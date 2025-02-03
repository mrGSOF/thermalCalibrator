import math
from . import linearSolver as LS

class stdPoint():
    def __init__(self, ohm, degC):
        self.ohm = ohm
        self.degC = degC

class ITS90():
    """
    Calculate the temperature using the ITS90 equations:
    83.8058K to 273.16K ; a4(W-1) + b4(W-1)ln(W) ; Ar, Hg
    0C to 660.323C ; a7(W-1) + b7(W-1)^2 + c7(W-1)^3 ; Sn, Zn, Al
    """
    A = [
        -2.13534729,
         3.18324720,
        -1.80143597,
         0.71727204,
         0.50344027,
        -0.61893395,
        -0.05332322,
         0.28021362,
         0.10715224,
        -0.29302865,
         0.04459872,
         0.11868632,
        -0.05248134
        ]

    B = [
         0.183324722,
         0.240975303,
         0.209108771,
         0.190439972,
         0.142648498,
         0.077993465,
         0.012475611,
        -0.032267127,
        -0.075291522,
        -0.056470670,
         0.076201285,
         0.123893204,
        -0.029201193,
        -0.091173542,
         0.001317696,
         0.026025526
         ]

    C = [
         2.78157254,
         1.64650916,
        -0.13714390,
        -0.00649767,
        -0.00234444,
         0.00511868,
         0.00187982,
        -0.00204472,
        -0.00046122,
         0.00045724
         ]

    D = [
         439.932854,
         472.418020,
         037.684494,
         007.472018,
         002.920828,
         000.005184,
        -000.963864,
        -000.188732,
         000.191203,
         000.049025
        ]

    def __init__(self,
                 coef={"RTPW":99.892,
                 "a4":-0.017702,
                 "b4": 0.011854,
                 "a7":-0.01843,
                 "b7":-0.001073193,
                 "c7": 0.0005989515}
                 ):
        """
        Init the ITS90 coefficiants
        """
        self.RTPW= coef["RTPW"]
        self.a4 = coef["a4"]
        self.b4 = coef["b4"]
        self.a7 = coef["a7"]
        self.b7 = coef["b7"]
        self.c7 = coef["c7"]
 
    def T( self, R):
        """
        Input in [Ohm] units
        Output in [C] units
        """
        W = R / (self.RTPW)
        if W<=1:
            Wr = W - self.DW(0, W )
            Wr = ( (Wr**(1.0/6.0)) -0.65)/0.35
            Tk = self.B[0]
            for i in range(1,16):
                Tk += self.B[i]*(Wr**i)
            #Tk *= 273.15 #Was
            Tk *= 273.16 #Acourding to Elik
        else:
            Wr = W - self.DW(300, W )
            Wr = (Wr-2.64)/1.64
            Tk = self.D[0] +273.15
            for i in range(1,10):
                Tk += (self.D[i])*( (Wr**i) )
        return degK_to_degC(Tk)

    def Wref( self, Tmeas):
        Tmeas = degC_to_degK(Tmeas)
        if (Tmeas<=273.16):
            Wr = self.A[0]
            Tmeas = (math.log(Tmeas/273.16)+1.5)/1.5
            for i in range(1,13):
                Wr += self.A[i]*(Tmeas**i)
            Wr = math.exp(Wr)
        else:
            Wr = self.C[0]
            Tmeas = (Tmeas-754.15)/481.0
            for i in range(1,10):
                Wr += self.C[i]*(Tmeas**i)
        return Wr
     
    def DW( self, T, W):
        if T<=273.16:
            return self.a4*(W-1) + self.b4*(W-1)*math.log(W)
        return self.a7*(W-1) + self.b7*(W-1)**2 + self.c7*(W-1)**3

    def solveCoef(self, stdTbl, RTPW):
        """
        Standartization Process - Finding the ITS90 coeficiants ( Resistance to Celsius units only)
        """
        A = []
        Y = []

        #Solving for below 0[C] region
        for i in range(0,2):
            W = stdTbl[i].ohm / RTPW
            Wr = self.Wref( stdTbl[i].degC)
            A.append([0,0])
            A[i][0] = W-1
            A[i][1] = (W-1)*math.log(W)
            Y.append( W -Wr )

        (solve_OK, Coef) = LS.linearSolver2x2( A, Y )
        if solve_OK == True:
            self.RTPW = RTPW
            self.a4 = Coef[0]
            self.b4 = Coef[1]
        else:
            return False;

        A = []
        Y = []
        for i in range(0,3):
            W = stdTbl[i+2].ohm / RTPW
            Wr = self.Wref( stdTbl[i+2].degC)
            A.append([0,0,0])
            A[i][0] = W-1
            A[i][1] = A[i][0]*A[i][0]
            A[i][2] = A[i][1]*A[i][0]
            Y.append( W -Wr )

        for row in A:
            print(row)
        print("\n")
        for row in Y:
            print(Y)

        (solve_OK, Coef) = LS.linearSolver3x3( A, Y )
        if solve_OK == True:
            self.a7 = Coef[0]
            self.b7 = Coef[1]
            self.c7 = Coef[2]
        return solve_OK

def degC_to_degK(Temp): #Convert degC to degK
    return Temp + 273.15

def degK_to_degC(Temp): #Convert degK to degC
    return Temp -273.15

if __name__ == '__main__':
    stdTbl = []
    stdTbl.append(stdPoint(ohm=176, degC=-30.693))
    stdTbl.append(stdPoint(ohm=200, degC=-0.976))
    stdTbl.append(stdPoint(ohm=230, degC= 36.595))
    stdTbl.append(stdPoint(ohm=260, degC= 74.653))
    stdTbl.append(stdPoint(ohm=300, degC= 126.189))
    its90 = ITS90()
    its90.solveCoef(stdTbl=stdTbl, RTPW=200.7839)
    print('RTPW: %f'%(its90.RTPW))
    print('a4: %f'%(its90.a4))
    print('b4: %f'%(its90.b4))
    print('a7: %f'%(its90.a7))
    print('b7: %f'%(its90.b7))
    print('c7: %f'%(its90.c7))
