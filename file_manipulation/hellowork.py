#!/usr/bin/env python
## authors: Tim
"""
This program shows the sub directories of each working directory, provides options for more detail informations like used storage.
1. This program is written specifically for 'twchang'. It cannot be used in other systems or computers.
2. Press '-h' for instruction and help. Press '-v' to show only the files/dirs under 'twchang/vasp'. Press -q to show only the files/dirs under 'twchang/qe'. Press '-s' to show the used storage of 'twchang/vasp' or 'twchang/qe'.
"""
import os, re, argparse
from sys import argv
import subprocess as sub
from pprint import pprint

def cd(max_limit, directory: str="./"):
	""" This function recursively checks the sub directories from their parent directory, calculating the sum of the used storage of each file inside them if the user wants to check the storage.
	"""
	global current_total # total used storage
	dir_list = os.listdir(directory) # list sub-dirs/files of current dir (dir path)
	dir_path_list = [directory + f"/{m}" for m in dir_list] # list of paths of sub-dirs/files
	files = list(filter(lambda x: os.path.isfile(x), dir_path_list)) # filter -> list of 'files'
	dirs = list(filter(lambda x: os.path.isdir(x), dir_path_list)) # filter -> list of 'sub-dirs'

	if choice_storage:
		for file in files:
			current_total += os.path.getsize(file)
	else:
		for file in files:
			# print("{}: {}".format(file, os.path.getsize(file)))
			current_total += os.path.getsize(file)
		if current_total >= max_limit:  # There are many files in the directory; no need to check further
			# print("over limit!! exiting...")
			return False

	if not dir_path_list: # no files
		return True
	else:
		for nextdir in dirs:
			if not cd(max_limit, nextdir + "/"): return False
		return True

def sort_twdirlist(tw_dirlist):
	twdir_numlist = [int(re.search(r"\d+", tw_dir).group(0)) for tw_dir in tw_dirlist]
	twdir_numlist.sort()
	tw_dirlist = ["/data" + str(num) + "/twchang" for num in twdir_numlist]
	return tw_dirlist

if __name__ == "__main__":
	## argparse option
	agps = argparse.ArgumentParser(description='option')
	agps.add_argument('-q', '--qe', action='store_true', help='show informations for /qe')
	agps.add_argument('-v', '--vasp', action='store_true', help='show informations for /vasp')
	agps.add_argument('-s', '--storage', action='store_true', help='show used storage for chosen dirs')
	# agps.add_argument('-t', '--tk', type=str, choices=['y','Y'], help='type -t y/Y for tk.py') #, required=True
	args = agps.parse_args()
	choice_qe = args.qe; choice_vasp = args.vasp
	choice_storage = args.storage

	tw_dirlist = sub.check_output("find /data*/ -maxdepth 1 -name twchang", shell=True).decode("utf-8").split() # data*/twchang
	tw_dirlist = sort_twdirlist(tw_dirlist)

	## establish work_dirdict
	worklist = []
	if choice_qe ^ choice_vasp:
		worklist.append("vasp") if choice_vasp else worklist.append("qe")
	else: worklist = ["vasp", "qe"]
	work_dirdict = {tw_dir : {calc : sub.check_output(f"find {tw_dir} -maxdepth 1 -name {calc}", shell=True).decode("utf-8").strip() for calc in worklist} for tw_dir in tw_dirlist}
	# pprint(work_dirdict) # two level dict

	max_limit = 0.5 * 10**9 # 0.5 GB
	for tw_dir in work_dirdict:
		tw_dir_colour = re.sub(r"(data\d*)", r"\033[34m\g<1>\033[0m", tw_dir)
		print(f"{tw_dir_colour}:")
		for calc in work_dirdict[tw_dir]:
			dirpath = work_dirdict[tw_dir][calc]
			current_total = 0
			if dirpath == '':
				print(f"  \033[31mNo\033[0m '\033[34m{calc}\033[0m' in {tw_dir}"); continue
			else:
				flag = cd(max_limit, dirpath) # T or F
				if current_total < 1000:
					print(f"  \033[31mNo\033[0m work files in {dirpath}")
				else:
					ls_dirs = [f for f in os.listdir(dirpath) if os.path.isdir("/".join([dirpath, f]))]
					ls_str = ", ".join([f"\033[34m{file}\033[0m" for file in ls_dirs])
					print("  \033[32mWorking dirs\033[0m in {}: {}".format(dirpath, ls_str))
					if choice_storage:
						print("  \033[32mUsed storage\033[0m in {}: {:.2f} GB".format(dirpath, current_total/10**9))
			if choice_storage and (calc == "vasp" and len(work_dirdict[tw_dir]) == 2):
				print("  --------------------")
		# print(list(work_dirdict)[-1])
		print("-------------------------------------------------------")  if tw_dir != list(work_dirdict)[-1] else 0
