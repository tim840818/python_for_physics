#!/usr/bin/env python
## authors: Tim
"""This program performs a numerical integration from the phonon DOS file '*.phonon.dos' and calculates the phonon contribution of heat capacity. The results are written into two files: 'Cv_ph.dat' and 'Cv-T_ph.dat'.
1. The integration formula: c_v(T) = int[f(w, T) * D(w)dw]. f(w, T): integration function, D(w): phonon DOS function
2. You should prepare the file whose name is '*.phonon.dos' to execute this file.
"""
import numpy as np
import math, os
from decimal import Decimal

# ## input parameters ###
# n_compound = 1 ## how many # of compounds in a primitive cell (for H3S: 1, for FeSe: 2)
# # T_list = np.arange(5.0, 250.1, 5) # long range T (5~250 K)
# T_list = np.arange(4.0, 25.1, 0.5) # short range T (4~25 K)
# #######################

## universal constants
h = Decimal(6.626e-34); hbar = h / (Decimal(2)*Decimal(math.pi))  ## Planck constants
k = Decimal(1.3807e-23)  ## Boltzmann constant
N_mol = Decimal(6.022e23)  ## Avogadro constant

def get_input():
	"""Gets parameters n_compound and T_list for the program from users' inputs.
	n_compound: int, the number of compounds in a primitive cell (for H3S: 1, for FeSe: 2).
	T_list: np array, array of temperatures with range
	"""
	print("Please enter how many compounds are in a cell (e.g., FeSe: 2): ", end="")
	while True:
		try:
			n_compound = int(input())
			if n_compound <= 0: print("Please enter a positive integer", end="")
			else: break
		except:
			print("Please enter a positive integer", end="")
	print("Please enter the temperature range and the interval to form a sequence. (Form: 'lowT highT interval', seperate them by space):")
	while True:
		T_string = input()
		T_list_tmp = T_string.strip().split()
		try:
			T_low = float(T_list_tmp[0]); T_high = float(T_list_tmp[1]) + 0.1; T_interval = float(T_list_tmp[2])
			T_list = np.arange(T_low, T_high, T_interval); break
		except:
			print("Please enter 3 numbers as 'lowT highT interval' seperated by space:")
	return n_compound, T_list

def cv_formula(w1, w2, y1, y2, T):
	"""This function calculates the value 'f(w) * D(w) * dw' for each w. w and D(w) is obtained from the average of the adjacent data.

	Parameters
	---------------
	w1, w2: frequencies of two adjacent data points
	y1: DOS of w1, y2: DOS of w2. 
	T: temperature
	"""
	w1 = Decimal(w1) ; w2 = Decimal(w2)
	y1 = Decimal(y1) ; y2 = Decimal(y2)     # D(w1), D(w2)
	w_delta = w2 - w1                       # dw
	w_avg = Decimal(0.5) * (w1 + w2)        # w ~ 0.5 * (w1 + w2)
	y_avg = Decimal(0.5) * (y1 + y2)        # D(w) ~ 0.5 * (D(w1) + D(w2))
	beta_hbar_w = hbar * w_avg / (k * T)
	exp_w = Decimal.exp(beta_hbar_w)
	multiple = w_delta * y_avg * beta_hbar_w**Decimal(2) * exp_w / (exp_w - 1)**Decimal(2)  # D(w)dw * f(w, T)
	return multiple

def cv_int(x_data, y_data, T):
	"""This function calculates the integral by discretely summing the results of 'cv_formula'.

	Parameters
	---------------
	x_data: list of frequencies of data.
	y_data: list of phonon DOS of data. y_data[i]: phonon DOS corresponding to x_data[i]
	T: temperature
	"""
	cv = Decimal(0)
	for i in range(len(x_data)):
		if i == 0: continue
		else:
			cv += cv_formula(x_data[i-1], x_data[i], y_data[i-1], y_data[i], T)
			# print("yay")
	cv = cv * k
	return cv

if __name__ == "__main__":
	## reads the file from the current directory
	files = os.listdir(".")
	files_ph = [file for file in files if "phonon.dos" in file]
	files_num = len(files_ph)
	if files_num == 0:
		print("No '*.phonon.dos' files in this directory, exiting..."); exit(1)
	elif files_num > 1:
		print("More than one '*.phonon.dos' files in this directory, exiting..."); exit(1)
	else:
		file = files_ph[0]
	print("Your phdos file is {}".format(file))
	fin = open(file, 'r')
	fin_lines = fin.readlines()

	## get input parameters
	n_compound, T_list = get_input()

	## creates data lists from the file
	x_data = []; y_data = []
	for line in fin_lines:
		line = line.strip()
		if line:
			datas = line.split()
			# print(datas)
			if datas[0] != "#":
				x, y = float(datas[0]), float(datas[1])
				x_data.append(x); y_data.append(y)

	w_data = [x * 2*math.pi / 33.356 * 10**12 for x in x_data]
	y_data = [y / (2*math.pi / 33.356 * 10**12) for y in y_data]

	## Writes the calculation results into output files
	fout = open("Cv_ph.dat", 'w')
	fout.write("# T(K)  Cv_mol(mJ/K-mol)  Beta(mJ/K^4-mol)\n")
	fout1 = open("Cv-T_ph.dat", 'w')
	fout1.write("# T^2(K^2)  Cv/T(mJ/mol-K^2)\n")
	for T in T_list:
		T = Decimal(T)
		cv = cv_int(w_data, y_data, T) # heat capacity per each cell
		cv_mol = cv / Decimal(n_compound) * N_mol * Decimal(1000) # 2 FeSes per cell; "N_mol" molecules per mole; unit: mJ/K-mol
		beta = cv_mol / T ** Decimal(3) #*1000

		print("T = {} (K). Calculated Cv = {:.4e} (J/K-cell); Cv_mol = {:.4f} (mJ/K-mol). Beta = {:.4f} (mJ/K^4-mol)".format(T, cv, cv_mol, beta))
		fout.write("  {:4.1f}    {:9.4f}           {:.4f}\n".format(T, cv_mol, beta))
		fout1.write("  {:6.2f}    {:.4e}\n".format(T**Decimal(2), cv_mol/T))
