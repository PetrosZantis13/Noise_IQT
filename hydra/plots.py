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
NU_C_LIST = np.linspace(100, 600, 100)*KHZ


dzB = 50
Om = 50*KHZ
nuSE = 10**-4
SBa = 10**-23
SV = 1
NuXY = 1.5*MHZ
pulse_shaping = False
g_factor = 70
vib_mode = 0   # STRETCH
chi = 0
SA = 10**-12
nbar = 0.1
sym_fluc = 0
dx = 1e-9

def plot_errors():

    err_h, err_d, err_t, err_o, err_a = em.compute_total_errors(
        NU_C_LIST, Om, dzB, nuSE, SBa, SV, NuXY, pulse_shaping, 
        g_factor, vib_mode, chi, dx, SA, nbar, sym_fluc)
    
    err_tot = err_h + err_d + err_t + err_a
    
    plt.plot(NU_C_LIST/KHZ, err_tot, label = "Total Errors", color = 'b')
    plt.plot(NU_C_LIST/KHZ, err_h, label = "Heating", color = 'r')
    plt.plot(NU_C_LIST/KHZ, err_d, label = "Decoherence", color = 'k')
    plt.plot(NU_C_LIST/KHZ, err_t, label = "Kerr", color = 'm')
    plt.plot(NU_C_LIST/KHZ, err_a, label = "Amplitude", color = 'g')
    
    plt.title("Errors (Infidelity) over Secular Frequency")
    plt.xlabel("COM frequency (kHz)")
    plt.ylabel("Infidelity")
    plt.yscale("log")
    plt.ylim(10**-3, 10**0)
    plt.legend()
    plt.show()

#plot_errors()

'''
JUST TO TEST THE NEW FUNCTION, RESTRUCTURE LATER
'''

nu_c = 300*KHZ
nuSE_LIST = np.linspace(0, 10**-4, 101)

def plot_errors2():

    err_h, err_d, err_t, err_o, err_a = em.compute_total_errors(
        nu_c, Om, dzB, nuSE_LIST, SBa, SV, NuXY, pulse_shaping, 
        g_factor, vib_mode, chi, dx, SA, nbar, sym_fluc)
    
    err_tot = err_h + err_d + err_t + err_a
    
    plt.plot(nuSE_LIST, err_tot, label = "Total Errors", color = 'b')
    plt.plot(nuSE_LIST, err_h, label = "Heating", color = 'r')
    plt.plot(nuSE_LIST, err_d, label = "Decoherence", color = 'k')
    plt.plot(nuSE_LIST, err_t, label = "Kerr", color = 'm')
    plt.plot(nuSE_LIST, err_a, label = "Amplitude", color = 'g')
    
    plt.title("Errors (Infidelity) over Secular Frequency")
    plt.xlabel("COM frequency (kHz)")
    plt.ylabel("Infidelity")
    plt.yscale("log")
    plt.ylim(10**-3, 10**0)
    plt.legend()
    plt.show()

plot_errors2()

# TRY IT AGAINST ALL VARIABLES




