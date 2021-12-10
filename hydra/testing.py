import numpy as np
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

mystr = "Com frequency (eto)"

print(mystr.split("(")) 