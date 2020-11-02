#!/usr/bin/env python
## authors: Tim
"""
This program determines the CPU 'cores' and 'nodes' of job submission file 'job.sh-*'. It searches the job files and sorts them in the specific order. After that, it asks the user to enter 'nodes', 'cores', and 'batch name' for this series of jobs.
1. This program is written specifically for linux evnironments and the jobscript files with patterns similar to `./sample files/job.sh`. Please make sure your system supports the same job scripting.
2. Usage: Enter the parameters of jobs by the instructions.
"""
### authors : Jake, Tim
import os, re
import subprocess as sub
from pprint import pprint

class Job:
	## the pattern of each job script
	job_head = '''#!/bin/sh
#PBS -N qe
#PBS -e err
#PBS -o out
### Queue name (default)
#PBS -q batch 
### Number of nodes (ppn: process per node)
#PBS -l nodes=node07:ppn=16

echo "Starting on `hostname` at `date`"
if [ -n "$PBS_NODEFILE" ]; then
   if [ -f $PBS_NODEFILE ]; then
      # print the nodenames.
      echo "Nodes used for this job:"
      cat ${PBS_NODEFILE}
      NPROCS=`wc -l < $PBS_NODEFILE`
   fi
fi
# Display this job's working directory
echo Working directory is $PBS_O_WORKDIR
cd $PBS_O_WORKDIR
# Use mpirun to run MPI program.
/opt/openmpi-1.4.4/bin/mpirun -machinefile $PBS_NODEFILE'''

	def __init__(self, jobname: str, order: int, runtime: int):
		self.jobname = jobname
		self.order = order
		self.runtime = runtime
job_dict = {
	"job.sh-scf"        : Job("job.sh-scf"       , 10, 10),
	"job.sh-scffit"     : Job("job.sh-scffit"    ,  9, 60),
	"job.sh-nscf"       : Job("job.sh-nscf"      , 12, 20),
	"job.sh-ph"         : Job("job.sh-ph"        , 14, 900),
	"job.sh-elph"       : Job("job.sh-elph"      , 16, 900),
	"job.sh-q2r"        : Job("job.sh-q2r"       , 18, 4),
	"job.sh-matdyn"     : Job("job.sh-matdyn"    , 22, 4),
	"job.sh-matdyn.dos" : Job("job.sh-matdyn.dos", 24, 4),
	"job.sh-bands"      : Job("job.sh-bands"     , 32, 10),
	"job.sh-dos"        : Job("job.sh-dos"       , 34, 4),
	"job.sh-pdos"       : Job("job.sh-pdos"      , 36, 4),
	"job.sh-lambda"     : Job("job.sh-lambda"    , 50, 4),
	"job.sh-plot"       : Job("job.sh-plot"      , 60, 2),
	"job.sh"            : Job("job.sh"           , 99, 10)
}

def preprocess(nodes_info_str):
	"""Creates the nodesdict from nodes_info_str.
	nodes_info_str: the outcome string of 'pbsnodes -a'.
	"""
	nodeslist = re.findall(r"node\d+.*\n(?:     \w+\s*=\s*.*\n)*", nodes_info_str)
	nodesdict = {}
	for node in nodeslist:
		name = re.match(r"(node\d+).*", node).group(1)
		total = int(re.search(r"np = (\d+)", node).group(1))
		search = re.search(r"     jobs = (.*)", node)
		if not search: remain = total; users = set()
		else: 
			remain = total - (search.group(1).count(",") + 1)
			users = set(re.findall(r"\d+/(\d+).*?[,$]", search.group(0)))
		if re.search(r"state\s*=\s*down", node): remain = "--"
		nodesdict[name] = {"total": total, "remain": remain, "users": users}
	return nodesdict

def print_nodes(nodesdict):
	"""Finds and prints the remaining cores of each node from nodesdict."""
	print("remaining number of cores:")
	for node in nodesdict:
		remain = nodesdict[node]["remain"]; total = nodesdict[node]["total"]
		if remain == "--":
			remain_str = "\033[31m{}\033[0m".format(remain)
		elif remain == 0:
			remain_str = "\033[91m{:2d}\033[0m".format(remain)
		elif remain == total:
			remain_str = "\033[32m{:2d}\033[0m".format(remain)
		else:
			remain_str = "{:2d}".format(remain)
		print("{}: {}".format(node, remain_str))

