
def det2x2( M ):
    """
    """
    return M[0][0]*M[1][1] - M[0][1]*M[1][0]

def det3x3( M ):
    """
    """
    D1 = M[0][0] * (M[1][1]*M[2][2] - M[1][2]*M[2][1])
    D2 =-M[1][0] * (M[0][1]*M[2][2] - M[0][2]*M[2][1])
    D3 = M[2][0] * (M[0][1]*M[1][2] - M[0][2]*M[1][1])
    return D1+D2+D3

def linearSolver3x3( A, Y ):
    """
    Solve the linear equations represented in A & Y using to Cramer's rule
    """
    solver_OK = True
    detA = det3x3( A )
    result = [0,0,0]
    tmpCol = [0,0,0]
	
    #Solving n-th variable
    for i in range(0,3):
        #Storing i column
        tmpCol[0] = A[0][i]
        tmpCol[1] = A[1][i]
        tmpCol[2] = A[2][i]

        #Overwriting i column with 'solution' vector
        A[0][i] = Y[0]
        A[1][i] = Y[1]
        A[2][i] = Y[2]

        #Solving for i variable and storing the result in Result-Array
        detV = det3x3( A )
        if detA != 0.0:
            result[i] = detV/detA
        else:
            result[i] = 0.0
            solver_OK = False
            
        #Restoring i column
        A[0][i] = tmpCol[0]
        A[1][i] = tmpCol[1]
        A[2][i] = tmpCol[2]
        
    return (solver_OK, result)


def linearSolver2x2( A, Y ):
    """
    Solve the linear equations represented in A & Y using to Cramer's rule
    """
    solver_OK = True
    detA = det2x2( A )
    result = [0,0]
    tmpCol = [0,0]
    
    #Solving n-th variable
    for i in range(0,2):

        #Storing i column
        tmpCol[0] = A[0][i]
        tmpCol[1] = A[1][i]

        #Overwriting i column with 'solution' vector
        A[0][i] = Y[0]
        A[1][i] = Y[1]

        #Solving for i variable and storing the result in Result-Array
        detV = det2x2( A )
        if detA != 0.0:
            result[i] = detV/detA
        else:
            result[i] = 0.0
            solver_OK = False

        #Restoring i column
        A[0][i] = tmpCol[0]
        A[1][i] = tmpCol[1]
    return (solver_OK, result)
