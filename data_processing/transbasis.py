#!/usr/bin/env python
## authors: Tim
"""
This file reads the parameters from 'atoms.json' and transforms the coordinates of the crystal in different basis from the parameters. It will create files: 'atompos-out.dat' for x-space, 'kpath-out.dat', 'qpath-out.dat', and 'kdist.dat' for k-space.
1. It only works for several crystal structures; user should prepare the file 'atoms.json' and its parameters accordingly.
2. Usage: prepare 'atoms.json', execute this program, and you'll get what you need.
"""
import numpy as np
import jstyleson as json # pip install jstyleson
import os
from sys import path; path.insert(0, "../modules") # /home/twchang/bin
from crystalbase import Crystal

def transbasis(vector, i_basis, f_basis):
	"""Transforms a vector by matrix multiplication.
	i_basis: np array, intial basis
	f_basis: np array, final basis
	"""
	return np.matmul(vector,np.matmul(i_basis, np.linalg.inv(f_basis)))

def process_atompos(structure, atominfo_dict, latratio_dict):
	"""Transforms atom positions from different basis in real space (x-space) and writes the new postions into the file 'atompos-out.dat'; return True when the work is done.
	
	Parameters
	---------------
	structure: str, the lattice structure in atoms_dict (from atoms.json), namely, atoms_dict["lattice"]["structure"].
	atominfo_dict: dict, the dictionary that gives information of positions of atoms and basis for transformation, namely, atoms_dict["atoms"].
	latratio_dict: dict, gives the ratio between other lattice consts. and the primary lattice const.
	* atoms_dict is the dictionary that is directly loaded from the file 'atoms.json', please refer to it for more details.
	"""
	atominfo_list = atominfo_dict["pos"]
	atom_calc_initial = atominfo_dict["calc_initial"]; atom_calc_final = atominfo_dict["calc_final"]
	atomtag_list = []; atompos_list = []
	for i in range(len(atominfo_list)):
		atomtag = list(atominfo_list[i])[0]
		atomtag_list.append(atomtag)
		atompos_list.append(atominfo_list[i][atomtag])
	print(f"You are using '{atom_calc_initial}' initial basis; you want to convert it to '{atom_calc_final}' basis")
	fout = open("atompos-out.dat", 'w')
	if atom_calc_initial == atom_calc_final:
		print("The initial structure is the same with the final structure; no need to transform")
		for i in range(len(atompos_list)):
			fout.write("{:>2}  {:18.15f} {:18.15f} {:18.15f}\n".format(atomtag_list[i], atompos_list[i][0], atompos_list[i][1], atompos_list[i][2]))
	else:
		i_basis = Crystal("x", structure, atom_calc_initial, **latratio_dict).basis()
		f_basis = Crystal("x", structure, atom_calc_final, **latratio_dict).basis()
		for i in range(len(atomtag_list)):
			newpos = list(transbasis(np.array(atompos_list[i]), i_basis, f_basis))
			fout.write("{:>2}  {:18.15f} {:18.15f} {:18.15f}\n".format(atomtag_list[i], newpos[0], newpos[1], newpos[2]))
	fout.close(); return True

