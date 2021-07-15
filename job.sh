#!/bin/bash
#SBATCH -J OncoGeriSim
#SBATCH -N 1
#SBATCH --ntasks-per-node 12
#SBATCH -D /home/544688/
#SBATCH -o debug.out
#SBATCH -e debug.err
#SBATCH -p compute
#SBATCH -t 00:10:00
#SBATCH --mail-user= gordon.mckenzie@hyms.ac.uk

echo $SLURM_JOB_NODELIST

module purge
module load python/anaconda/4.6/miniconda/3.7

source activate /home/544688/.conda/envs/ogsim
export PATH=/home/544688/.conda/envs/ogsim/bin:${PATH}

python /home/544688/run.py

