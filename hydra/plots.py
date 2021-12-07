import numpy as np
import matplotlib.pyplot as plt
import errormodel_myedits as em

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

def plot_errors():

    err_h, err_d, err_t, err_o, err_a = em.compute_total_errors(NU_C_LIST, Om, dzB, nuSE, SBa, SV, NuXY,
                                                    pulse_shaping = pulse_shaping, g_factor = g_factor,
                                                    vib_mode = vib_mode, chi = chi, dx = 1e-9, SA = SA,
                                                    nbar = nbar, sym_fluc = sym_fluc)
    
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

plot_errors()