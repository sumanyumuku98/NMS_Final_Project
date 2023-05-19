#Base events file
import sys
sys.path.append('../')
from base import Msg, addLocalEvent

#generate event list from file
#returns a dictionary of events
def generateEvenlist(filename):
    eFile = open(filename)
    eventList = {} # time -> [events]
    for line in eFile:
        #reads the file, splits each line into the required fields 
        line = line.strip().split(' ', 4)
        time, node, event = line[:3]
        #sets last field to none if it doesns't exist in the file
        if(len(line) > 3):
            id = line[3]
        else:
            id = None
        t = int(time)
        #creates a new Msg
        e = Msg(node, event)
        #optional step, adds a new field "text" to each Msg object
        e.id = id
        #adds event e to eventlist at time t
        addLocalEvent(eventList, e, t)
    eFile.close()
    return eventList






#   test function
#generates an eventlist and prints the times and events
if __name__ == '__main__':        
    eventList  = generateEvenlist('ev.ev')
    for t in eventList:
        print('-t:' + str(t) + '')
        for e in eventList[t]:
            print('| [{'+e.id+'} ' + e.type + ' to '+ e.dstNode + (' :"' + e.text + '"' if e.text!=None else '') + ']')
        print('')
