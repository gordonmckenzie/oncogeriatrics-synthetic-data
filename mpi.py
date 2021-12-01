from mpi4py import MPI
import time, os
import pandas as pd
import numpy as np
from run import generateSample, generateReport 
from util.analysis import Analysis

comm = MPI.COMM_WORLD 
size = comm.Get_size()
rank = comm.Get_rank()

population = []

if rank != 0:
    pop = generateSample(env="HPC") 
    comm.send(pop, dest=0, tag=11)
else:
    for s in range(1,size):
        data = comm.recv(source=s, tag=11)
        population.append(data)
    arr = [item for sublist in population for item in sublist]
    df = pd.DataFrame(arr)
    date = time.strftime("%d-%m-%Y-%H-%M-%S")
    df.to_csv(f'results/data/{date}.csv', index=False)
    #os.rename('results/data/prescribing.csv', f'results/data/prescribing-{date}.csv')
    analysis = Analysis(arr)
    filename = f"results/reports/{date}.docx"
    generateReport(analysis, filename)
        



