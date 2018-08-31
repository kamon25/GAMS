import sys
import networkx as nx
from collections import defaultdict 
from DataHandler import readConnectionRows as conReader
from DataHandler import redConnectionWeights as weightReader

#Networkgraph
infraNetworkGraph = nx.MultiGraph()

#Infrastructure to include
infra=["countryroad","train", "autobahn"]
modes=["car", "publicTransport"]
connections=["car_countryroad", "publicTransport_train", "car_autobahn", "publicTransport_bus"]

#global cost variables
costModes=None

def getShortestPath(start, end, cellDict):
  
    otherPath = calc_dijkstra(start, end, cellDict)
    
    return otherPath


def getShortestPaths_withStartMode(start, end, cellDict):
    
    #dict of shortest paths
    otherPath=defaultdict()

    for m in modes:
        path = calc_dijkstra_withStartMode(start, end, cellDict, m)
        if path:
            otherPath[m]=path
        else:
            otherPath[m]=None
            print("Start: " +start + " End: " + end + " Mode: " + m )
    
    return otherPath


def bildGraph(): 

    infraConnections = defaultdict()

    #---- read Infrastructure 
    for infraElement in infra:
        infraConnections[infraElement]=conReader(infraElement)

    #--- add all edges to graph
    addEdges(infraConnections[infra[0]], connections[0])
    addEdges(infraConnections[infra[1]], connections[1])
    addEdges(infraConnections[infra[2]], connections[2])
    addEdges(infraConnections[infra[0]], connections[3])

    #--- read Cost
    global costModes
    costModes = weightReader()
    
        
def addEdges(data, connection):
    for row in data:
        str = row.split(";")
        #Get Gemeindekennzahlen
        location_1 = str[0].split("_")[0]
        location_2 = str[1].split("_")[0]
        #Get distance
        dist = int(str[2])

        #Save edge
        infraNetworkGraph.add_edge(location_1, location_2, weight=dist, connect=connection, dist=dist)

##---- MAIN Djikstra
def calc_dijkstra(start_node, target_node, trafficCells):
    data = infraNetworkGraph.copy()
    
    ##Assign variable costs to all edges
    for u,v,d in data.edges(data=True):
        d['weight'] *= costModes[d['connect']]
        
    #Unvisited nodes
    unvisited = list(data.nodes())
    #Dict for shortest paths
    shortest_paths = {start_node: 0}
    #Save previous nodes here
    prev = {}
    
    #Start algorithm
    while unvisited:
      #If we found our destination -> break
        if target_node in shortest_paths and target_node not in unvisited:
            break

        min_node = None
        expand_car_nodes = True

      #Search for next node to visit -> minimum weight
        for node in unvisited:
            if node in shortest_paths:
                if min_node is None:
                    min_node = node
                elif shortest_paths[node] < shortest_paths[min_node]:
                    min_node = node

        if min_node is None:
            break

      #Visit the selected node
        unvisited.remove(min_node)
      #Save the current minimum weight for this node
        curr_min_weight = shortest_paths[min_node]

      #Check used edge between min_node and previous_node
        last_type=None
        if min_node in prev:
            last_type = prev[min_node][1]

        #If used edge was public transport or bike -> 
        # do not expand car nodes on this path
        if last_type!=None:
            if last_type == connections[1] or last_type == connections[3]:
                expand_car_nodes = False

        for u,v,d in data.edges(min_node, data=True):
        #Skip car edges if necessary
            if (d['connect'] == connections[0] or d['connect'] == connections[2]) and not expand_car_nodes:
                continue

            #Get weight
            weight = d['weight']

            #Get next node
            if u != min_node:
                cur = u
            else:
                cur = v

            if cur not in shortest_paths or (weight + curr_min_weight) < shortest_paths[cur]:
                shortest_paths[cur] = (weight + curr_min_weight)
                prev[cur] = (min_node, d['connect'], d['dist'])

    #End Algorithm
    path = []
    #print(shortest_paths[target_node])
    if target_node in shortest_paths:
      ###Trace back from target###
      curr_node = target_node
      path.insert(0, trafficCells[curr_node].cellID)
      while curr_node in prev:
        #Look up city
        previous = prev[curr_node]
        city = trafficCells[previous[0]].cellID

        path.insert(0, (city, previous[1], previous[2]))
        curr_node = previous[0]

    return path
      
def calc_dijkstra_withStartMode(start_node, target_node, trafficCells, first_mode):
    data = infraNetworkGraph.copy()
    
    ##Assign variable costs to all edges
    for u,v,d in data.edges(data=True):
        d['weight'] *= costModes[d['connect']]
    #Unvisited nodes
    unvisited = list(data.nodes())
    #Dict for shortest paths
    shortest_paths = {start_node: 0}
    #Save previous nodes here
    prev = {}
    
    #Start algorithm
    while unvisited:
      #If we found our destination -> break
        if target_node in shortest_paths and target_node not in unvisited:
            break

        min_node = None
        expand_car_nodes = True

      #Search for next node to visit -> minimum weight
        for node in unvisited:
            if node in shortest_paths:
                if min_node is None:
                    min_node = node
                elif shortest_paths[node] < shortest_paths[min_node]:
                    min_node = node

        if min_node is None:
            break

      #Visit the selected node
        unvisited.remove(min_node)
      #Save the current minimum weight for this node
        curr_min_weight = shortest_paths[min_node]

      #Check used edge between min_node and previous_node
        last_type=None
        if min_node in prev:
            last_type = prev[min_node][1]

        #If used edge was public transport or bike -> 
        # do not expand car nodes on this path
        if last_type!=None:
            if last_type == connections[1] or last_type == connections[3]:
                expand_car_nodes = False

        for u,v,d in data.edges(min_node, data=True):        
        #Skip car edges if necessary
            if (d['connect'] == connections[0] or d['connect'] == connections[2]) and not expand_car_nodes:
                continue
        #Skip edges from start_node if they do not have the correct mode
            if(u == start_node and d['connect'].split('_')[0] != first_mode):
                continue

            #Get weight
            weight = d['weight']

            #Get next node
            if u != min_node:
                cur = u
            else:
                cur = v

            if cur not in shortest_paths or (weight + curr_min_weight) < shortest_paths[cur]:
                shortest_paths[cur] = (weight + curr_min_weight)
                prev[cur] = (min_node, d['connect'], d['dist'])

    #End Algorithm
    path = []
    #print(shortest_paths[target_node])
    if target_node in shortest_paths:
      ###Trace back from target###
      curr_node = target_node
      path.insert(0, trafficCells[curr_node].cellID)
      while curr_node in prev:
        #Look up city
        previous = prev[curr_node]
        city = trafficCells[previous[0]].cellID

        path.insert(0, (city, previous[1], previous[2]))
        curr_node = previous[0]

    return path