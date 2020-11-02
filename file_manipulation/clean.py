#!/usr/bin/env python
## authors: Tim
"""
This program finds and displays the specified files/dirs that users want to delete, and allows users to choose which to delete.
1. This program only works in linux environment.
2. Name of files/dirs can be written in glob; the program will express all the related files and directories in detail.
3. You can choose three options (y/n/c) to decide how to clean the files/dirs. 'y' -> the program will delete all the listed files/dirs after the countdown. 'n' -> the program will stop, no files will be deleted. 'c' (choose by oneself) -> The program will ask you to enter what you want to delete (please enter the whole name this time), and then delete them after the countdown.
4. Please be aware that all the sub-directories of the chosen dirs will be removed after the 3-second countdown. You can press 'ctrl+z' to stop it.
"""
import subprocess as sub
from time import sleep
import sys

def arg_process(in_cmd) -> bool:
	"""Reads the sys.argv as in_cmd. Exits when sys.argv is wrong. Returns True or False for different conditions."""
	if len(in_cmd) > 2: print("Usage: clean.py (file/dir)"); exit(1)
	elif len(in_cmd) == 2: return True # have arg
	else: return False # no arg

def countdown():
	"""Countdowns for three seconds."""
	for t in range(3):
		print(".", end = "", flush = True)
		sleep(1)
	print("")
	
def process_rmlist(rm_list):
	"""Removes the files/dirs from rm_list"""
	print("Processing", end = " ")
	countdown()
	for file in rm_list:
		sub.run("rm -r {}".format(file), shell=True)
	print("Done.")

if __name__ == "__main__":
	## arg process
	in_cmd = sys.argv
	if arg_process(in_cmd): # argv
		filename = in_cmd[1]
		print("This program helps you to remove the '{}'s (file/dir) in ALL sub directories.".format(filename))
	else: # input interaction
		filename = input("Please enter the file/dir you want to remove in ALL sub directories: ") # "WAVECAR", "WAV*", "tmp"
	## list the files 
	remove_list = sub.check_output(f"find -name {filename}", shell=True).decode("utf-8").split("\n")
	remove_list.pop(-1) if remove_list[-1] == '' else 0
	print(remove_list)
	[sub.run("ls -lhd {}".format(x), shell=True) for x in remove_list]
	## remove files with different choices
	print(f"Remove ALL '{filename}'s? (y/n/c) (enter c to choose specifically): ", end="")
	while True:
		choice = input()
		if choice == "y":
			rm_list = remove_list
			process_rmlist(rm_list); exit(0)
		elif choice == "c":
			print("Please list what you want to remove according to the above (seperate by space)")
			str_rmlist = input()
			rm_list = str_rmlist.split(" ")
			print(rm_list)
			process_rmlist(rm_list); exit(0)
		elif choice == "n":
			print("You choose to keep the files; exiting.."); exit(0)
		else:
			print("Please type 'y' or 'n' or 'c': ",  end="")