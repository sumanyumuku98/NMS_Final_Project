#add folder directory above to python's path
from sys import path
path.append('..')

import random
random.seed()

##################
# Pre
##################
#random lat function
def lat(node, dst):
    num = int(random.gauss(10,5))
    return max([1, num])
#adds bidirectional connection between two nodes
def addbidcon(n1, n2, lat):
    n1.con[n2.name] = lat
    n2.con[n1.name] = lat
from base import Node
numAcceptors = 0
#generates topology based on the numbers or replicas, leades, and acceptors
def generateTop():
    global numAcceptors
    top = []
    topD = {}
    numReplicas = 3
    numLeaders = 1
    numAcceptors = 3
    #replicas
    for r in range(1,numReplicas+1):
        n = Node('r'+str(r))
        n.type = 'replica'
        n.state = []
        n.slot_in = 1
        n.slot_out = 1
        n.requests = []
        n.proposals = []
        n.decisions = []
        n.window = 5
        n.leaders = ['l1'] #only has one leader
        top += [n]
    #leader
    for l in range(1,numLeaders+1):
        n = Node('l'+str(l))
        n.type = 'leader'
        n.ballot_num = [0,n.name]
        n.proposals = []
        n.active = False
        n.commanders = {}
        n.scout = None
        top += [n]
    #acceptors
    for a in range(1,numAcceptors+1):
        n = Node('a'+str(a))
        n.type = 'acceptor'
        n.ballot_num = [-1, ''] #blank ballot
        n.accepted = []
        top += [n]
    for n in top:
        topD[n.name] = n
    for n1 in top:
        for n2 in top:
            if n1 == n2:
                continue
            addbidcon(n1,n2,lat)
            #addbidcon(n1,n2,5)
    return (top, topD)


#EVENTS
from base import Msg
def generateEventList(eventFile):
    eventList = {}    
    with open(eventFile) as file:
        for line in file:
            if 'request' in line:
                time, dst, type, c, text = line.strip().split(' ',4)
                ev = Msg(dst, type)
                ev.c = c
                ev.text = text
            else:
                time, dst, type = line.strip().split(' ',2)
                ev = Msg(dst, type)      
            time = int(time)
            if time not in eventList:
                eventList[time] = []
            eventList[time] += [ev]
    return eventList
    
    
##################
# Debug functions 
##################
#replacement debug function, ignores BLANKTIMESTEP event and simply prints anything else
def debugNOBLANK(eventName, data):
    if eventName == 'BLANKTIMESTEP':
        return
    if eventName == 'EVENTLIST':
        return
        for e in data:
            print(d.__dict__)
        print()
    if isinstance(data, Msg):
        return
        #prints Msg dicts rather than the object pointer location
        print(eventName + ' ' + str(data.__dict__))
    else:
        print(eventName + ' ' + str(data))
        
        
######################    
# Multipaxos
######################    
leaderSCId = 0
def generateId():
    global leaderSCId
    leaderSCId += 1
    return leaderSCId

class Commander():
    def __init__(self, leader, acceptors, replicas, proposal):
        self.id = generateId()
        self.leader = leader
        self.proposal = proposal
        b, s, c = proposal
        self.acceptors = acceptors
        self.waitfor = [a for a in acceptors]
        self.replicas = replicas
    
    
        
class Scout():
    def __init__(self, leader, acceptors, b):
        self.id = generateId()
        self.leader = leader
        self.waitfor = []
        self.acceptors = acceptors
        self.waitfor = [a for a in acceptors]
        self.b = b
        self.pvalues = []

#get all acceptors connected to node and return their names
def getAcceptors(node):
    global topD
    acceptors = []
    for n in node.con:
        if topD[n].type == 'acceptor':
            acceptors += [n]
    return acceptors
    
def getReplicas(node):
    global topD
    replicas = []
    for n in node.con:
        if topD[n].type == 'replica':
            replicas += [n]
    return replicas

def isLeader(node):
    return node.type == 'leader'
def isAcceptor(node):
    return node.type == 'acceptor'
def isReplica(node):
    return node.type == 'replica'
    
    
#ballot num is actually a (num, leader) tuple
def biggerBallot(compare, base):
    return compare[0] > base[0]
    
  
