#  Job Queuing
The programs in this folder are mainly for job manipulating and job submitting.

## `jobop.py`
Determines the CPU 'cores' and 'nodes' of job-scripts like `job.sh`, `job.sh-*`. Searches the job files and sorts them in the specific order. After that, asks the users to enter 'nodes', 'cores', and 'batch name' for this series of jobs.

### Usage
1. This program is written specifically for linux evnironments and the jobscript files with patterns similar to `./sample files/job.sh`. Please make sure your system supports the same job scripting.

2. Usage: Follow the instructions and enter the parameters of your jobscripts.

3. Example: please check `./sample files/` to view the sample jobscripts. The code below shows the interface of this program.
```
[twchang@breadserver NM]$ jobop.py
remaining number of cores:
node01:  8
node02:  8
node03:  8
node04:  8
node05: 16
node06: 16
node07: 16
node08: 16
node09: 16
node10: 16
node11: 16
node12:  0
['job.sh']
Please enter the list of # of node(s) you want to run on: 1
Please specify ppn for job.sh: 8
You are NOT working under a 'qe/' directory; still turn on 'qe_switch' (y/n)? n
------------------------------------
Current batch_name: H3S
Please enter the batch_name of the job: test_for_vasp_jobscript
Done.

```


## `qebatch.py`
Automatically submits jobs in order and checks for error messages routinely.

### Usage
1. This program is written specifically for linux evnironments and the jobscript files with patterns similar to `./sample files/job.sh-*`. Please make sure your system supports the same job scripting.

2. Make sure you prepare the right input files and jobscripts in your working directory. Type `qebatch.py` and wait for results.

3. Command line options: 
	* `-t`: A small window will pop up once the job-batch is done and show "SUCCESS" or "FAIL".
