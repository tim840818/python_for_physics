#!/usr/bin/env python
## authors: Tim, Jake
import re, json
from os import listdir, path
"""
Usage:

from parse import Parser

1. 	Initialization:
		P = Parser() # This program automatically finds all the '*.in' files in current directory.

2. 	Functions
	1) 	Global functions: P.*(parameters), ex: P.add_ctrl(a, b), P.add_line(a, b, n, direction). Modifies ALL files.
	2) 	Local  functions: P.*_l(file, parameters), ex: P.add_ctrl(file, a, b), P.add_anchor_l(file, anchor, b). Modifies only the files stated in 'file' (can be a str, a list of str, or regex).

	Please refer to documentations for each function

3. 	Notification:
	1) 	Parameters called 'a' are matched using regex. On the other hand, parameters called 'b' are strings.
	2) 	Parameters called 'anchor' are regexes match the entire single line. Hence, do not put newlines(\n) into 'anchor'.
	3) 	Since 'a' and 'anchor' are regex, please use regex to express these parameters.

4. 	Examples:
	def format_dos(P, pwd):
		P.add_ctrl_l("{}.nscf.in".format(atoms), "occupations", "tetrahedra") if "/dos" in pwd else 0

	def format_title(P):
		P.add_line(r"&control", atoms+"\n", n="inf", direction="up")

	def format_crystal(P):
		P.del_line(r"B\s*=")
		P.del_line(r"C\s*=")
		cryst_str = "\n".join(["  "+" = ".join(alat) for alat in param_dict["CRYST"]])
		# P.replace_single_line(r"A\s*=", param_dict["CRYST"])
		P.replace_single_line(r"A\s*=", cryst_str)
"""

