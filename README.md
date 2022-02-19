# HYDRA

"For every head chopped off, the Hydra would regrow two." - For every noise source eliminated, two more pop up.

HYDRA is a software which visualises the error models for two-qubit microwave gates using trapped ions in a static magnetic field gradient. 
Perfect calibration of experimental parameters is assumed (no mis-set errors).
Allows the option to choose the variable parameter (horizontal axis) and optimise it for minimising errors (maximising fidelity).
Calculates maximum achievable fidelity due to inherent noise/error mechanisms.
Also calculates expected heating rate, gate time and coherence time.


## 1. Installation 

There are two ways to run the program : execute the python code or run the executable.

   - Executing the python code : Clone the Github repository, in a python environment run "python hydra/hydra.py"

   - Running the executable : The repository is precompiled, and the executable is available for download here : https://www.dropbox.com/sh/k32ud9l3iswu76q/AAAhsE7xK_B1VEvOixPkWXAea?dl=0
Simply download the zip of the latest version, extract it, and run the executable called "main.exe".


## 2. Documentation 

Click the following link : https://imperial-college-of-london-hydra.readthedocs-hosted.com/en/latest/errormodel.html


## 3. Miscellaneous

Version history : 

  - 1.1 : Added amplitude noise, CCW noise, and trap frequency (symmetric detuning) noise. Added temperature dependence to kerr coupling and trap frequency noise.
		  Cleaned up legend.
  - 1.0 : First stable release. Plotting heating, decoherence, kerr and offres errors. Can support up to four traces. Can save and load files. 

To do : 
  
  - Complete HELP section
  - Refine off-resonant coupling error model with pulse-shaping.
  - Add radial STR and COM vibrational modes
