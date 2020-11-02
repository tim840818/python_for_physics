#  Python Files for Physics
These files which mainly worked for Quantum Espresso program were written for my research works. They were catagorized as:
* **File manipulation**: Shows details or locations of working files/directories, cleans specified files/dirs, etc.
* **Input manipulation**: Modifies input file parameters using Python's `re` (regex) module.
* **Job queuing**: Automatic submits a series of jobs, and periodically checks their progress.
* **Data processing**: Mathematically processes the output data, e.g., integrations, transforming units, etc.

## Modules used
Built-in modules:
`re`, `numpy`, `math`, `matplotlib` `os`, `sys`, `time`, `subprocess`, `argparse`

User-defined modules:
`parse`, `multibatch`, `crystalbase`

## Programs included

### File manipulation
* `clean.py`: Finds and displays the specified files/dirs that users want to delete, and allows users to choose which to delete.

* `hellowork.py`: Shows the sub directories of each working directory, provides options for more detail informations like used storage.

* `workparam.py`: Finds and opens/executes the file 'modparam.py' for further steps.

### Input manipulation
* `modparam.py`: Determines input file parameters for further Quantum Espresso calculations.

### Job queuing
* `jobop.py`: Determines the CPU 'cores' and 'nodes' of job submission file `job.sh`.

* `qebatch.py`: Automatically submits jobs in order and checks for error messages routinely.

### Data processing
* `check_maxmin.py`: Finds the maximum and minimum of y data in a file and prints 'Warning' if there are multiple y data or the minimum of the y data < 0. Prints only the maximum and the minimum of the data if everything goes right.

* `normbandos.py`: Normalizes the output data regarding electrons (electron bands/density of states) by the Fermi level; for k-points (or q-points in data regarding phonons), normalizes them to [0, 1].

* `transbasis.py`: Transforms the coordinates of a chosen crystal in different basis.

* `thermal_ph.py`: Performs a numerical integration from the phonon DOS file `*.phonon.dos` and calculates the phonon contribution of heat capacity. The results are written into two files: `Cv_ph.dat` and `Cv-T_ph.dat`.
