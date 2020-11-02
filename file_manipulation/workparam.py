#!/usr/bin/env python
## authors: Tim
"""
This program finds and opens/executes the file 'modparam.py' for further processing.
1. Usage: Type "python workparam.py w/x" in command line; w -> edit 'modparam.py'; x -> execute 'modparam.py'.
2. This program is written specifically for 'twchang'. It cannot be used in other systems or computers.
"""
import sys, os, re, argparse
import subprocess as sub

def get_option():
	"""This function reads the option from sys.argv[1] (should be w/x) and return the option."""
	in_cmd = sys.argv
	if len(in_cmd) != 2:
		print("usage: python workparam.py option(w/x)")
		exit(1)

	option = in_cmd[1]
	if option not in ["w", "x"]:
		print("plz choose your option(w/x)"); exit(1)
	return option

def find_modparam(pwd_recursor):
	"""This function finds if the file 'modparam.py' in current directory. If not, the function checks its parent directories recursively until the file is found."""
	find_tag = sub.check_output(f"find {pwd_recursor} -maxdepth 1 -name modparam.py", shell=True).decode("utf-8")
	parent_pwd_tag = re.search(r"(.*twchang.*)/.*", pwd_recursor)
	if find_tag: return pwd_recursor
	elif parent_pwd_tag:
		parent_pwd_recursor = parent_pwd_tag.group(1)
		return find_modparam(parent_pwd_recursor) # go to parent dir and find again
	else: return False # /data2/twchang (the 'ancestor' dir) --> dead (cannot find it even in this dir)


if __name__ == "__main__":
	## get option(w/x) and pwd
	option = get_option()
	pwd = os.getcwd(); pwd_recursor = pwd
	## find modparam.py from pwd and parents of pwd
	workingdir = find_modparam(pwd_recursor)
	if not workingdir:
		# print(pwd, pwd_recursor)
		print("Cannot find 'modparam.py' in all parent dirs from the pwd. Exiting..."); exit(1)
	print("working directory: {}".format(workingdir))
	workfile = workingdir + "/modparam.py"
	## option: choose to write or execute modparam.py
	if option == "w":
		sub.run("rsub {}".format(workfile), shell=True)
	if option == "x":
		sub.run("python {}".format(workfile), shell=True)