from base import Msg, conditionalBroadcast, addMsgEvent
def spawnScout(node, acceptors, ballot_num):
    node.scout = Scout(node, acceptors, ballot_num)
    msg = Msg(None, 'p1a')
    b, l = ballot_num
    msg.text = 'p1a(' + str(b) + ',' + l + ')'
    msg.source = node.scout.leader.name
    msg.b = node.scout.b
    msg.dstid = node.scout.id
    conditionalBroadcast(node, msg, isAcceptor)
    
def spawnCommander(node, acceptors, replicas, proposal):
    com = Commander(node, acceptors, replicas, proposal)
    msg = Msg(None, 'p2a')
    msg.source = node.name
    b, s, c = proposal
    msg.text = 'p2a(' + str(s) + ',' + str(c) + ')'
    msg.b = node.ballot_num
    msg.dstid = com.id
    msg.s = s
    msg.c = c 
    conditionalBroadcast(node, msg, isAcceptor)
    node.commanders[com.id] = com
    pass
    
def pmax(pvals):
    #uses list to compare s values
    sDic = {}
    for b, s, c in pvals:
        #conflicting s, compares ballot
        if s in sDic:
            b2 , _, _ = sDic[s]
            if(biggerBallot(b, b2)):
                sDic[s] = [b,s,c]
        else:
            sDic[s] = [b,s,c]
    #return as list
    list = []
    for k in sDic:
        b, s, c = sDic[k]
        list += [[s,c]]
    return list
    
def update(proposals, pmaxvals):
    props = [p for p in pmaxvals]
    occupied_slots = [s for s, c in props]
    for s, c in proposals:
        #adds proposal if slot isn't occupied
        #if the slot is occupied either the operation is different or the same operation is already in
        if s not in occupied_slots:
            props += [[s,c]]
    return props
    
    
