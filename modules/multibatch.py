#!/usr/bin/env python
## authors: Tim, Jake
"""This package contains all the functions about job submissions. It allows users to have preprosesses/postprocesses before/after the jobs.
Usage: 

from multibatch import Job, Batch

1. Prepare the following for each job:
	Name of the file to submit
	Number of cores needed
	Relevant data
	Functions (preprocess/postprocess) to handle the revelant data. Note that these functions should be written by YOURSELF.
	A list of files that will be used in this job.

Please note that, when referring to a file that you want to modify, please ALWAYS use the data["files"] mapping.
This maps the name of the original file to the new file name (i.e. in a new directory, etc.)
Since the name of the file may change, the safest way to refer to the file is by the mapping.
For example, if you want to modify 'ecutwfc' in '*.scf.in':

def preprocess(data):
	scfin_filename = data["files"]["*.scf.in"]
	scfin_file = open(scfin_filename, "r")
	# modify scfin_file...

2. Place all jobs into a list.
	- If it is a single job, simply put it in.
	- If it is a series of jobs that must be executed in order, put them in a list.
	*** Then, convert the jobs into a batch.
	You should end up with a list of jobs: 
		batch_list = [Batch(single_job1), Batch(single_job2), Batch([batchjob1, batchjob2]), Batch(single_job3), ...]
	Done!

Example:
def job1_pre(data):
	re.sub(data["ecutwfc"]....)
def job1_post(data):
	print(something)
j1 = Job("job 1", 20, {"ecutwfc": 32.0, "file": "*.scf.in"}, job1_pre, job1_post)

j2 = ...
j3 = ...
B = Batch([j1, j2, j3]) # single node
B.run()
"""
from threading import Lock, Thread
from os import system
import subprocess as sub
from time import sleep
import re, os

