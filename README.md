# HYDRA

*"For every head chopped off, the Hydra would regrow two." - For every noise source eliminated, two more pop up.*

HYDRA is a software which visualises the error models for two-qubit microwave gates using trapped ions in a static magnetic field gradient.

• Perfect calibration of experimental parameters is assumed (no mis-set errors).  
• Allows the option to choose the variable parameter (horizontal axis) and optimise it for minimising errors (maximising fidelity).  
• Calculates maximum achievable fidelity due to inherent noise/error mechanisms.  
• Also calculates expected heating rate, gate time and coherence time.  



## 1. Installation 

There are two ways to run the program: 

1) Running the executable : The repository is precompiled, and the executable is available for download here: 
   https://github.com/PetrosZantis13/Noise_IQT/blob/master/dist/hydra-v1.2.exe

   Simply download the application and run the executable file called "hydra.exe".

2) Compiling the python code : Clone the Github repository and in a python environment run "python hydra/hydra.py"



## 2. Documentation 

There are two pdf files inside the docs folder (https://github.com/PetrosZantis13/Noise_IQT/tree/master/docs):   

1) Presentation+Results.pdf (A presentation on HYDRA and some preliminary results obtained using the program. The slides are displayed in the docs/README.md file)  

2) Documentation_previous.pdf (A previous version of the documentation explaining the error model derivations; included for completeness.)



## 3. Miscellaneous

This software was adapted with permission from https://github.com/christophevalahu/hydra.git

Updates from me (Petros Zantis) on the original (Christophe Valahu) HYDRA include:

• Distinct colour coding of error plots.  
• Drop-down list to change the variable parameter (horizontal axis).  
• Expected coherence time added to the results table.  
• Option to simulate multi-tone and multi-loop MS gates. (new 'K' parameter)  
• Refined some equations (e.g. 1/3 factor in decoherence infidelity)  
• Effect of electrode pairing added, if voltage noise on the electrodes is assumed to be correlated.  

![](docs/Presentation+Results/Slide3.PNG)
