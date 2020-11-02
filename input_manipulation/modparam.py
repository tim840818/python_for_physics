#!/usr/bin/env python
## authors: Tim
"""
This program determines input parameters for further Quantum Espresso calculations. It only works for QE input files.
Usage:
(1) Edit atoms and param_dict below to set parameters.
(2) Go to the working directory in which all the input files are, execute this program by typing "python workparam.py x"; all the input parameters will be changed as desired.
"""
import os
from sys import path; path.insert(0, "../modules") # ~/bin
from parse import Parser

## parameters ######################################################
atoms = "H3S"
param_dict = {  # create dictionary for common parameters
##  control
	"prefix"      : 'q6k18f36',
	# "pseudo_dir"  : '/data2/twchang/q-e-qe-6.1.0/pseudo', "str"),
	"pseudo_dir"  : '/data3/twchang/qe/H3S/oncv_pbe/pseudo',
	"outdir"      : './tmp',
##  basic params
	"ibrav"       : 3,
	# "A"           : 2.984, 
	# "CRYST"       : "" + # list for lattice constants
	# "  " + "A = 3.768" + "\n" +
	# "  " + "C = 5.524"
	"CRYST"       : [ # list for lattice constants
	 ["A", "2.9985"],
	 # ["B", "5.3342"],
	 # ["C", "5.486"],
	]
	,
	"nat"         : 4,
	"ntyp" 	      : 2,
	"AMASS"       : [
	  1.008, # amass(1)
	 32.060, # amass(2)
	],
	# "POT"         : "" +
	# "Fe   55.845  Fe_ONCV_PBE_sr.upf" + "\n" +
	# "Se   78.971  Se_ONCV_PBE_sr.upf" #+ "\n" +
	"POT"         : [
	 "H    1.008  H_ONCV_PBE_sr.upf",
	 "S   32.060  S_ONCV_PBE_sr.upf",
	]
    ,
	"ecutwfc"     : 62.0, 
	"ecutrho"     : 62.0 * 10, 
	"occupations" : 'smearing', #  tetrahedra
	"degauss"     : 0.030,
	"smearing"    : 'gaussian',
	"ATOMPOS"     : [
	"H    0.500000000000000 -0.500000000000000  0.000000000000000",
	"H    0.000000000000000  0.500000000000000 -0.500000000000000",
	"H    0.500000000000000  0.000000000000000  0.500000000000000",
	"S    0.000000000000000  0.000000000000000  0.000000000000000",
	]
	,
	"KPOINTS"     : {
	 "{}.scf.in".format(atoms)     : "18 18 18  0 0 0",
	 "{}.scf.fit.in".format(atoms) : "36 36 36  0 0 0",
	 "{}.nscf.in".format(atoms)    : "24 24 24  0 0 0",
	},

##  phonon params
	"nq1"         : 6,
	"nq2"         : 6,
	"nq3"         : 6,
	"fildvscf"    : '{}dv'.format(atoms),
	"ndos" 	      : 600,
	# "fildyn" : '{}.dynG'.format(atoms), "str"),
	# "flfrq" : '{}.freq'.format(atoms), "
}
param_dict["flfrc"] = '{}.{}{}{}.fc'.format(atoms, param_dict["nq1"], param_dict["nq2"], param_dict["nq3"])
atom_rel_list = [".dynG", ".freq"]

####################################################################

def format_crystal(P):
	"""Formats the lattice constants with corresponding values in param_dict."""
	P.del_line(r"B\s*=")
	P.del_line(r"C\s*=")
	cryst_str = "\n".join(["  "+" = ".join(alat) for alat in param_dict["CRYST"]])
	# P.replace_single_line(r"A\s*=", param_dict["CRYST"])
	P.replace_single_line(r"A\s*=", cryst_str)
def format_amass(P, ntyp_old, ntyp):
	"""Formats the mass of atoms with corresponding values in param_dict."""
	[P.del_line(r"amass\({}\)".format(i)) for i in range(2, ntyp_old+1)]
	amass_list = param_dict["AMASS"]
	P.add_ctrl(r"amass\(1\)", str(amass_list[0]))
	amass_str = ""
	for i in range(2, ntyp):
		amass_str += "  amass({}) = {}\n".format(i, amass_list[i-1])
	amass_str += "  amass({}) = {}".format(ntyp, amass_list[ntyp-1])
	P.add_anchor(r"amass\(1\)", amass_str)
def format_pot(P, ntyp_old):
	"""Formats the potential string of each atom with the corresponding strings in param_dict."""
	P.add_line(r"ATOMIC_SPECIES", "", ntyp_old)
	pot_str = "\n".join(param_dict["POT"])
	P.add_anchor(r"ATOMIC_SPECIES", pot_str)
def format_atompos(P, nat_old):
	"""Formats the position string of each atom with the corresponding strings in param_dict."""
	P.add_line(r"ATOMIC_POSITIONS \{crystal\}", "", nat_old)
	atompos_str = "\n".join(param_dict["ATOMPOS"])
	P.add_anchor(r"ATOMIC_POSITIONS \{crystal\}", atompos_str)
def format_dos(P, pwd):
	"""Changes the parameter of 'occupations' to 'tetrahedra' of the file '*.nscf.in' under the folder '*/dos/'."""
	P.add_ctrl_l("{}.nscf.in".format(atoms), "occupations", "tetrahedra") if "/dos" in pwd else 0
def format_occupation(P, ls):
	"""Comments (add # in front of the string) the lines 'degauss' to 'smearing' if the parameter of 'occupations' is 'smearing'; else, uncomments the lines."""
	occup_list = ["degauss", "smearing"]
	ls_in = [file for file in ls if ".in" in file and "test_" not in file]
	for file in ls_in:
		occup = P.find_ctrl_l(file, "occupations", one=True)
		if occup == "'smearing'":
			[P.force_uncomment_l(file, r"{}\s*=".format(suboption)) for suboption in occup_list]
		else:
			[P.force_comment_l(file, r"{}\s*=".format(suboption)) for suboption in occup_list]
def format_scf(P, kpoint_dict, ls):
	"""Formats the kpoint string of each file with the corresponding string in 'KPOINTS' dict of param_dict."""
	for file in kpoint_dict:
		P.add_line_l(file, "K_POINTS automatic", kpoint_dict[file], 1) if file in ls else 0
def format_atoms(P):
	"""Add the string (atoms) in front of each string inside the atom_rel_list."""
	for atom_rel in atom_rel_list:
		P.change_prefix(atom_rel, atoms)
def format_title(P):
	"""Add '&control' in front of each file."""
	P.add_line(r"&control", atoms+"\n", n="inf", direction="up")

if __name__ == '__main__':
	pwd = os.getcwd(); ls = os.listdir(".")

	P = Parser()
	print(P)
	## grep values in original files
	ntyp_old = int(P.find_ctrl("ntyp", one=True))
	nat_old = int(P.find_ctrl("nat", one=True))
	## define new param
	ntyp = param_dict["ntyp"]
	kpoint_dict = param_dict["KPOINTS"]
	## format parameters with param_dict
	for param in param_dict:
		P.add_ctrl(param, str(param_dict[param]))
	format_crystal(P)
	format_amass(P, ntyp_old, ntyp)
	format_pot(P, ntyp_old)
	format_atompos(P, nat_old)
	format_dos(P, pwd)
	format_occupation(P, ls)
	format_scf(P, kpoint_dict, ls)
	format_atoms(P)
	format_title(P)
	## constructs new files with new params
	P.reconstruct_files() # test=True  to test_file