def process_kgrid(structure, A, kgridinfo_dict):
	"""Transforms k-vectors from different basis in reciprocal space (k-space) and writes the new k-vectors into the files 'kpath-out.dat', 'qpath-out.dat', and 'kdist.dat'; return True when the work is done.

	Parameters
	---------------
	structure: str, the lattice structure in atoms_dict (from atoms.json), namely, atoms_dict["lattice"]["structure"].
	A: float, the primary lattice const., namely, atoms_dict["lattice"]["a"].
	kgridinfo_dict: dict, the dictionary that gives information of k-vectors of symmetry points and basis for transformation, namely, atoms_dict["kgrid"].
	* atoms_dict is the dictionary that is directly loaded from the file 'atoms.json', please refer to it for more details.
	"""
	weight_norm = round(40 * 2*3.1416/A)
	kgridinfo_list = kgridinfo_dict["grid"]
	kgrid_calc_initial = kgridinfo_dict["calc_initial"]; kgrid_calc_final = kgridinfo_dict["calc_final"]
	kgridtag_list = []; kgridpos_list = []
	for i in range(len(kgridinfo_list)):
		kgridtag = list(kgridinfo_list[i])[0]
		kgridtag_list.append(kgridtag)
		kgridpos_list.append(kgridinfo_list[i][kgridtag])
	print(f"You are using '{kgrid_calc_initial}' initial basis; you want to convert it to '{kgrid_calc_final}' basis")
	fout_dist = open("kdist.dat", 'w')
	i_basis = Crystal("k", structure, kgrid_calc_initial, **latratio_dict).basis()
	f_basis = Crystal("k", structure, kgrid_calc_final, **latratio_dict).basis()
	cart_basis = Crystal("k", structure, "cart", **latratio_dict).basis()
	## preparing new k-grid, new-qgrid, and dist_list
	k_final_list = []; q_final_list = []; weight_list = []
	for i in range(len(kgridpos_list)):
		k = np.array(kgridpos_list[i])
		k_final_np = transbasis(k, i_basis, f_basis)   ; k_final_list.append(list(k_final_np))
		k_cart_np  = transbasis(k, i_basis, cart_basis); q_final_list.append(list(k_cart_np))
		if i == 0: k_new = k_cart_np
		else:
			k_old = k_new
			k_new = k_cart_np
			kdist = np.linalg.norm(k_new - k_old)
			fout_dist.write("{:.5f}\n".format(kdist))
			weight = int(max(1, round(kdist * weight_norm)))
			weight_list.append(weight)
	weight_list.append(1)
	fout_dist.close()
	fout_kpath = open("kpath-out.dat", 'w'); fout_qpath = open("qpath-out.dat", 'w')
	for i in range(len(k_final_list)):
		newk = k_final_list[i]; newq = q_final_list[i]
		fout_kpath.write(" {: .10f}  {: .10f}  {: .10f}  {:2d}  !{}\n".format(newk[0], newk[1], newk[2], weight_list[i], kgridtag_list[i]))
		fout_qpath.write(" {: .10f}  {: .10f}  {: .10f}  {:2d}  !{}\n".format(newq[0], newq[1], newq[2], weight_list[i], kgridtag_list[i]))
	fout_kpath.close(); fout_qpath.close()
	return True

if __name__ == "__main__":
	## load json file
	print("This program needs an input file 'atoms.json', please make sure the file is ready.")
	if not "atoms.json" in os.listdir(): print("There's no 'atom.json'! Please prepare one."); exit(1)
	atoms_json_file = open("atoms.json", "r")
	atoms_dict = json.load(atoms_json_file); atoms_json_file.close()

	## handling basic structure informations of the compund; atoms_dict["lattice"]
	basicinfo_dict = atoms_dict["lattice"]
	atoms = basicinfo_dict["atoms"]
	structure = basicinfo_dict["structure"]
	A = basicinfo_dict["a"] # the lattice constant
	latratio_dict = {}
	for i in ["b", "c"]:
		try: latratio_dict[i] = basicinfo_dict[i] / A
		except KeyError: continue
	# b_ratio = basicinfo_dict["b"] / A; c_ratio = basicinfo_dict["c"] / A
	print(f"Your compound is '{atoms}', and the structure is '{structure}'")

	## handling basis transformation of atoms (x-space)
	atominfo_dict = atoms_dict["atoms"]
	print("Now processing atompos transformation...")
	if process_atompos(structure, atominfo_dict, latratio_dict):
		print("Atompos process finished, 'atompos-out.dat' created.")

	## handling basis transformation of k/q-grid (k-space)
	kgridinfo_dict = atoms_dict["kgrid"]
	print("Now processing kgrid transformation...")
	if process_kgrid(structure, A, kgridinfo_dict):
		print("K-grid process finished, 'kpath-out.dat', 'qpath-out.dat', and 'kdist.dat' created.")
