#################
# BASE EVENT
#################
# Simulation is based on discrete events 
#the "list" of events is a dictionary which stores an array of events(messages) tied to a numeric key which is the time when the message(s) arrive at a node(s)
#e.g. eventlist[time] -> [event1, event2], with time being an int
#a Msg object has at least three attributes, the destination node, the type of the message, and an unique identifier which unifies the send-receive pair 
#the identifier can be set to anything, but each node can only receive an identifier once, and each identifier can only be sent by a node once
#other types of events can be created but they must be objects with a type and destination node fields
class Msg:
    def __init__(self, dstNode, type, identifier=None):
        #destination node identifier
        self.dstNode = dstNode
        #event type
        self.type = type
        #event identifier, generates one if not provided
        if identifier is not None:
            self._id = identifier
        else:
            self._id = generateID()

#uses a counter to return unique ids 
idCounter = 0
def generateID():
    global idCounter
    idCounter += 1
    return 'E'+str(idCounter)
    
#duplicates a Msg event with a new ID
def duplicateMSG(orig):
    clone = Msg(None, None)
    #copies fields in the internal dict from one object to the other, vars outside the dict are ignored
    for field in orig.__dict__:
        #don't copy ID
        if field == '_id':
            continue
        clone.__dict__[field] = orig.__dict__[field]
    return clone

            
#add event to the received eventlist at time t
def addLocalEvent(eventList, event, t):
    #creates timeslot if it doesn't already exists
    if t not in eventList:
        eventList[t] = []
    #adds event to timeslot t
    eventList[t] += [event]
            
#add event to the global eventlist at time t
def addEventAt(event, t):
    #creates timeslot if it doesn't already exists
    if t not in eventList:
        eventList[t] = []
    #adds event to timeslot t
    eventList[t] += [event]
            
#add event to the global eventlist with a delay of t from the current simulation time
def addDelayedEvent(event, t):
    time = curSimTime+t
    addEventAt(event, time)
            
#add event to the global eventlist at time t+latency(src to dst) and logs the event creation
def addMsgEvent(event, src, dst):
    global log
    #if dst isn't a string (e.g. is a node) gets its name instead 
    if not isinstance(dst, str):
        dst = dst.name
    if event.dstNode == None:
        event.dstNode = dst
    #gets latency
    lat = src.getLatencyTo(dst)
    time = curSimTime + lat
    addEventAt(event, time)
    log += [(curSimTime, event, src)] 
    
    
    
#################
# BASE NODE
#################
# Network is made out of nodes, each node has a name 
#connections are stored in the con dictionary, which returns the latency for the given destination node
#the nodes can be accessed either through the "top" list, or through the "topD" dict
class Node:
    def __init__(self, name):
        #name string
        self.name = name
        #dictionary of latency toNode -> latency 
        #latency can either be an integer or a function that returns an int
        self.con = {}
    
    #gets the latency from this node to dst node, with dst being the name of the node
    def getLatencyTo(self, dst):
        lat = self.con[dst]
        #lat is a function
        if(callable(lat)):
            return lat(self, dst)
        #lat must be an int
        return lat
        
#uses the duplicate function to duplicate the event with a new id and send copies to all nodes in the node's connection dictionary
def broadcast(node, event, duplicate=duplicateMSG):
    for dstNode in node.con:
        msg = duplicate(event)
        msg.dstNode = dstNode
        addMsgEvent(msg, node, dstNode)
        
#duplicates nodes and sends to all nodes in the node's connection dictionary that pass the exclude function
def conditionalBroadcast(node, event, excludeFunc, duplicate=duplicateMSG):
    for dstNode in node.con:
        #only create a msg if it passes the exclude function
        if excludeFunc(topD[dstNode]):
            msg = duplicate(event)
            msg.dstNode = dstNode
            addMsgEvent(msg, node, dstNode)



##########
# Simulator
#########
#blank placeholder function for when there is no debug function
def noDebug(eventName, data):
    return    

#   Runs the event list on the topology 
#requires the alg function which treats each event as the algorithm would 
#alg is a function alg(Event, Node)
#can receive a debug function which receives all events 
def simulate(inEList, topology, topDict, alg, debugF=noDebug, clean=True):
    global eventList
    global curSimTime
    global topD
    global log
    comOverHead=0
    proposals=0
    overheadFile='overhead.txt'
    consensusFile='consensus.txt'
    #changes global eventlist to received event list
    eventList = inEList
    topD = topDict
    #events log
    log = []
    #advances time until there are no events left
    curSimTime = 0
    firstProposalTime=None
    meanConsensus=0    
    while(len(eventList) > 0):
        #checks if there are no events at current time
        if curSimTime not in eventList:
            debugF('_BLANKTIMESTEP', curSimTime)
            curSimTime += 1
            continue
        debugF('_TIMESTEP', curSimTime)
        #gets all events for current time and iterates through them 
        
        events = eventList.pop(curSimTime)
        debugF('_EVENTS', events)
        for event in events:
            dstNode = topD[event.dstNode]
            if event.type=='msg':
                proposals+=1
                firstProposalTime=curSimTime
            else:
                comOverHead+=1
            #adds event to log
            log += [(curSimTime, event, None)] 
            #processes the event and adds any resulting events to the log
            debugF('_EVENT', event)
            alg(dstNode, event, debugF)
            if dstNode.type=='learner' and event.type=='commit':
                meanConsensus+=(curSimTime-firstProposalTime)
        curSimTime += 1
        #clean eventList to prevent errors
        if clean:
            for key in [k for k in eventList]:
                if key < curSimTime:
                    eventList.pop(key)
        debugF('_EVENTLIST', eventList)
    debugF('_END', curSimTime)
    comOverHead-=proposals
    
    with open(overheadFile, 'a') as f:
        f.write('%d,%d\n' % (proposals, comOverHead))
        
    with open(consensusFile, 'a') as f:
        f.write('%d,%.3f\n' % (proposals, meanConsensus))
    return log
    
#formats log to msgs[id] -> [msg, source, t0(, t1)]
def formatLog(log):
    msgs = {}
    for time, msg, source in log:
        if source is not None:
            source = source.name
            
        id = msg._id
        #sender/external event
        if id not in msgs:
            msgs[id] = [msg, source, time]
        #receiver
        else:
            msgs[id] += [time]
    return msgs	