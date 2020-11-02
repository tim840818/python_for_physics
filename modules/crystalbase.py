#!/usr/bin/env python
## authors: Tim
"""This package contains basis of some crystal structures (sc, fcc, bcc, ...) in different forms (vasp, qe, cart). It allows users to acquire these basis by functions given in the package.

Parameters:

basis_dict: dict, contains all basis of crystal structures and forms in real space.
space: str, 'x' or 'k', determines which space (real space or reciprocal space) is the users now interested in.
lattice: str, lattice type, e.g., 'sc', 'fcc', 'bcc', etc. Each material has its lattice structure, and the users should choose this parameter that correctly corresponds to the material.
calc: str, 'vasp', 'qe', or 'cart'. A crystal lattice can be expressed in different basis. This parameter determines which kind of basis do we want to express the crystal lattice.
b, c: float, the ratio of 2nd and 3rd lattice constants with 1st lattice constant. There is no b or c in a cubic lattice. However, one should give b or c for lattice 'st', 'bct', and 'base-co'.

Usage:
from crystalbase import Crystal

1. Prepare the parameters stated above.
2. Use Crystal(space, lattice, calc, **latratio_dict).basis() to get the basis you want.
3. latratio_dict: dictionary for the parameters b and c.
"""
import numpy as np

class Crystal:
	identity_matrix = [ ## general constant (DO NOT CHANGE)
	[ 1.00, 0.00, 0.00],
	[ 0.00, 1.00, 0.00],
	[ 0.00, 0.00, 1.00]
	]
	def __init__(self, space, lattice, calc, **kwargs):
		self.space = space # x-space or k-space
		self.lattice = lattice # lattice type (ex: bcc, fcc, ...)
		self.calc = calc # calculation meethod (ex: vasp, qe)
		# self.latratio = kwargs.setdefault("latratio", {"b": False, "c": False})
		# self.b = self.latratio["b"]
		# self.c = self.latratio["c"]
		self.b = kwargs.setdefault("b", False)
		self.c = kwargs.setdefault("c", False)
		# print(self.b, self.c)
		self.basis_dict = {
				"sc": {
					"vasp": Crystal.identity_matrix,
					"qe"  : Crystal.identity_matrix,
					"cart": Crystal.identity_matrix,
				},
				"fcc": {
					"vasp" : 
						[[ 0.00, 0.50, 0.50],
						 [ 0.50, 0.00, 0.50],
						 [ 0.50, 0.50, 0.00]],
					"qe" : 
						[[-0.50, 0.00, 0.50],
						 [ 0.00, 0.50, 0.50],
						 [-0.50, 0.50, 0.00]],
					"cart": Crystal.identity_matrix,
				},
				"bcc": {
					"vasp" : 
						[[-0.50, 0.50, 0.50],
						 [ 0.50,-0.50, 0.50],
						 [ 0.50, 0.50,-0.50]],
					"qe" : 
						[[ 0.50, 0.50, 0.50],
						 [-0.50, 0.50, 0.50],
						 [-0.50,-0.50, 0.50]],
					"cart": Crystal.identity_matrix,
				},
				"st": {
					"vasp" : 
						[[ 1.00, 0.00, 0.00],
						 [ 0.00, 1.00, 0.00],
						 [ 0.00, 0.00, 1.00 * self.c]],
					"qe" : 
						[[ 1.00, 0.00, 0.00],
						 [ 0.00, 1.00, 0.00],
						 [ 0.00, 0.00, 1.00 * self.c]],
					"cart": Crystal.identity_matrix,
				},
				"bct": {
					"vasp" : 
						[[-0.50, 0.50, 0.50 * self.c],
						 [ 0.50,-0.50, 0.50 * self.c],
						 [ 0.50, 0.50,-0.50 * self.c]],
					"qe" : 
						[[ 0.50,-0.50, 0.50 * self.c],
						 [ 0.50, 0.50, 0.50 * self.c],
						 [-0.50,-0.50, 0.50 * self.c]],
					"cart": Crystal.identity_matrix,
				},
				"base-co": {
					"vasp" : 
						[[ 0.50,-0.50 * self.b, 0.00],
						 [ 0.50, 0.50 * self.b, 0.00],
						 [ 0.00, 0.00, 1.00 * self.c]],
					"qe" : 
						[[ 0.50, 0.50 * self.b, 0.00],
						 [-0.50, 0.50 * self.b, 0.00],
						 [ 0.00, 0.00, 1.00 * self.c]],
					"cart": Crystal.identity_matrix,
				},
			}
	def _checklat(self):
		"""Check if the lattice is correct. If the lattice is not cubic but one does not give the value of b or c, returns false."""
		check_flag = True
		if self.lattice == "st" or self.lattice == "bct":
			if not self.c: print("You chose 'tetragonal' lattice but didn't give lattice parameter 'c'."); check_flag = False
		elif self.lattice == "bace-co":
			if not self.b: print("You chose 'orthorhombic' lattice but didn't give lattice parameter 'b'."); check_flag = False
			if not self.c: print("You chose 'orthorhombic' lattice but didn't give lattice parameter 'c'."); check_flag = False
		return check_flag

	def basis(self): # return a matrix in np-array form
		"""Returns an np-array matrix for the decided parameters."""
		if self._checklat():
			x_matrix = np.array(self.basis_dict[self.lattice][self.calc])
		else: print("lattice parameter error, exiting..."); exit(1)
		if self.space == "x":
			return x_matrix
		elif self.space =="k":
			k_matrix = np.transpose(np.linalg.inv(x_matrix))
			return k_matrix

# print(self.basis_dict["fcc"])

# if __name__ == "__main__":
	# matrix_x_bcc_vasp = Crystal("x", "bcc", "vasp")
	# print("matrix_x_bcc_vasp:")
	# print(Crystal.basis(matrix_x_bcc_vasp))

	# matrix_k_bcc_vasp = Crystal("k", "bcc", "vasp")
	# print("matrix_k_bcc_vasp:")
	# print(Crystal.basis(matrix_k_bcc_vasp))

	# matrix_x_st_vasp = Crystal("x", "st", "vasp",**{"c": 1.5}) # ,c = 1.5
	# print("matrix_x_st_vasp:")
	# print(Crystal.basis(matrix_x_st_vasp))
	# print(matrix_x_st_vasp.basis())
