#  Modules
The files in this folder contain packages and functions for general purposes. Files like `modparam.py`, `qebatch.py`, `transbasis.py` import these modules for further use.

To import this modules, first insert the path by typing `from sys import path; path.insert(0, filepath)`; filepath is the string which means the relative path of this folder (modules) to the destination folder. And then import the modules by typing `from filename import classname`; filename is the name of the desired file in this folder (please exclude ".py"), and the classname(s) are the classes in the file.

For example, to import modules from `multibatch.py` to `qebatch.py`, check the paths of these two files:

* `qebatch.py`: "pyf/job_queuing/qebatch.py"
* `multibatch.py`: "pyf/modules/multibatch.py"

Hence, type `from sys import path; path.insert(0, "../modules")` in `qebatch.py` to set the path.
To further import classes, type `from multibatch import Job, Batch` in `qebatch.py`.

## parse

### Class:
`Parser`: Analyzes the pattern of a file using `re`, and substitutes new strings in it.

### Usage:
```python
from parse import Parser
```

1. 	Initialization:
	`P = Parser()`. This program automatically finds all the `*.in` files in current directory.

2. 	Functions
	1) 	Global functions: `P.*(parameters)`, ex: `P.add_ctrl(a, b)`, `P.add_line(a, b, n, direction)`. Modifies ALL files.
	2) 	Local  functions: `P.*_l(file, parameters)`, ex: `P.add_ctrl(file, a, b)`, `P.add_anchor_l(file, anchor, b)`. Modifies only the files stated in `file` (can be a str, a list of str, or regex).

	Please refer to documentations for each function

3. 	Notification:
	1) 	Parameters called `a` are matched using regex. On the other hand, parameters called `b` are strings.
	2) 	Parameters called `anchor` are regexes match the entire single line. Hence, do not put newlines(\n) into `anchor`.
	3) 	Since `a` and `anchor` are regex, please use regex to express these parameters.

4. 	Examples:
```python
def format_dos(P, pwd):
	P.add_ctrl_l("{}.nscf.in".format(atoms), "occupations", "tetrahedra") if "/dos" in pwd else 0

def format_title(P):
	P.add_line(r"&control", atoms+"\n", n="inf", direction="up")

def format_crystal(P):
	P.del_line(r"B\s*=")
	P.del_line(r"C\s*=")
	cryst_str = "\n".join(["  "+" = ".join(alat) for alat in param_dict["CRYST"]])
	P.replace_single_line(r"A\s*=", cryst_str)
```

## multibatch

### Class:
`Job`: Contains all the preprocess, checking process, running process, and postprocess functions for a job.

`Batch`: Combines all the jobs and their processes, and executes them in order.

### Usage:
```python
from multibatch import Job, Batch
```

1. 	Prepare the following for each job:
	* Name of the file to submit
	* Number of cores needed
	* Relevant data
	* Functions (preprocess/postprocess) to handle the revelant data. Note that these functions should be written by YOURSELF.
	* A list of files that will be used in this job.

	Please note that, when referring to a file that you want to modify, please ALWAYS use the data["files"] mapping.
	This maps the name of the original file to the new file name (i.e. in a new directory, etc.)
	Since the name of the file may change, the safest way to refer to the file is by the mapping.
	For example, if you want to modify `ecutwfc` in `*.scf.in`:
```python
def preprocess(data):
	scfin_filename = data["files"]["*.scf.in"]
	scfin_file = open(scfin_filename, "r")
	# modify scfin_file...
```

2. 	Place all jobs into a list.
	- If it is a single job, simply put it in.
	- If it is a series of jobs that must be executed in order, put them in a list.
	- **Then, convert the jobs into a batch.**
	You should end up with a list of jobs: 
		```
		batch_list = [Batch(single_job1), Batch(single_job2), Batch([batchjob1, batchjob2]), Batch(single_job3), ...]
		```
	Done!

3. 	Example:
```python
def job1_pre(data):
	re.sub(data["ecutwfc"]....)
def job1_post(data):
	print(something)
j1 = Job("job 1", 20, {"ecutwfc": 32.0, "file": "*.scf.in"}, job1_pre, job1_post)

j2 = ...
j3 = ...
B = Batch([j1, j2, j3]) # single node
B.run()
```

## crystalbase

### Class:
`Crystal`: Contains basis of some crystal structures (sc, fcc, bcc, ...) in different forms (vasp, qe, cart). Allows users to acquire these basis by functions given inside.

### Usage:
```python
from crystalbase import Crystal
```

1. 	Prepare the parameters:
	* `basis_dict`: *dict*, contains all basis of crystal structures and forms in real space.
	* `space`: *str*, 'x' or 'k', determines which space (real space or reciprocal space) is the users now interested in.
	* `lattice`: *str*, lattice type, e.g., 'sc', 'fcc', 'bcc', etc. Each material has its lattice structure, and the users should choose this parameter that correctly corresponds to the material.
	* `calc`: *str*, 'vasp', 'qe', or 'cart'. A crystal lattice can be expressed in different basis. This parameter determines which kind of basis do we want to express the crystal lattice.
	* `b`, `c`: *float*, the ratio of 2nd and 3rd lattice constants with 1st lattice constant. There is no `b` or `c` in a cubic lattice. However, one should give `b` or `c` for lattice 'st', 'bct', and 'base-co'.

2. 	Use `Crystal(space, lattice, calc, **latratio_dict).basis()` to get the basis you want.
	* `latratio_dict`: dictionary for the parameters `b` and `c`.