def print_twchang(nodesdict):
	"""This is just to check which nodes 'twchang's are in."""
	qstat_str = sub.check_output("qstat", shell=True).decode("utf-8")
	match_list = re.findall(r"(\d+).*?\s+.*?\s+(.*?)\s+.*", qstat_str) # [(jobname, username)]
	twchangset = set([a[0] for a in match_list if a[1] == "twchang"])
	inlist = [node for node in nodesdict if twchangset & nodesdict[node]["users"]]
	print("Warning, twchang already in {}".format(", ".join(inlist))) if inlist else 0

def get_job_list():
	"""Gets jobs from the working directory and sorts them according to Job.order in job_dict."""
	dirlist = os.listdir(".")
	joblist = [x for x in dirlist if "job.sh" in x and x in job_dict]
	tmplist = [x for x in dirlist if "job.sh" in x and x not in job_dict]
	def compare_function(s: str):
		return job_dict[s].order
	joblist.sort(key=compare_function)
	joblist.extend(tmplist)
	return joblist

def get_int(nodesdict):
	"""Asks the users to input the desired nodes for jobs and returns the nodes as node_choice. Shows error message and asks for new inputs if the program receives wrong inputs."""
	limit = len(nodesdict); 
	while True:
		node_choice = input().strip().split(" ")
		valid = True
		for node in node_choice:  
			try:
				node_int = int(node)
			except ValueError:
				print("Please enter a series of number(s)!", end= " ")
				valid = False; break
			if not 1 <= node_int <= limit:
				print(f"Please enter number(s) between 01 and {limit}:", end=" ")
				valid = False; break
			elif nodesdict["node{:02d}".format(node_int)]["remain"] == "--":
				print("'node{:02d}' is unavailable, please choose others:".format(node_int), end=" ")
				valid = False; break
			elif nodesdict["node{:02d}".format(node_int)]["remain"] == 0:
				print("'node{:02d}' is full, please choose others:".format(node_int), end=" ")
				valid = False; break
		if valid: node_choice = [int(node) for node in node_choice]; return node_choice

def get_ppn(nodesdict, node_choice):
	"""Asks the users to input the desired CPU cores for each job and assigns these cores due to node_choice; afterwards, returns the assigned cores as ppn_list. Shows error message and asks for new inputs if the program receives wrong inputs."""
	while True:
		try:
			ppn = int(input())
		except ValueError:
			print("Please enter a number!", end= " ")
			continue
		## allocate ppn into chosen nodes
		ppn_list = []
		ppn_left = ppn
		valid = True
		for i in range(len(node_choice)):
			ppn_available = nodesdict["node{:02d}".format(node_choice[i])]["remain"]
			if i == len(node_choice)-1:
				if ppn_left <= 0:
					break
				if not ppn_left <= ppn_available:
					print("Assigned cores > remaining cores, gelingbo :)")
					valid = False; break
				ppn_list.append(ppn_left)
			else:
				if ppn_left <= ppn_available:
					ppn_list.append(ppn_left); break
				else:
					ppn_list.append(ppn_available)
					ppn_left -= ppn_available
		if valid: return ppn_list

def get_qe_atoms(pwd, qe_switch: bool):
	"""This function reads qe_switch and finds suitable atom_name, returning it as 'atoms'."""
	if not qe_switch:
		return False
	atoms_list = []
	for job in joblist:
		fin = open(job, "r"); file = fin.read(); fin.close()
		atoms = re.search(r"-np\s+\$NPROCS\s+.*\s+<(.*?)\..*>\s+(.*?)\..*", file).group(1)
		atoms_list.append(atoms) if atoms not in atoms_list else 0
	if len(atoms_list) == 1 and atoms_list[0] in pwd:
		return False
	else:
		print(f"Atom_name in jobs is not coincident with it in workdir; current workdir: {pwd}, 'atoms' in jobs: {atoms_list}")
		atoms = input("Please enter the 'atoms' of your batch: ")
	return atoms

def get_batch_name(joblist):
	"""Finds the batch_name and returns it from the first job-script of the joblist. Allows users to keep the old batch_name or define a new one."""
	fin = open(joblist[0], 'r'); file = fin.read(); fin.close()
	batch_name = re.search(r"#PBS\s+-N\s+(.*)", file).group(1)
	print("\033[34m------------------------------------\033[0m\nCurrent \033[35mbatch_name\033[0m: {}".format(batch_name))
	print("Please enter the \033[35mbatch_name\033[0m of the job:", end=" ")
	batch_name_input = input()
	batch_name = batch_name_input if batch_name_input != "" else batch_name
	return batch_name

