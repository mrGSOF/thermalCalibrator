
"""
Calculate the IPTS68 correction.
This correction should be calculated for a temperature value that was derived
from Van-Dusen (ITS27) calaculation.
"""
A1 = 0.045
Zn = 419.58
A2 = 630.74

    
def ipts68(T):
    """Return the ITS68 correction for a given temperature in [C]"""
    return A1*(T/100.0)*((T/100.0) -1)*((T/Zn) -1)*((T/A2) -1)

        
