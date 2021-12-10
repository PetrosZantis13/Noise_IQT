import numpy as np
import matplotlib.pyplot as plt
import errormodel_forplots as em
#import errormodel_myedits as em   # for backup

plt.rcParams['figure.figsize'] = (8, 6)
plt.rcParams['font.size'] = 11

print("Let's plot!")

"Continue here to produce some interesting plots!"

KHZ = 2*np.pi*1e3
MHZ = 2*np.pi*1e6

# make the names better
var_name_list = ["COM frequency (kHz)", "Gate Rabi frequency (kHz)", "Magnetic field gradient (T/m)",
                 r'Scaled Electric field noise (V/m)$^2$', "Ambient Magnetic field noise (T$^2$/ Hz)", 
                 "Voltage noise (V$^2$/ Hz)", "Radial mode frequency (MHz)", "Pulse shaping", 
                 r"G factor (m^-1)", "Vib mode", "Chi", "dx", "SA", 
                 r"Initial temperature $\bar{n}$", "sym_fluc"]

nu_c = 300*KHZ
Om = 50*KHZ
dzB = 50
nuSE = 10**-4
SBa = 10**-23
SV = 1
nuXY = 1.5*MHZ
pulse_shaping = False
g_factor = 70
vib_mode = 0   # STRETCH
chi = 0
dx = 1e-9
SA = 10**-12
nbar = 0.1
sym_fluc = 0

nu_c_list = np.linspace(100, 600, 100)*KHZ
Om_list = np.linspace(1, 150, 151)*KHZ
dzB_list = np.linspace(1, 150, 151)
nuSE_list = np.linspace(0, 10**-4, 101)
SBa_list = np.linspace(0, 10**-20, 101)
SV_list = np.linspace(0, 10**-14, 101)
nuXY_list = np.linspace(1, 5, 101)*MHZ
g_factor_list = np.linspace(0, 100, 101)
SA_list = np.linspace(0, 10**-6, 101)
nbar_list = np.linspace(0, 10, 101)

var_lists = [nu_c_list, Om_list, dzB_list, nuSE_list, SBa_list, SV_list, nuXY_list, g_factor_list, SA_list, nbar_list]

fixed = [nu_c, Om, dzB, nuSE, SBa, SV, nuXY, pulse_shaping, 
        g_factor, vib_mode, chi, dx, SA, nbar, sym_fluc]

def plot_errors(*args):
    
    params = list(args)
    list_idx = 0
    
    for i in range(0,len(params)):
        if(type(params[i]) == np.ndarray):
            list_idx = i
            print("List is in position: " + str(list_idx))
            variable_list = params[i]  
    
    var_name = var_name_list[list_idx].split("(")[0]
            
    err_h, err_d, err_t, err_o, err_a = em.compute_total_errors(*args)
    
    err_tot = err_h + err_d + err_t + err_a
    
    plt.plot(variable_list, err_tot, label = "Total Errors", color = 'b')
    plt.plot(variable_list, err_h, label = "Heating", color = 'r')
    plt.plot(variable_list, err_d, label = "Decoherence", color = 'k')
    plt.plot(variable_list, err_t, label = "Kerr", color = 'm')
    plt.plot(variable_list, err_a, label = "Amplitude", color = 'g')
    
    plt.title("Errors (Infidelity) over " + var_name)  
    #plt.xlabel("COM frequency (kHz)")
    plt.xlabel(var_name_list[list_idx])
    plt.ylabel("Infidelity")
    plt.yscale("log")
    plt.ylim(10**-3, 10**0)
    plt.legend()
    plt.show()

for i in range(0, len(var_lists)):
    fixed = [nu_c, Om, dzB, nuSE, SBa, SV, nuXY, pulse_shaping, 
        g_factor, vib_mode, chi, dx, SA, nbar, sym_fluc]
    fixed[i] = var_lists[i]
    plot_errors(*fixed)
    
    

