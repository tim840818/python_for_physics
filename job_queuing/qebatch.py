#!/usr/bin/env python
## authors: Tim
"""
This program automatically submits jobs in order and checks for error messages routinely.
1. This program is written specifically for linux evnironments and the jobscript files with patterns similar to `./sample files/job.sh-*`. Please make sure your system supports the same job scripting.
2. Usage: just type 'qebatch.py' and wait for results; if you type 'qebatch.py -t', a small window will pop up once the job batch is done and show "SUCCESS" OR "FAIL".
"""
import subprocess as sub
import os, re, datetime, argparse
from time import sleep
from sys import path; path.insert(0, "../modules") # /home/twchang/bin
from multibatch import Job, Batch

class Job_info:
	def __init__(self, jobname: str, order: int, runtime: int, cores: int):
		self.jobname = jobname
		self.order = order
		self.runtime = runtime
		self.cores = cores

job_dict = {                       #jobname           #ord #time #core
	"job.sh-scf"        : Job_info("job.sh-scf"       , 10,  10,  16),
	"job.sh-scffit"     : Job_info("job.sh-scffit"    ,  9,  60,  16),
	"job.sh-nscf"       : Job_info("job.sh-nscf"      , 12,  16,  16),
	"job.sh-ph"         : Job_info("job.sh-ph"        , 14, 900,  16),
	"job.sh-elph"       : Job_info("job.sh-elph"      , 16, 900,  16),
	"job.sh-q2r"        : Job_info("job.sh-q2r"       , 18,   6,  16),
	"job.sh-matdyn"     : Job_info("job.sh-matdyn"    , 22,   8,  16),
	"job.sh-matdyn.dos" : Job_info("job.sh-matdyn.dos", 24,   8,  16),
	"job.sh-bands"      : Job_info("job.sh-bands"     , 32,  10,  16),
	"job.sh-dos"        : Job_info("job.sh-dos"       , 34,   4,   1),
	"job.sh-pdos"       : Job_info("job.sh-pdos"      , 36,   4,   1),
	"job.sh-lambda"     : Job_info("job.sh-lambda"    , 50,   4,   1),
	"job.sh-plot"       : Job_info("job.sh-plot"      , 60,   2,   1),
}

def get_joblist():
	"""Gets jobs from the working directory and sorts them according to Job.order in job_dict."""
	dirlist = os.listdir(".")
	joblist = [job for job in dirlist if "job.sh-" in job]
	joblist.sort(key=lambda s: job_dict[s].order) # sort joblist
	if len(joblist) == 0:
		print("No 'qe'-jobs in this directory; exiting..."); exit(1)
	return joblist
def _empty():
	pass

if __name__ == "__main__":
	## argparse param
	agps = argparse.ArgumentParser(description='tk.py launcher')
	agps.add_argument('-t', '--tk', action='store_true', help='type -t for tk.py')
	args = agps.parse_args(); choice = args.tk
	## get joblist
	joblist = get_joblist()
	batchlist = [Job(jobname, job_dict[jobname].cores, job_dict[jobname].runtime, {}, _empty, _empty, []) for jobname in joblist]
	## initialize err file; get starting time
	time_start = datetime.datetime.now(); print(f"Batch started at {time_start}")
	fout = open("err", 'w'); fout.close()
	## run batch; get the batch_flag from the B.run() func.
	B = Batch(batchlist)
	batch_flag = "FAILED" if not B.run() else "SUCCESS"
	## run tk.py or not
	time_end = datetime.datetime.now(); print(f"Batch ended at {time_end}")
	time_processing = time_end - time_start; print(f"This batch-process lasted for '{time_processing}'")
	if choice:
		sub.run(f"tk.py {batch_flag}", shell=True)
