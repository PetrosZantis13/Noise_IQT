import numpy as np
from sympy import Symbol
from sympy.solvers import solve
import time

print("from eclipse")
print("from atom")


def foo(*args):
    
    params = list(args)
    list_idx = 0
    
    #print( [type(args[i]) for i in range(0,len(args))] )
    for i in range(0,len(params)):
#         print(type(args[i]))
#         print(type(args[i]) == np.ndarray)
        if(type(params[i]) == np.ndarray):
            list_idx = i
            print("List is in position: " + str(list_idx))
            varlist = params[i]    
    
    
    for var in varlist:   # do with zip
        params[list_idx] = var 
        a, b, c, d, e = params
                
        print(a,b,c,d,e)
        
    print("end\n")

# foo(3.0, 45, np.linspace(0,3,4), 4, 5)
# 
# foo(3.0, 45, 4, 5, np.linspace(0,3,4))


def multiTone(tones):
    
    t1= time.time()
    
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
    
#     for j in range(1, tones+1):
#         np.exp()
    #print(np.sum(np.abs(cs)))
    
    t2 = time.time()
    print("For " + str(tones)+ " tones the calculation took: " + str(t2-t1) + " seconds")
    return R_min

for i in range(1,10):
    print(multiTone(i))  

    
