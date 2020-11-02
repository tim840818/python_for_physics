#!/bin/sh
#PBS -N H3S 
#PBS -e err
#PBS -o out
### Queue name (default)
#PBS -q batch 
### Number of nodes (ppn: process per node)
#PBS -l nodes=node08:ppn=16+node04:ppn=8

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
/opt/openmpi-1.4.4/bin/mpirun -machinefile $PBS_NODEFILE -np $NPROCS /home/twchang/bin/vasp_noncol 
# print end time
echo "Job Ended at `date`"

