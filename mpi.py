from mpi4py import MPI
import time
import pandas as pd
from run import generateSample, generateReport 
from util.analysis import Analysis

comm = MPI.COMM_WORLD 
rank = comm.Get_rank()

size = comm.Get_size()

print(size)

# population = []

# comm.scatter(0, root=0)
# pop = generateSample()
# population.append(comm.gather(pop, root=0))

# if rank == 0:
#     df = pd.DataFrame(population)
#     date = time.strftime("%d-%m-%Y-%H-%M-%S")
#     df.to_csv(f'results/data/{date}.csv', index=False)
#     analysis = Analysis(population)
#     filename = f"results/reports/{date}.docx"
#     generateReport(analysis, filename)
    



