#  Data Processing
The programs in this folder deal with the data mathematically, e.g., integrations, transforming units, finding max/min, etc.

## `check_maxmin.py`
Finds the maximum and minimum of y data in a file and prints `Warning` if there are multiple y data or the minimum of the y data < 0. Prints only the maximum and the minimum of the data if everything goes right.

### Usage
1. `check_maxmin.py filename`; filename is the name of file which you want to check for max/min.


## `normbandos.py`
Normalizes the output data regarding electrons (electron bands/density of states) by the Fermi level. For k-points (or q-points in phononic data), normalizes them to [0, 1].

### Usage
1. This program is written specifically for QE users and files which have `/qe` as their parent directory. It can process a file each time.

2. Instructions
	1) Prepare the output files (band, dos, phonon dispersion).
		band: `bands.dat.gnu`, etc.
		dos: `S.dos`, etc.
		phonon dispersion: `freq.plot`, etc.
	2) Prepare `kdist.dat` for "band" and "phonon dispersion" normalizations.
	3) Execute this program and follow the instructions.
	4) A normalized output file (`*-qe_*.dat`) will be created.

3. Examples:
	- Please check for `bands.dat.gnu` (input) and `FeSe-qe_band.dat` (output) under the folder `./sample files/normbandos`.


## `transbasis.py`
Reads the parameters from `atoms.json` and transforms the coordinates of the crystal in different basis from the parameters. After that creates output files: `atompos-out.dat` for x-space, `kpath-out.dat`, `qpath-out.dat`, and `kdist.dat` for k-space.

### Usage
1. It only works for several crystal structures; you should prepare the file `atoms.json` and its parameters accordingly.

2. Examples:
	- Please check for `atoms.json` (input) and `atompos-out.dat`, `kpath-out.dat`, `qpath-out.dat`, `kdist.dat` (output) under the folder `./sample files/transbasis`.


## `thermal_ph.py`
Performs a numerical integration from the phonon DOS file `*.phonon.dos` and calculates the phonon contribution of heat capacity. The results are written into two files: `Cv_ph.dat` and `Cv-T_ph.dat`.

### Usage
1. The integration formula: c_v(T) = int[f(w, T) * D(w)dw].
	* w: frequencies
	* T: temperatures
	* f(w, T): integration function
	* D(w): phonon DOS function

2. You should prepare the file whose name is `*.phonon.dos` to execute this file.

3. Examples:
	- Please check `FeSe.phonon.dos` (input) and `Cv_ph.dat`, `Cv-T_ph.dat` (output) under the folder `./sample files/thermal_ph`.
