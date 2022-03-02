import numpy as np
from sympy import Symbol
from sympy.solvers import solve
import time

# ------------------------------------------
# Other MS Schemes (Multi-Tone)
# ------------------------------------------

def calc_Rheat(tones):
    '''
    Calculates analytically the reduced heating factors when using multi-tone MS gates.
    '''
    
    if tones==1:
        return 1
    
    l = Symbol('l')
    sum = 0
    
    for j in range(1, tones+1):
        sum += 1/(1-(j*l)) 
        
    solutions = solve(sum,l)
    
    cs = np.zeros( (len(solutions), tones) )
    Rs = np.zeros( len(solutions) )
    
    for i in range( len(solutions)):
    
        sol = solutions[i]
        #print("\nWith lambda= " + str(sol) + ",")
        
        b=0
        for j in range(1, tones+1):
            b += j/(1-j*sol)**2
        
        b = -(1/4)* b**(-1/2)    
        Rheat = 0
        
        #print("\nThe cs are:")
        for j in range(1, tones+1):
            c = 4*j*b / (1-j*sol)
            Rheat += c**2 / j**2
            #print( float(c) )
            cs[i,j-1] = c
        
        Rheat = float(Rheat/2)
        Rs[i] = Rheat
        #print("\nand Rheat = " + str(Rheat))   
    
    # find the best solution which corresponds to the lower Rheat
    min_idx = np.argmin(Rs)
    cs_min = cs[min_idx]
    R_min = Rs[min_idx]

    return R_min

def multitone(max):
    '''
    Can be used if one wants to investigate the effects of using Multi-Tone MS gates (MTMS).
    Returns the reduced heating factors corresponding to the number of tones used in MTMS.
    Might take a few seconds to calculate.
    '''
    
    multiTones = []
    print("Calculating Multi-Tone heating factors...")    
    for tone in range(1,max+1):
        print("for " + str(tone) + " tones")
        multiTones.append(calc_Rheat(tone))
    
    print("Done!\nThe reduced heating factors are:") 
    print(multiTones)
    return multiTones

multitone(10)       # Used this to include the Rheats into the errormodel.
