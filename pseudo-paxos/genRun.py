import os
import random
import argparse


parser=argparse.ArgumentParser()
parser.add_argument('--interval', type=int, default=10)
parser.add_argument('--seed', type=int, default=42)
parser.add_argument('--process', type=int, default=5)

args=parser.parse_args()
paxosEvents='./paxosevents'

random.seed(args.seed)

for p in range(1, args.process+1):
    if os.path.exists(paxosEvents):
        os.remove(paxosEvents)
    currTime=0
    events=[]
    for id in range(1, p+1):
        timeStamp=random.randint(currTime+1, currTime+args.interval)
        events.append('%d p1 msg %d\n' %(timeStamp, id))
        currTime=timeStamp
    
    with open(paxosEvents, 'a') as f:
        for event in events:
            f.write(event)
            
    os.system('python pseudo-paxos.py')
    