import math
from . import IPTS68
from . import linearSolver as LS

class stdPoint():
    def __init__(self, ohm, degC):
        self.ohm = ohm
        self.degC = degC
        
class ITS27():
    """
    Using the root of the 2nd degree equation: RT/R0 = -(Alpha*Delta/10000)*T^2 +Alpha*(1+Delta/100)*T +1
    """
    def __init__(self, coef={"R0":200.0, "Alpha":0.0039, "Delta":1.55}):
        """
        Init the Van-Dusen coefficiants
        """
        self.R0 = coef["R0"]
        self.Alpha = coef["Alpha"]
        self.Delta = coef["Delta"]

    def T( self, R):
        """
        Input in [Ohm] units
        Output in [C] units
        """
        #T(RT) = (A1 - sqrtf(A1*A1 -2*A3*(PRTohm -R0)))/A3
        A1 = self.R0*self.Alpha*((self.Delta/100.0) +1.0)
        A3 = 2.0*self.Alpha*self.Delta*self.R0/10000.0
        return (A1 - math.sqrt(A1*A1 -2.0*A3*(R -self.R0)))/A3

    def solveCoef(self, stdTbl):
        """
        Standartization Process - Finding the true RTD coeficiants ( Resistance to Celsius units only)
        """
        A = []
        Y = []
        for i in range(0,3):
            A.append([0,0,0])
            A[i][0] = 1.0
            T = stdTbl[i].degC
            A[i][1] = T -IPTS68.ipts68( T )	#Removing the its68 correction because we need the ITS27 conversion;
            T = T/100.0
            A[i][2] = T*(T-1.0)
            Y.append( stdTbl[i].ohm )

        (solveOK, Coef) = LS.linearSolver3x3( A, Y )
        if solveOK == True:
            self.R0 = Coef[0]
            self.Alpha = Coef[1] / Coef[0]
            self.Delta = -Coef[2] / Coef[1]
        return solveOK

if __name__ == '__main__':
    stdTbl = []
    stdTbl.append(stdPoint(ohm=176, degC=-30.693))
    stdTbl.append(stdPoint(ohm=200, degC=-0.976))
    stdTbl.append(stdPoint(ohm=300, degC= 126.189))
    its27 = ITS27()
    its27.solveCoef(stdTbl)
    print('R0: %f'%(its27.R0))
    print('Alpha: %f'%(its27.Alpha))
    print('Delta: %f'%(its27.Delta))
    
        
