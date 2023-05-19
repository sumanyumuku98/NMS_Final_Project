import os
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()
import numpy as np
from scipy.signal import savgol_filter

processes=[]
consensus_time=[]
cons_list=None

if not os.path.exists('../assets'):
    os.makedirs('../assets')

# Generate Consensus Time
with open('./consensus.txt', 'r') as f:
    cons_list=f.readlines()
    for item in cons_list:
        p, time = item.split(',')
        processes.append(int(p))
        consensus_time.append(float(time.strip()))
  
plt.figure(figsize=(10, 8))
plt.title('Consensus Time for Paxos Algorithm')
plt.plot(processes, savgol_filter(consensus_time,51, 3))
plt.xlabel('Load ->')
plt.ylabel('Consensus Time ->')
plt.savefig('../assets/consensus.png')


# Generate Communication Overhead
cons_list=None
processes=[]
overhead=[]
with open('./overhead.txt', 'r') as f:
    cons_list=f.readlines()
    for item in cons_list:
        p, oh = item.split(',')
        processes.append(int(p))
        overhead.append(float(oh.strip()))
  
plt.figure(figsize=(10, 8))
plt.title('Communication Overhead for Paxos Algorithm')
plt.plot(processes, savgol_filter(overhead,51, 3), 'r')
plt.xlabel('Load ->')
plt.ylabel('Communication Overhead (Messages Passed) ->')
plt.savefig('../assets/overhead.png')