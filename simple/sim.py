#add directory above to python's path to access base.py and svg.py
from sys import path
path.append('..')

##################
# Debug functions 
##################
#replacement debug function, ignores three internal events and simply prints anything else
def debugNOBLANK(eventName, data):
	#ignore BLANKTIMESTEP, EVENTLIST and EVENTS events
    if eventName in ('_BLANKTIMESTEP', '_EVENTLIST', '_EVENTS'):
        return
    #ignore Msg objects
    if isinstance(data, Msg):
        return
    else:
        print(eventName + ' ' + str(data))
        
#replacement debug function, only prints node and time events
def debugNodeTime(eventName, data):
    if eventName.split(' ')[0] in ('Node', '_TIMESTEP', '_END'):
        print(eventName + ' ' + str(data))
        
        
######################    
# Algorithm definition
######################    
from base import Msg, addMsgEvent
#minimum accepts required for a commit
acceptThreshold = 2    

#makes a msg object
def makeMsg(dst, event, id, text, source):
    msg = Msg(dst, event)
    msg.id = id
    msg.text = text
    msg.source = source
    return msg

#alg
def simple(node, event, debugF):    
    #received message from client, proposes to other nodes
    if event.type == 'msg':
        node.msgAccept[event.id] = 0
        debugF('Node ' + node.name + ' proposes', event.id)
        #iterates through all other nodes
        for dstNode in top:
            #skip self
            if dstNode == node:
                continue
            #creates a confirmation message to send and adds required fields
            text = 'p('+event.id+')'
            confirmationMsg = makeMsg(dstNode.name, 'propose', event.id, text, node.name)
            addMsgEvent(confirmationMsg, node, dstNode)
            
    #message proposed from another node, instantly accepts
    elif event.type == 'propose':
        #gets source node and sends a confirmation message back
        dstNode = topD[event.source]
        text = 'a('+event.id+')'
        acceptMsg = makeMsg(dstNode.name, 'accept', event.id, text, node.name)
        debugF('Node ' + node.name + ' accepts', event.id)
        addMsgEvent(acceptMsg, node, dstNode)
        
    #received accept, updates counter and commits when able
    elif event.type == 'accept':
        msg = event.id
        node.msgAccept[msg] += 1
        debugF('Node ' + node.name + ' receive accept', msg + ' from ' + event.source)
        if(node.msgAccept[msg] == acceptThreshold):
            debugF('Node ' + node.name + ' commits', msg)
         
         
######################    
# Run simulation
######################
#topology	
from top import generateTopology
#generates topology from file
top, topD = generateTopology('top.top')
#adds a new field to each node, number of acceptors of each message
for node in top:
    node.msgAccept = {}
        
#eventlist    
from event import generateEvenlist
eventList = generateEvenlist('ev.ev')   
    
#simulation
from base import simulate
#runs simulation
debugFunction = debugNOBLANK
log = simulate(eventList, top, topD, simple, debugFunction)

#generates svg from log
from svg import generateSvg
generateSvg('a.svg', log, '5x', '5x')