def modify_job(filename, batch_name, node_choice, ppn_list, qe_switch, atoms):
	"""Modifies each job for all the parameters entered by the user.
	Parameters
	--------------
	filename: str, the name of the job-script; e.g., job.sh, job.sh-scf etc.
	batch_name: str, the batch name of the joblist; all the jobs in it will have the same batch_name.
	node_choice: list of integers, the No. of nodes that the users choose to run for the jobs.
	ppn_list: list of integers, the CPU cores that are assigned for each node in node_choice.
	qe_switch: bool, a switch that decide the program to modify the jobs in qe_mode or vasp_mode.
	atoms: str, along with qe_switch (True); the program modifies the jobs regarding qe with this parameter.
	"""
	fin = open(filename, "r"); file = fin.read(); fin.close()
	# fin_head = open("/home/twchang/bin/others/job.sh-mod", 'r').read()
	fin_head = Job.job_head
	node_str = "+".join(["node{:02d}:ppn={}".format(node_choice[i], ppn_list[i]) for i in range(len(ppn_list))])
	tail = re.search(r".*(\s*-np.*)", file, re.S).group(1).strip()
	tail = re.sub(r"\s*>>\s*out", r"", tail)
	if qe_switch:
		tail = re.sub(r"(NPROCS\s*).*(/bin/)", r"\g<1>/data2/twchang/opt/q-e-qe-6.4.1\g<2>", tail, re.S)
	else: # vasp mode
		tail = re.sub(r"(NPROCS\s*).*(/bin/).*(\n)", r"\g<1>/home/twchang\g<2>vasp_noncol \g<3>", tail, re.S)
	file = fin_head + " " + tail
	file = re.sub(r"(#PBS\s+-N\s+).*", r"\g<1>{}".format(batch_name), file) # if batch_name != "" else file # modify batch_name
	file = re.sub(r"(#PBS\s+-l\s+nodes=).*", r"\g<1>{}".format(node_str), file) # modify ppn
	file = re.sub(r"(-np\s+\$NPROCS\s+.*\s+<).*?(\..*>\s+).*?(\..*)", r"\g<1>{}\g<2>{}\g<3>".format(atoms, atoms), file) if atoms else file
	file = re.sub(r"/data2/twchang/q-e-qe-6\.1\.0/bin", r"/data2/twchang/opt/q-e-qe-6.4.1/bin", file)# if qe_switch else file
	fout = open(filename, "w"); fout.write(file)

### main function
if __name__ == "__main__":
## get job_node information
	nodes_info_str = sub.check_output("pbsnodes -a", shell=True).decode("utf-8")
	nodesdict = preprocess(nodes_info_str)
	print_nodes(nodesdict)
	print_twchang(nodesdict)
## get joblist (all jobs in the batch)
	joblist = get_job_list()
	print(joblist)
	if len(joblist) == 0: print("There are \033[31mno\033[0m job files in this directory!"); exit(0)
## get node_#, and job_ppn for each job and check if applicable
	print("Please enter the \033[35mlist of # of node(s)\033[0m you want to run on:", end=" ")
	node_choice = get_int(nodesdict)
	ppndict = {}
	for job in joblist: #all job.sh
		print("Please specify \033[35mppn\033[0m for {}: ".format(job), end="")
		ppn_list = get_ppn(nodesdict, node_choice)
		ppndict[job] = ppn_list
	# pprint(ppndict)
## jobop specify for qe_switch
	pwd = os.getcwd()
	if "/qe" in pwd:
		print("You are working under a 'qe/' directory; turn on 'qe_switch' ([y]/n)? ", end='')
		while True:
			qe_choice = input()
			if qe_choice == "y" or qe_choice == "": qe_switch = True; break
			elif qe_choice == "n": qe_switch = False; break
			else: print("Please type 'y' or 'n': ", end='')
	else:
		print("You are NOT working under a 'qe/' directory; still turn on 'qe_switch' (y/n)? ", end='')
		while True:
			qe_choice = input()
			if qe_choice == "y": qe_switch = True; break
			elif qe_choice == "n": qe_switch = False; break
			else: print("Please type 'y' or 'n': ", end='')
	atoms = get_qe_atoms(pwd, qe_switch)
## finally, get batch name
	batch_name = get_batch_name(joblist)
## final operations for all jobs
	for job in joblist: #all job.sh
		ppn_list = ppndict[job]
		modify_job(job, batch_name, node_choice, ppn_list, qe_switch, atoms)
	print("Done.")
