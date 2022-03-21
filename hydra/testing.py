import numpy as np
from sympy import Symbol
from sympy.solvers import solve
import matplotlib.pyplot as plt
import os
import time
plt.rcParams['figure.figsize'] = (12, 5)
plt.rcParams['font.size'] = 9

print("Testing custom functions:")

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

def add_delay(list, fract):
    '''
    list: the list of functions you want to mirror
    fract: the delay you want to add given as a fraction of the size of the original functions
    '''
    
    newV = []    
    plt.subplot(1, 2, 1)
    plt.plot(list)
    
    for funct in list.T:
        delay = np.ones(int(fract*funct.size)) * funct[-1]
        newFunct = np.concatenate((funct,delay,funct[::-1]))
        newV.append(newFunct)
    
    newV = np.array(newV)
    plt.subplot(1, 2, 2)
    plt.plot(newV.T)
    plt.show()
    return newV


V = np.loadtxt("C:/Users/Petros Laptop/Downloads/Eustace_Junction_Straight_WE_33_ramp_T20220321-120702.csv",dtype=float,delimiter=",")
# xs = np.linspace(1,10,100)
# logistic = 1/(1+ 50*np.exp(-xs))
# #logistic = xs
add_delay(V, 0.5)    
