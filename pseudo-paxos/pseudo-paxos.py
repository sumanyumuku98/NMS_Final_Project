#add folder directory above to python's path
from sys import path
path.append('..')

##################
# Debug functions 
##################
#replacement debug function, ignores BLANKTIMESTEP event and simply prints anything else
def debugNOBLANK(eventName, data):
    if eventName in ('_BLANKTIMESTEP', '_EVENTLIST', '_EVENTS'):
        return
    if isinstance(data, Msg):
        return
        #prints Msg dicts rather than the object pointer location
        print(eventName + ' ' + str(data.__dict__))
    else:
        print(eventName + ' ' + str(data))
        
######################    
# Paxos
######################    
def isAcceptor(node):
    return node.type == 'acceptor'
def isLearner(node):
    return node.type == 'learner'
    
from base import Msg, conditionalBroadcast, addMsgEvent
def paxos(node, event, debugF):
    if(node.type == 'proposer'):
        #new message, send a prepare to then propose the message
        if event.type == 'msg':
            if(node.phase != 0):
                return 
            debugF('Proposer ' + node.name, 'sends prepare')
            node.phase = 1
            node.waiting[event.text] = [x for x in node.quorum]
            #msg
            msg = Msg(None, 'prepare')
            msg.text = event.text
            msg.source = node.name
            conditionalBroadcast(node, msg, isAcceptor)
        #receives ready from acceptor
        if event.type == 'ready':
            if(node.phase != 1):
                return 
            debugF('Proposer ' + node.name, 'receives ready from ' + event.source)
            node.waiting[event.text].remove(event.source)
            #all ready
            if node.waiting[event.text] == []:
                node.phase = 2
                node.waiting[event.text] = [x for x in node.quorum]
                debugF('Proposer ' + node.name, 'proposes ' + event.text)
                msg = Msg(None, 'propose')
                msg.text = event.text
                msg.source = node.name
                conditionalBroadcast(node, msg, isAcceptor)
        #receives accept from acceptor
        if event.type == 'accept':
            if(node.phase != 2):
                return 
            debugF('Proposer ' + node.name, 'receives accept ' + event.text + ' from ' + event.source)
            node.waiting[event.text].remove(event.source)
            #quorum accepted
            if node.waiting[event.text] == []:
                node.phase = 0
                debugF('Proposer ' + node.name, 'commits ' + event.text)
                msg = Msg(None, 'commit')
                msg.text = event.text
                msg.source = node.name
                conditionalBroadcast(node, msg, isLearner)                
            
    elif(node.type == 'acceptor'):
        #receives prepare, replies with ready
        if event.type == 'prepare':
            debugF('Acceptor ' + node.name, 'receives prepare from ' + event.source)
            msg = Msg(event.source, 'ready')
            msg.text = event.text
            msg.source = node.name
            addMsgEvent(msg, node, event.source)
        #receives propose, replies with accept
        if event.type == 'propose':
            debugF('Acceptor ' + node.name, 'receives propose from ' + event.source)
            msg = Msg(event.source, 'accept')
            msg.text = event.text
            msg.source = node.name
            addMsgEvent(msg, node, event.source)
        
    elif(node.type == 'learner'):
        if event.type == 'commit':
            debugF('Learner ' + node.name, 'receives commit ' + event.text + ' from ' + event.source)
    
######################    
# Simulate
######################    
from pseudopaxospre import generateTop, generateEventList
from base import simulate
eventList = generateEventList()
top, topD = generateTop()
log = simulate(eventList, top, topD, paxos, debugNOBLANK)

from svg import generateSvg
generateSvg('a.svg', log, '5x', '5x')