class Job:
	def __init__(self, jobname: str, cores: int, runtime: int, data, preprocess, postprocess, files: list):
		self.jobname = jobname ## the job.sh file
		self.cores = 16  ## number of cores needed
		self.jobid = ""
		self.runtime = runtime
		self.data = data
		self.preprocess = preprocess
		self.postprocess = postprocess
		self.files = {f : f for f in files}
		self.data["files"] = files ## list of files that will be used by this job

	def preprocess(self):
		self.preprocess(self.data)

	def postprocess(self):
		self.postprocess(self.data)

	def kill(self):
		print(f"Job {self.jobname} stopped. Exiting..."); return False

	def _grep_job_core(self):
		"""Gets the job nodes and cores used of each nodes from a jobscript file."""
		job = self.jobname; # core = self.cores
		# core = re.search(r"#PBS\s+-l\s+nodes=(.*)", fin).group(1)
		core = sub.check_output("grep PBS\\ -l {}".format(job), shell=True).decode("utf-8")  #like: #PBS -l nodes=node03:ppn=4
		match_list = re.findall(r"node(\d+).*?:ppn=(\d+)", core)
		core_index_list = [match[0] for match in match_list]    # "03"
		core_count_list = [int(match[1]) for match in match_list]  # 4
		self.cores = sum(core_count_list)
		return core_index_list, core_count_list

	def _get_nodesdict(self):
		"""Gets the general nodes usage information from the system by the command 'pbsnodes -a'. Organized them in nodesdict by several parameters: total (total cores in a node), remain (remaining cores in a node), users (user names and their jobids in a node)"""
		nodes_info_str = sub.check_output("pbsnodes -a", shell=True).decode("utf-8")
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
			nodesdict[name] = {"total": total, "remain": remain, "users": users}
		return nodesdict

	def _check_run(self):
		"""Checks if a job can be submitted. Reads nodesdict to get informations of the chosen nodes and examines that the cores in the jobscript should be less than the remain cores in the node. If not, return false for further process."""
		core_index_list, core_count_list = self._grep_job_core()
		nodesdict = self._get_nodesdict()
		for i in range(len(core_index_list)):
			core_index, core_count = core_index_list[i], core_count_list[i]
			core_remain = nodesdict[f"node{core_index}"]["remain"]
			if core_count > core_remain:
				print(f"Illegal!! Assigned job cores greater than remaining cores. Modyfing ppn of {self.jobname} ..")
				return False
		return True

	def select_node(self, ppn, core_container_list):
		"""Automatically selescts nodes and cores for the users. Gets ppn (self.cores) and arranges them into each node in core_container_list. Returns false when the ppn exceeds the total remaining cores of the system.
		ppn: self.cores
		core_container_list: The list of [node_name, node_remaining_cores] sorted by remaining cores.
		"""
		core_current_list = core_container_list; ppn_left = ppn
		select_node_list = []
		while ppn_left > 0:
			# print("len", len(core_current_list))
			for i in range(len(core_current_list)):
				volume = core_current_list[i][1]
				if ppn_left <= volume:
					select_node_list.append([core_current_list[i][0], ppn_left])
					volume -= ppn_left; ppn_left = 0
					break
				elif i == len(core_current_list)-1:
					select_node_list.append(core_current_list[i])
					ppn_left -= volume; core_current_list.pop(-1)
				# else:
				# 	continue
			# print("ppn_left", ppn_left); print(core_current_list)
			if core_current_list == []:
				# print("ppn > total remaining cores in the server; exiting...")
				return False
		return select_node_list

	def modify_cores(self):  # this should modify self.jobname's PBS -l line
		"""Gets select_node_list from the function 'select_node' and modifies the jobscript (self.jobname) with the list. Returns false when it receives the false condition from select_node(ppn, core_container_list)"""
		ppn = self.cores; nodesdict = self._get_nodesdict()
		core_container_list = [[name, nodesdict[name]["remain"]] for name in nodesdict if nodesdict[name]["remain"] != 0]
		core_container_list.sort(key=lambda s: s[1]); # pprint(core_container_list)
		select_node_list = self.select_node(ppn, core_container_list); # pprint(select_node_list)
		if not select_node_list: return False
		node_str = "+".join(["{}:ppn={}".format(select_node_list[i][0], select_node_list[i][1]) for i in range(len(select_node_list))])
		filename = self.jobname; fin = open(filename, "r"); file = fin.read(); fin.close()
		file = re.sub(r"(#PBS\s+-l\s+nodes=).*", r"\1{}".format(node_str), file)
		tempname = "oooo"; fout = open(tempname, 'w'); fout.write(file); fout.close()
		os.rename(tempname, filename)
		print(f"Successfully modify ppn of {self.jobname}")
		return True

	def _check_and_modify(self):
		"""Executes _check_run() to see if the job is ready to run. If not, modifies the jobscript (self.jobname) with modify_cores(). If unsuccuessful (ppn exceeds the total remaining cores in system), sleeps for one minute and tries again (for at most ten times), killing the job after that. """
		if self._check_run(): return True
		else:
			count = 0;
			while count < 10:
				if self.modify_cores():
					return True
				else:
					sleep(60); count += 1
			print("ppn > total remaining cores in the server; exiting..."); return self.kill()

	def submit(self):
		"""Submits a job and gets its jobid."""
		job_echo = sub.check_output("qsub {}".format(self.jobname), shell=True).decode("utf-8")
		job_echo = re.sub(r"\n", r"", job_echo)
		# print(job_echo, end = "; "); print("job '{}' running".format(self.jobname))
		self.jobid = re.search(r"(\d+)", job_echo).group(1)
		print(f"{job_echo}; job '{self.jobname}' is running.")

	def wait(self):
		"""When job is running, checks for every self.runtime and kills the job if err occurs. If nothing bad happens, keeps waiting until the job is finished (self.is_done() == True) and returns true."""
		print("->", end = " "); sleep(6)
		while True:
			if self.is_done(): 
				if not self.is_err(): return self.kill()
				else: 
					print("{} success".format(self.jobname)); return True
			if not self.is_err(): return self.kill()
			sleep(self.runtime)

	def is_done(self):
		"""Checks if self.jobid is still in the nodesdict. If yes, meaning that the job is still running, returns false. Else, returns true."""
		core_index_list, core_count_list = self._grep_job_core()
		nodesdict = self._get_nodesdict()
		done_flag = True
		for i in range(len(core_index_list)):
			core_index = core_index_list[i]
			# s = sub.check_output("qinfo | grep node{}".format(core_index), shell=True).decode("utf-8")
			if self.jobid in nodesdict[f"node{core_index}"]["users"]:
				done_flag = False; break
		if not done_flag:
			print(".", end = "", flush=True); return False
		else:
			print(" {} submitted by twchang is done.".format(self.jobname)); return True

	def is_err(self):
		"""Checks if there are any err messages in the err file and returns false when err happens; returns true if no err messages."""
		if "err" not in os.listdir():
			print("No 'err' file.\nBATCH STOPPED")
			return False
		else:
			errfile = open("err", "r").read()
			if errfile != "":
				print("Process {} failed.\nBATCH STOPPED".format(self.jobname))
				print("errfile:\n{}".format(errfile))
				return False
			else:
				return True

	def run(self):
		"""Runs all the processes for the job. Returns false when things get wrong in any process. Returns True when all processes finish successfully.
		Please refer to the functions stated above.
		"""
		self.preprocess()
		if not self._check_and_modify(): return False
		self.submit()
		if not self.wait(): return False
		self.postprocess()
		return True

class Batch: # is literally just a list of jobs
	def __init__(self, jobs: list):
		self.jobs = jobs if type(jobs) == list else [jobs]

	def run(self):
		"""Runs all the jobs. Returns false when a job fails."""
		for job in self.jobs:
			if not job.run(): return False
		return True
