#Base topology file
import sys
sys.path.append('../')
from base import Node

#bidirectional connection with same latency
def addbidcon(n1, n2, lat):
    n1.con[n2.name] = lat
    n2.con[n1.name] = lat

#generate topology from file
#returns a list of nodes and a dictionary of nodes
def generateTopology(filename):
    tFile = open(filename)
    nodes = tFile.readline().strip().split(' ')
    top = []  #list of nodes
    topD = {} #dic name -> node
    for n in nodes:
        node = Node(n)
        top += [node]
        topD[n] = node
    #add bidirectional connections
    for line in tFile:
        line = line.strip().split('-')
        n1 = line[0]
        n2, lat = line[1].split(' ')
        addbidcon(topD[n1], topD[n2], int(lat))
    tFile.close()
    return (top, topD)






#   test function
#generates a topology and prints the node names and the latency between them
if __name__ == '__main__':        
    top, _  = generateTopology('top.top')
    for n in top:
        print(n.name + ':' + str(n.con))
