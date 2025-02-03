
def degC_to_degF(C):
    """Input in degC units, Output in degF units"""
    return (C*9.0)/5.0 +32;	#< 1.8*Tc+32;

def degF_to_degC(F):
    """Input in degF units Output in degC units"""
    return ((F -32)*5.0)/9.0;	#< (F-32)/1.8
 
def C_to_units(C, units):
    if units == 'C':
        return C
    return degC_to_degF(C)

def units_to_C(T, units):
    if units == 'C':
        return T
    return degF_to_degC(T)

def C_to_units_dev(C, units):
    if units == 'C':
        return C
    return C*9.0/5.0
