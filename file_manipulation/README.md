#  File Manipulation
The programs in this folder are mainly for file-manipulating. They show details or paths of working files/directories, open/execute/clean specified files/dirs, etc.

## `clean.py`
Finds and displays the specified files/dirs that users want to delete, and allows users to choose which to delete.

### Usage
1. This program only works in linux environment.

2. Name of files/dirs can be written in glob; the program will express all the related files and directories in detail.

3. You can choose three options (y/n/c) to decide how to clean the files/dirs.
	* 'y' -> the program will delete all the listed files/dirs after the countdown.
	* 'n' -> the program will stop, no files will be deleted.
	* 'c' (choose by oneself) -> The program will ask you to enter what you want to delete (please enter the whole name this time), and then delete them after the countdown.

4. Please be aware that all the sub-directories of the chosen dirs will be removed after the 3-second countdown. You can press `ctrl + z` or `ctrl + c` to stop it.


## `hellowork.py`
Shows the sub directories of each working directory, provides options for more detail informations like used storage.

### Usage
1. This program is written specifically for `twchang`. It may fail in other environments or users.
2. Command line options of this program:
	* Type `-h` for instruction and help.
	* Type `-v` to show only the files/dirs under `twchang/vasp`.
	* Type `-q` to show only the files/dirs under `twchang/qe`.
	* Type `-s` to show the used storage of `twchang/vasp` or `twchang/qe`.


## `workparam.py`
Finds and edits/executes the program `modparam.py` for further steps.

### Usage
1. This program is written specifically for `twchang` and QE-users. Please be sure you have `modparam.py` and corresponding QE-input-files.
2. Type `python workparam.py w/x` in command line.
	* `w` -> edit `modparam.py` with Sublime Text.
	* `x` -> execute `modparam.py`.