import numpy as np
import matplotlib.pyplot as plt
import errormodel_forplots as em
#import errormodel_myedits as em   # for backup

plt.rcParams['figure.figsize'] = (8, 6)
plt.rcParams['font.size'] = 11

print("Let's plot!")

KHZ = 2*np.pi*1e3
MHZ = 2*np.pi*1e6

# Parameter name list
var_name_list = ["COM frequency (kHz)", "Magnetic field gradient (T/m)", "Gate Rabi frequency (kHz)",
                 r'Scaled Electric field noise (V/m)$^2$', "Ambient Magnetic field noise (T$^2$/ Hz)", 
                 "Voltage noise (V$^2$/ Hz)", "Radial mode frequency (MHz)", r"Initial temperature $\bar{n}$",                 
                 r"Heating factor $\phi$", r"Amplitude signal-to-noise ratio $\chi$",
                 "CCW current noise (A$^2$/ Hz)", r"Variance from voltage noise $\Delta$s",                 
                 r"Geometric factor $(m^-1)$", "Pulse shaping",  "Vibrational mode (0 => Stretch, 1 => COM)", "dx"]

# Parameter initial values
nu_c = 300*KHZ
dzB = 50
Om = 50*KHZ
nuSE = 10**-5
SBa = 10**-23
SV = 1
nuXY = 1.5*MHZ
nbar = 0.1
phi = 1
chi = 0
SA = 10**-12
sym_fluc = 0
g_factor = 70
pulse_shaping = False
vib_mode = 0   # Stretch mode
dx = 1e-9

# Parameter variable lists 
nu_c_list = np.linspace(100, 600, 100)*KHZ
dzB_list = np.linspace(1, 150, 151)
Om_list = np.linspace(1, 150, 151)*KHZ
nuSE_list = np.logspace(-8, -3, 101)
SBa_list = np.logspace(-25, -19, 101)
SV_list = np.logspace(-19, -12, 101)
nuXY_list = np.linspace(1, 5, 101)*MHZ
nbar_list = np.linspace(0, 10, 101)
phi_list = np.linspace(0, 10, 101)  # not sure
chi_list = np.linspace(0, 1, 101)
SA_list = np.logspace(-15, -3, 101)
sym_fluc_list = np.linspace(0, 10**-6, 101)  # not sure
g_factor_list = np.linspace(0, 100, 101)
pulse_shaping_list = np.linspace(0, 10, 101)  # not sure
vib_mode_list = np.array([0, 1])        # 0 => Stretch mode, 1 => COM mode
dx_list = np.linspace(0, 1e-8, 101)


var_lists = [nu_c_list, dzB_list, Om_list, nuSE_list, SBa_list, SV_list, nuXY_list, 
             nbar_list, phi_list, chi_list, SA_list, sym_fluc_list, g_factor_list,
             pulse_shaping_list, vib_mode_list, dx_list]

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
    
    if(list_idx==0 or list_idx==2):
        variable_list*= 1/KHZ
    elif(list_idx==6):
        variable_list*= 1/MHZ
    
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
    if(list_idx>=3 and list_idx<=5 or list_idx==10):
        plt.xscale("log")
    elif(list_idx==14):
        plt.xticks([0,1])
    plt.ylim(10**-4, 10**0)
    plt.legend()
    plt.show()

for i in range(0, len(var_lists)):
    #if(i!=6 or i!=9):
    fixed = [nu_c, dzB, Om, nuSE, SBa, SV, nuXY, nbar, phi, chi, SA, sym_fluc, 
             g_factor, pulse_shaping, vib_mode, dx]
    fixed[i] = var_lists[i]
    plot_errors(*fixed)
    
    