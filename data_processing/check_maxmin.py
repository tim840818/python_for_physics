#!/usr/bin/env python
"""
This program finds the maximum and minimum of y data in a file. It prints warning if there are multiple y data or the minimum of the y data < 0.
It will print only the maximum and the minimum of the data if everything goes right.
"""
import sys, re

in_cmd = sys.argv
if len(in_cmd) != 2:
	print("usage: python check_maxmin.py filename")
	exit(0)

f = in_cmd[1]  # file name
fin = open(f, "r")
num = []
count = 0

for data in fin:
	if not re.search(r"[^eE\s\d\.\-+]", data):
		datalist = data.split()
		count = count+1 if len(datalist) > 2 else count
		num.append(float(datalist[1])) if len(datalist) > 1 else 0
print("Warning, multiple y data, please check your file to confirm the max & min.") if count > 0 else 0

num_large, num_little = max(num), min(num)
print("Maximum : {}".format(num_large))
print("Minimum : {}".format(num_little))

if (num_little < 0 and "band" not in f):
	print("Warning, negative value in {}!".format(f))