def multipaxos(node, event, debugF):       
    #
    #Replica-------------------
    if(node.type == 'replica'):
        if event.type == 'request':
            debugF('Replica ' + node.name, 'receives request ' + event.c)
            node.requests += [event.c]
            
        elif event.type == 'decision':
            debugF('Replica ' + node.name, 'receives decision (' + str(event.s) + ',' + event.c + ') from ' + event.source)
            node.decisions += [[event.s, event.c]]
            for s, c in node.decisions:
                if s != node.slot_out:
                    continue
                for s2, c2 in node.proposals:
                    if s == s2:
                        node.proposals.remove((s2,c2))
                        if c != c2:
                            node.requests += [c2]
                #simplified perform
                debugF('Replica ' + node.name, 'performs ' + c)
                node.slot_out += 1
                
        #propose
        for c in node.requests:
            while node.slot_in < node.slot_out + node.window:
                #Not implemented: if leaders were reconfigured in slot_in-window slot reconfigure leaders
                #if there isn't a <slot_in, c> in decisions:
                if node.slot_in not in [s for s,c2 in node.decisions]:
                    debugF('Replica ' + node.name, 'proposes <' + str(node.slot_in) + ',' + c +'>')
                    node.requests.remove(c)
                    node.proposals += [(node.slot_in, c)]
                    msg = Msg(None, 'propose')
                    msg.text = 'p('+ str(node.slot_in) + ',' + c+')'
                    msg.s = node.slot_in
                    msg.c = c
                    leaders = node.leaders
                    conditionalBroadcast(node, msg, (lambda node : node.name in leaders))
                    node.slot_in += 1
                    break
                node.slot_in += 1

    #
    #Acceptor-------------------
    elif(node.type == 'acceptor'):
        if event.type == 'p1a':
            if biggerBallot(event.b, node.ballot_num):
                node.ballot_num = event.b
                debugF('Acceptor ' + node.name, 'receives p1a ' + str(event.b) + ' from ' + event.source)
            else:
                debugF('Acceptor ' + node.name, 'refuses p1a ' + str(event.b) + ' from ' + event.source)
            msg = Msg(event.source, 'p1b')
            b, l = node.ballot_num
            msg.text = 'p1b(' + str(b) + ',' + l + ')'
            msg.dstid = event.dstid
            msg.source = node.name
            msg.ballot_num = node.ballot_num
            msg.accepted = node.accepted
            addMsgEvent(msg, node, event.source)
        if event.type == 'p2a':
            if(event.b == node.ballot_num):        
                debugF('Acceptor ' + node.name, 'receives p2a ' + str(event.b) + 'from ' + event.source)
                node.accepted += [[event.b, event.s, event.c]]
            else:
                debugF('Acceptor ' + node.name, 'refuses p2a ' + str(event.b) + 'from ' + event.source)
            msg = Msg(event.source, 'p2b')
            b, l = node.ballot_num
            msg.text = 'p2b(' + str(b) + ',' + l + ')'
            msg.source = node.name
            msg.ballot_num = node.ballot_num
            msg.dstid = event.dstid
            addMsgEvent(msg, node, event.source)

    #
    #Leader-------------------
    elif(node.type == 'leader'):
        adopted = False
        preempted = False
            
        #commander
        if event.type == 'p2b':
            #ignore message for dead commanders
            if event.dstid not in node.commanders:
                return
            com = node.commanders[event.dstid]
            b, s, c = com.proposal
            if event.ballot_num == b:
                com.waitfor.remove(event.source)
                if(len(com.waitfor) < (len(com.acceptors)/2)):
                    msg = Msg(None, 'decision')
                    msg.source = com.leader.name
                    msg.s = s
                    msg.c = c
                    msg.text = 'D(' + str(s) + ',' + c + ')'
                    conditionalBroadcast(node, msg, isReplica)
            else:
                preempted = True
                #kill commander
                node.commanders.pop(com.id)
            
        #scout
        if event.type == 'p1b':
            if(node.scout == None):
                return
            if event.dstid == node.scout.id:     
                if event.ballot_num == node.scout.b:
                    node.scout.pvalues += event.accepted
                    node.scout.waitfor.remove(event.source)
                    if(len(node.scout.waitfor) < (len(node.scout.acceptors)/2)):
                        adopted = True
                        node.scout = None
                else:
                    preempted = True
                    node.scout = None
                
        #initializes leader
        if event.type == 'init':
            spawnScout(node, getAcceptors(node), node.ballot_num)
                  
        
        if event.type == 'propose':
            debugF('Leader ' + node.name, 'receives request ' + str(event.c))
            if event.s not in [s for s, c in node.proposals]:
                node.proposals += [[event.s, event.c]]
                if node.active:
                    spawnCommander(node, getAcceptors(node), getReplicas(node), (node.ballot_num, event.s, event.c))
        #leader rvcs from scout
        if adopted:
            node.proposals = update(node.proposals, pmax(event.accepted))
            for s, c in node.proposals:
                spawnCommander(node, getAcceptors(node), getReplicas(node), (node.ballot_num, s, c))
            node.active = True         
        if preempted:
            #ignore outdated messages
            if not biggerBallot(node.ballot_num, event.ballot_num):            
                node.active = False
                r, self = node.ballot_num
                node.ballot_num = [r+1, self]
                spawnScout(node, getAcceptors(node), node.ballot_num)
        
    
######################    
# Simulate
######################    
#from paxospre import generateTop, generateEventList
from base import simulate
efile = 'ev1'
eventList = generateEventList(efile)
top, topD = generateTop()
log = simulate(eventList, top, topD, multipaxos, debugNOBLANK)
#log = simulate(eventList, top, topD, multipaxos)

#from svg import generateSvg
#generateSvg('a.svg', log, '5x', '5x')
exit()
#format
ops = {}
c = ''
for l in log:
    t, m = l[:2]
    if not hasattr(m, 'c'):
        continue
    c = m.c
    #first instance
    if m.c not in ops:
        ops[m.c] = [t]
    else:
        ops[m.c] += [t]
o = ops.pop(c)

min = o[-1]-o[0]
max = o[-1]-o[0]
sum = o[-1]-o[0]
count = 1

#ops
for op in ops:
    lat = ops[op][-1]-ops[op][0]
    if lat < min:
        min = lat
    elif lat > max:
        max = lat
    sum += lat
    count += 1
print(efile + ' ' + str([min, max, sum/count]))
