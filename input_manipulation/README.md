#  Input Manipulation
The programs in this folder are mainly for setting parameters in input files like `*.scf.in`, `*.ph.in`, etc.

## `modparam.py`
Determines input file parameters for further Quantum Espresso calculations.

### Usage
1. Type `python workparam.py w` to edit this program with Sublime Text.

2. Edit `atoms` and `param_dict` in this program to set parameters.

3. Go to the working directory in which all the input files are, execute this program by typing `python workparam.py x`; all the input parameters will be changed as desired.

4. The examples of the input files are under the folder `./sample files/`