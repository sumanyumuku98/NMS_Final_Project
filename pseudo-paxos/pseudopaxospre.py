#add folder directory above to python's path
from sys import path
path.append('..')

#---------------------------
#bidirectional connection with same latency
def addbidcon(n1, n2, lat):
    n1.con[n2.name] = lat
    n2.con[n1.name] = lat

#import nodes and generate topoolgy
from base import Node
def generateTop():
    top = []
    topD = {}
    with open('paxostop') as file:
        line = file.readline()
        
        #find initializa quorum 
        while 'quorum' not in line:
            line = file.readline()
        quorum = file.readline().strip().split(',')
        
        #initializes all learners 
        file.readline()
        line = file.readline()
        while 'proposer' not in line:
            n = Node(line.strip())
            n.type = 'learner'
            topD[n.name] = n
            line = file.readline()
            
        #initializes all proposers 
        line = file.readline()
        while 'acceptor' not in line:
            n = Node(line.strip())
            n.type = 'proposer'
            n.quorum = quorum
            n.phase = 0
            n.waiting = {}
            topD[n.name] = n
            line = file.readline()
            
        #initializes all acceptor 
        line = file.readline()
        while 'connection' not in line:
            n = Node(line.strip())
            n.type = 'acceptor'
            topD[n.name] = n
            line = file.readline()
            
        #initializes connections
        line = file.readline()
        while 'end' not in line:
            n1, n2, lat = line.strip().split(' ')
            n1 = topD[n1]
            n2 = topD[n2]
            lat = int(lat)
            addbidcon(n1,n2,lat)  
            line = file.readline()  
    for n in topD:
        top += [topD[n]]
    return (top, topD)
    
    
#---------------------------
from base import Msg
def generateEventList():
    eventList = {}
    with open('paxosevents') as file:
        for line in file:
            time, dst, event, text = line.strip().split(' ')
            time = int(time)
            event = Msg(dst, event)
            event.text = text
            if time not in eventList:
                eventList[time] = []
            eventList[time] += [event]
    return eventList
    

#---------------------------
#test function
if __name__ == '__main__':                
    top, topD = generateTop()
    print('###TOPOLOGY###')
    for n in topD:
        print(n + ' : ' + str(topD[n].__dict__))
    
    eventList = generateEventList()
    print('###Events###')
    for time in eventList:
        for event in eventList[time]:
            print(str(time) + ' : ' + str(event.__dict__))