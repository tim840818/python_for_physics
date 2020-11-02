#!/usr/bin/env python
## authors: Tim
"""
This program normalizes the output data regarding electrons (electron bands/density of states) by the Fermi level; for k-points (or q-points in data regarding phonons), it normalizes them to [0, 1].
1. This program is written specifically for QE users and files which have "/qe" as their parent directory. It can process a file each time.
2. Usage: prepare the output file (band, dos, phonon dispersion) and execute this program, follow the instructions and yuor file will be normalized as you wish.
"""
import re, sys, os, argparse, math
import subprocess as sub
import numpy as np

def get_atoms(choice_qe: bool):
	"""Checks if the files are from QE calculations and returns the string (atoms). If choice_qe == False and 'qe/' is not the parent dir of current dir, exits the program."""
	pwd = os.getcwd()
	if "qe" in pwd:
		atoms = re.search(r"qe/(.*?)/",pwd).group(1)
		print(f"Current 'atoms': {atoms}; is it right ([y]/n)? ", end="")
		while True:
			choice = input()
			if choice == "y" or choice == "": return atoms
			elif choice == "n":
				atoms = input("Please input 'atoms': "); return atoms
			else: print("Plz enter 'y' or 'n': ", end="")
	elif choice_qe:
		print(f"You are not in the 'qe'-dir but switch on the qe option. Current directory:{pwd}")
		atoms = input("Please input 'atoms': "); return atoms
	else:
		print("This program only works under 'qe' directory; you're not in here."); exit(1)

def get_mode():
	"""Asks the users to input the mode (band/phband/dos), which is the type of the output file, and returns it as a string."""
	print("Please choose the file type that you want to normalize ('band'/'phband'/'dos'): ", end='')
	while True:
		mode = input()
		if   mode == "b"   or mode == "band"  : return "band"
		elif mode == "pb"  or mode == "phband": return "phband"
		elif mode == "d"   or mode == "dos"   : return "dos"
		elif mode == "phd" or mode == "phdos" :
			print("phdos-files don't need to be normalized; if you wanna change the unit, plz try other programs."); exit(1)
		else: print("Plz enter 'band'/'b', 'phband'/'pb', or 'dos'/'d': ", end="")
def get_files(file_list, mode):
	"""Searches the files that contains keywords (bands.dat.gnu, freq.plot, or S.dos) and asks the users to enter the filename (just one). Returns the filename as file (str)."""
	file_set = set(file_list)
	if "band" in mode:
		band_all_set = set(["bands.dat.gnu", "freq.plot"])
		band_file_set = file_set & band_all_set ; remain_file_set = file_set - band_all_set
		files_str = ", ".join([f"\033[32m{b}\033[0m" for b in band_file_set]) + "; " + ", ".join(remain_file_set)
	if mode == "dos":
		dos_all_set = set(["S.dos"])
		dos_file_set = file_set & dos_all_set ; remain_file_set = file_set - dos_all_set
		files_str = ", ".join([f"\033[32m{d}\033[0m" for d in dos_file_set]) + "; " + ", ".join(remain_file_set)
	print(f"Files in the directory: {files_str}"); file = input("Please choose your file (type one only): ")
	return file

def stretch(number, scale):
	"""Stretches the reference lines according to the scale (usually 10, 50 or 100) so they look prettier in graphs.
	If number is 184.23 and scale is 100, returns  200.
	If number is -73.52 and scale is  50, returns -100.
	"""
	if number >= 0:
		return scale * math.ceil(number / scale)
	else:
		return scale * math.floor(number / scale)

def findmaxmin(input_file):
	"""Checks the maximum and minimum of the file by executing check_maxmin.py; returns them as Emax, Emin."""
	E_list = sub.check_output("check_maxmin.py {}".format(input_file), shell=True).decode("utf-8")
	Emax = float(re.search(r"Maximum\s*:\s*(([+-]|\s)\d*\.\d+)", E_list).group(1))
	Emin = float(re.search(r"Minimum\s*:\s*(([+-]|\s)\d*\.\d+)", E_list).group(1))
	return Emax, Emin

def grep_fermi(atoms):
	"""Gets the Fermi energy from the file *.scf.out in this directory; returns it as E_fermi."""
	lfermi = sub.check_output("grep Fermi {}.scf.out".format(atoms), shell=True).decode("utf-8") # the Fermi energy is    17.4819 ev
	E_fermi_re = re.search(r".*Fermi energy is\s*([+-]?\d*\.?\d*).*", lfermi)
	E_fermi = float(E_fermi_re.group(1))
	return E_fermi

