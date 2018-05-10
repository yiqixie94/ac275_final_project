#!/bin/bash
#SBATCH --job-name=monolayer_CrI3
#SBATCH -n 32	# Number of cores requested
#SBATCH -N 1	# number of nodes
#SBATCH -t 0-01:00	# Runtime in d-HH:MM
#SBATCH -p shared	# Partition to submit to
#SBATCH --mem-per-cpu=4000	# Memory per cpu in MB (see also--mem)
#SBATCH -o job_%j.out	# Standard out goes to this file
#SBATCH -e job_%j.err	# Standard err goes to this file
#SBATCH --mail-type=all	# notifications for job done & fail
##SBATCH --mail-user=<youremail@your.domain> # send-to address

source new-modules.sh
module load intel/15.0.0-fasrc01 
module load impi/5.1.2.150-fasrc01 

mpirun -np $SLURM_NTASKS ~/VASP/vasp.5.4.4.std > vasp.out