temp_global = "" # used for _handler()
class Parser:
	# useful constants
	scientific_notation = r"[+\-]?(?:0|[1-9]\d*)(?:\.\d*)?(?:[edE][+\-]?\d+)?"

	def __init__(self):
		self.flist = set(filter(lambda x: ".in" in x and "test_" not in x and path.isfile(x), listdir("."))) ## list of files for modification
		self.fdict = {}
		for file in self.flist: ## read the files and put each of them in self.dict
			f = open(file, "r")
			self.fdict[file] = f.read(); f.close()

	def reconstruct_files(self, test=False):
		"""Writes each file from self.fdict[file] for all files."""
		for file in self.fdict:
			f = open(f"test_{file}", "w") if test else open(file, "w")
			f.write(self.fdict[file]); f.close()

	def _get_files(self, file, use_regex):
		if type(file) is str:
			if not use_regex: return [file]
			else: return [f for f in self.fdict if re.match(file, f)]
		elif type(file) is list: 
			return file
		else: print("file not a string or list!"); assert 0

	@staticmethod
	def _handler(match):
		g1, g2 = match.group(1), match.group(2)
		if re.match(r"'.*'", g2): s = f"'{temp_global}'"
		else: s = f"{temp_global}"
		return g1 + s

	@staticmethod
	def _comment(match):
		"""Adds a comment(!) for a match without it; Removes it for a match with it."""
		m = match.group(0)
		# if comment already exists, remove comment
		if re.match(r"\s*!.*?", m): return re.sub(r"\s*!(.*)", r"\1", m)
		else: return "!" + m

	@staticmethod
	def _comment_force(match):
		"""Force the comment(!) to exist for any matches."""
		m = match.group(0)
		# if comment already exists, do nothing
		if re.match(r"\s*!.*?", m): return m
		else: return "!" + m

	@staticmethod
	def _uncomment_force(match):
		"""Force the comment(!) to disappear for any matches."""
		m = match.group(0)
		# if comment exists, remove it; else, do nothing
		if re.match(r"\s*!.*?", m): return re.sub(r"\s*!(.*)", r"\1", m)
		else: return m

	def has_comment_l(self, file: str, anchor): 
		"""Finds if there is a comment(!) in front of the 'anchor'.
		anchor: regex, the keyword for comment (usually 'degauss' or 'smearing')
		file: str, represents only ONE file, and cannot be a list.
		"""
		return re.search(r"\s*!.*?{}.*?".format(anchor), self.fdict[file])

	def add_ctrl_l(self, file, a: str, b: str, use_regex=False):
		"""Matches a = b, and modifies b."""
		filelist = self._get_files(file, use_regex)
		for f in filelist:
			match_str = r"({}\s*=\s*)({}|'.*'|\.true\.|\.false\.)".format(a, self.scientific_notation)
			global temp_global; temp_global = str(b)
			self.fdict[f] = re.sub(match_str, self._handler, self.fdict[f])

	def add_line_l(self, file, a: str, b: str, n: int, use_regex=False, direction="down"):
		"""Matches a, and replaces the next n lines into b."""
		filelist = self._get_files(file, use_regex); assert direction == "down" or direction == "up"
		amount_str = "{0,})" if n == "inf" else "{" + str(n) + "})"
		if direction == "down": match_str = r"(\s*{}.*\n)((?:.*(?:\n|$))".format(a) + amount_str
		else: match_str = r"((?:.*(?:\n|$))" + amount_str + r"(\s*{}.*\n)".format(a)
		for f in filelist:
			if direction == "down": self.fdict[f] = re.sub(match_str, r"\g<1>{}".format(b), self.fdict[f])
			else: self.fdict[f] = re.sub(match_str, r"{}\g<2>".format(b), self.fdict[f])

	def rep_line_l(self, file, a: str, b: str, n: int, use_regex=False, direction="down"):
		"""Same as add_line_l(), but a is deleted afterwards."""
		filelist = self._get_files(file, use_regex); assert direction == "down" or direction == "up"
		amount_str = "{0,})" if n == "inf" else "{" + str(n) + "})"
		if direction == "down": match_str = r"[^\S\n]*{}.*\n((?:.*(?:\n|$))".format(a) + amount_str # the () is (){n}
		else: match_str = r"((?:.*(?:\n|$))" + amount_str + r"\s*{}.*\n".format(a)
		for f in filelist:
			if direction == "down": self.fdict[f] = re.sub(match_str, b, self.fdict[f])
			else: self.fdict[f] = re.sub(match_str, b, self.fdict[f])

	def add_anchor_l(self, file, anchor: str, b: str, use_regex=False):
		"""Matches anchor, and then adds b after it. (same usage as add_line_l(), but not deleting any lines)"""
		filelist = self._get_files(file, use_regex)
		for f in filelist:
			self.fdict[f] = re.sub(r"(.*{}.*\n)".format(anchor), r"\g<1>{}\n".format(b), self.fdict[f])

	def add_comment_l(self, file, anchor: str, use_regex=False):
		"""Matches anchor, then un/comments the line with the anchor."""
		filelist = self._get_files(file, use_regex)
		for f in filelist:
			self.fdict[f] = re.sub(r"(^.*{}.*\n)".format(anchor), self._comment, self.fdict[f], flags=re.M)

	def force_comment_l(self, file, anchor: str, use_regex=False):
		"""Matches anchor, and forces the line with it to be commented(!)."""
		filelist = self._get_files(file, use_regex)
		for f in filelist:
			self.fdict[f] = re.sub(r"(^.*{}.*\n)".format(anchor), self._comment_force, self.fdict[f], flags=re.M)

	def force_uncomment_l(self, file, anchor: str, use_regex=False):
		"""Matches anchor, and forces the line with it to be uncommented(!)."""
		filelist = self._get_files(file, use_regex)
		for f in filelist:
			self.fdict[f] = re.sub(r"(^.*{}.*\n)".format(anchor), self._uncomment_force, self.fdict[f], flags=re.M)

	def del_line_l(self, file, anchor: str, use_regex=False):
		"""Matches anchor, and then deletes the entire line containing it."""
		filelist = self._get_files(file, use_regex)
		for f in filelist:
			self.fdict[f] = re.sub(r"^.*{}.*\n".format(anchor), "", self.fdict[f], flags=re.M)

	def replace_single_line_l(self, file, anchor: str, b: str, use_regex=False):
		"""Matches anchor, and replaces it with b. (b can be anything, including multiple lines.)"""
		filelist = self._get_files(file, use_regex)
		for f in filelist:
			self.fdict[f] = re.sub(r"^.*{}.*".format(anchor), b, self.fdict[f], flags=re.M)

	def simple_sub_l(self, file, a: str, b: str, use_regex=False):
		"""The simplest substitution. Does not make an assumptions at all."""
		filelist = self._get_files(file, use_regex)
		for f in filelist:
			re.sub(a, b, self.fdict[f])

	def find_ctrl_l(self, file, a: str, use_regex=False, one=False):
		"""Match a = b for all files and return a value (b) or a dictionary (match_dict[file] = b). If you can certify that b is the same in all the files, please set `one=True`."""
		filelist = self._get_files(file, use_regex); match_dict = {}
		for f in filelist:
			match_str = r"({}\s*=\s*)({}|'.*'|\.true\.|\.false\.)".format(a, self.scientific_notation)
			match = re.search(match_str, self.fdict[f])
			if one and match: return match.group(2)
			if match: match_dict[f] = match.group(2)
		return match_dict

	def change_prefix_l(self, file, a: str, b: str, use_regex=False):
		"""Matches "'.*a" or "^.*a", then replace it with "'ba" or "ba"."""
		filelist = self._get_files(file, use_regex)
		for f in filelist:
			self.fdict[f] = re.sub(r"(.*)(^|').*({})".format(a), r"\1\g<2>{}\3".format(b), self.fdict[f])

	## Global functions: for each global function, please refer to each single function.
	def add_ctrl(self, a: str, b: str):
		[self.add_ctrl_l(f, a, b) for f in self.flist]

	def add_line(self, a: str, b: str, n: int, direction:str ="down"):
		[self.add_line_l(f, a, b, n, direction=direction) for f in self.flist]

	def rep_line(self, a: str, b: str, n: int, direction:str ="down"):
		[self.rep_line_l(f, a, b, n, direction=direction) for f in self.flist]

	def add_anchor(self, anchor: str, b: str):
		[self.add_anchor_l(f, anchor, b) for f in self.flist]

	def add_comment(self, anchor: str):
		[self.add_comment_l(f, anchor) for f in self.flist]

	def force_comment(self, anchor: str):
		[self.force_comment_l(f, anchor) for f in self.flist]

	def force_uncomment(self, anchor: str):
		[self.force_uncomment_l(f, anchor) for f in self.flist]

	def del_line(self, anchor: str):
		[self.del_line_l(f, anchor) for f in self.flist]

	def replace_single_line(self, anchor: str, b: str):
		[self.replace_single_line_l(f, anchor, b) for f in self.flist]

	def change_prefix(self, a: str, b: str):
		[self.change_prefix_l(f, a, b) for f in self.flist]

	def simple_sub(self, a: str, b: str):
		[self.simple_sub_l(f, a, b) for f in self.flist]

	def find_ctrl(self, a: str, one=False):
		match_dict = {}
		for f in self.flist:
			match_str = r"({}\s*=\s*)({}|'.*'|\.true\.|\.false\.)".format(a, self.scientific_notation)
			match = re.search(match_str, self.fdict[f])
			if one and match: return match.group(2)
			if match: match_dict[f] = match.group(2)
		return match_dict


	def __str__(self):
		return f"files: {self.flist}"