def make_knorm(fin_dist):
	"""Reads fin_dist (list of strings) and returns the kpoints_norm (sum of data) and kpoints_line_norm (normalized to [0, 1] by kpoints_norm).

	Input Parameters
	--------------------
	fin_dist: list of str, data of 'kdist.dat'.

	Output Parameters
	--------------------
	kpoints_norm: float, sum of data in fin_dist (transformed into floats before the summation)
	kpoints_line_norm: list of float, normalized list of fin_dist (transformed into floats first) by dividing them by kpoints_norm. The numbers of the list goes from 0.0 to 1.0.
	"""
	kpts_dist = 0.0
	kpts_line_dist = [0.0]
	for i in range(len(fin_dist)):
		dist = float(fin_dist[i])
		kpts_dist += dist
		kpts_line_dist.append(kpts_dist)
	kpoints_norm = kpts_dist
	kpoints_line_norm = [kpts/kpoints_norm for kpts in kpts_line_dist]
	return kpoints_norm, kpoints_line_norm

def normbands(line, E_fermi, kpoints_norm):
	"""Normalizes each line of the data regarding bands by E_fermi and kpoints_norm and returns it as a formatted string. Devides the x_data of the line by kpoints_norm and subtracts the y_data of the line by E_fermi.

	Input Parameters
	--------------------
	line: str, each 'line' of the input file; contains x_data as kpoint-distance and y_data as energy (or frequency).
	E_fermi: float, please refer to func. 'grep_fermi'.
	kpoints_norm: float, please refer to func. 'make_knorm'.
	"""
	ls = line.split()
	if len(ls) == 2:
		x = float(ls[0])/kpoints_norm
		y = float(ls[1])-E_fermi
		line = "    {:.4f}  {: 8.4f}\n".format(x,y) # :P
	return line

def normdos(line, E_fermi):
	"""Normalizes each line of the data regarding dos by E_fermi and returns it as a formatted string. Subtracts the x_data of the line by E_fermi.

	Input Parameters
	--------------------
	line: str, each 'line' of the input file; contains x_data as energy and y_data as dos.
	E_fermi: float, please refer to func. 'grep_fermi'.
	"""
	ls = line.split()
	if len(ls) == 3:
		ls[0] = float(ls[0])-E_fermi
		line = " {: 7.3f}  {}  {}\n".format(ls[0], ls[1], ls[2])
	return line

if __name__ == "__main__":
	## argparse option
	agps = argparse.ArgumentParser(description='qe option')
	agps.add_argument('-q', '--qe', action='store_true', help='open the qe option anyway')
	args = agps.parse_args(); choice_qe = args.qe
	## get files, atoms, mode
	file_list = [file for file in os.listdir(".") if os.path.isfile(f"./{file}")]
	atoms = get_atoms(choice_qe)
	mode = get_mode(); print("mode: ", mode) # band, phband, dos
	## check and confirm the input files for the program
	if "band" in mode and "kdist.dat" not in file_list:
		print("This program cannot normalize band-files without 'kdist.dat'."); exit(1)
	input_file = get_files(file_list, mode)
	## check if fermi energy is needed or not
	E_fermi = 0 if mode == "phband" else grep_fermi(atoms)
	## Start the work in different modes:
	fin = open(input_file, "r")
	fmax, fmin = findmaxmin(input_file)
	fout = open("{}-qe_{}.dat".format(atoms, mode), "w")
	if "band" in mode:
		fin_dist = open("kdist.dat", 'r').readlines()
		kpoints_norm, kpoints_line_norm = make_knorm(fin_dist)
		Emax_norm, Emin_norm = fmax-E_fermi, fmin-E_fermi
		# Emax_ceil, Emin_floor = stretch(Emax_norm, 50), stretch(Emin_norm, 50) if "ph" in mode else stretch(Emax_norm, 10), stretch(Emin_norm, 10)
		if "ph" in mode:
			Emax_ceil, Emin_floor = stretch(Emax_norm, 50), stretch(Emin_norm, 50)
		else:
			Emax_ceil, Emin_floor = stretch(Emax_norm, 10), stretch(Emin_norm, 10)
		for k_norm in kpoints_line_norm:
			for E_stretch in [Emin_floor, Emax_ceil]:
				fout.write("    {:.4f}  {: 8.4f}\n".format(k_norm, E_stretch))
			fout.write("\n")
		fout.write("    0.0000  0.0000\n    1.0000  0.0000\n\n")
		for line in fin:
			line = normbands(line, E_fermi, kpoints_norm)
			fout.write(line)
	if mode == "dos":
		##  writing fermi line into file
		f_ceil, f_floor = stretch(fmax, 5), stretch(fmin, 1)
		for dos_stretch in [f_floor, f_ceil]:
			fout.write("   0.000  {: .4f}\n".format(dos_stretch))
		fout.write("\n")
		for line in fin:
			line = normdos(line, E_fermi)
			fout.write(line)
