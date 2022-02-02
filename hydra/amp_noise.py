import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt


def ou_process_frequency_fluctuations(T2 = 0, Nsamples = 0, tmax = 0):
    
    # Obtain a continuous function interpolated from discrete random
    # variables of an OU process, corresponding to frequency fluctuations
    # T2 : Coherence time in seconds
    # Nsamples: Number of samples taken from the discrete OU process
    # tmax: Maximum time in seconds
    
    x = np.zeros(Nsamples)
    
    tau = T2/10 # Correlation time in seconds
    c = 2/(T2*tau**2) # Diffusion constant
    dt = tau/10 # Time steps
    
    for i in range(Nsamples-1):
        x[i+1] = x[i]*np.exp(-dt/tau) + \
            np.sqrt(c*t/2*(1-np.exp(-2*dt/tau)))*np.random.normal()
    
    times = np.linspace(0, tmax, Nsamples)
    return interp1d(times, x)


def ou_process_amplitude_fluctuations(xi = 0, Omega=0 , tau = 0, Nsamples = 0, tmax = 0):
    
    # Obtain a continuous function interpolated from discrete random
    # variables of an OU process, corresponding to amplitude fluctuations
    # xi : Relative amplitude fluctuations, dOmega/Omega
    # Omega : Rabi frequency of the field in rad * Hz
    # tau : Correlation time in seconds
    # Nsamples: Number of samples taken from the discrete OU process
    # tmax: Maximum time in seconds
    
    x = np.zeros(Nsamples)
    c = 2*(xi*Omega)**2/tau # Diffusion constant
    dt = tau/10 # Time steps
    
    for i in range(Nsamples-1):
        x[i+1] = x[i]*np.exp(-dt/tau) + \
            np.sqrt(c*tau/2*(1-np.exp(-2*dt/tau)))*np.random.normal()
    
    times = np.linspace(0, tmax, Nsamples)
    return interp1d(times, x)


xs = np.linspace(0, 10, 100)
f = ou_process_amplitude_fluctuations(10**-3, 50, 1, 100, 10)
plt.plot(xs, f(xs))
plt.show()
