import sys
import networkx as nx
from collections import defaultdict 
from DataHandler import readConnectionRows as conReader
from DataHandler import redConnectionWeights as weightReader
from DataHandler import readDefaultCapacity
from DataHandler import readBasicLoad
from Infrastructure.Connection import Connection 

#Networkgraph
infraNetworkGraph = nx.MultiGraph()

#Infrastructure to include
infra=["countryroad","train", "autobahn"]
modes=["car", "publicTransport", "bicycle"]
connections=["car_countryroad", "publicTransport_train", "car_autobahn", "publicTransport_bus", "bicycle_countryroad"]

#global cost variables
costModes=None

def getShortestPaths_withStartMode(start, end, cellDict, jsonParamter):
    #Weight to punish mode interchangig
    changingWeight=jsonParamter['changingModeWeigth']

    #dict of shortest paths
    otherPath=defaultdict()
    otherConnections = defaultdict()

    for m in modes:
        #skip bicycel mode if the target node is not neighbour of the start node
        if (end not in infraNetworkGraph.adj[start].keys()) and (start != end) and (m == 'bicycle'):
            continue
        #calc shortest paths
        path, connections = calc_dijkstra_withStartMode(start, end, cellDict, m, changingWeight)
        if path:
            otherPath[m]=path
            otherConnections[m]=connections
        else:
            otherPath[m]=None
            otherConnections[m]=None
            print("Start: " +start + " End: " + end + " Mode: " + m )
    
    return otherPath, otherConnections


def bildGraph(): 

    infraConnections = defaultdict()

    #---- read Infrastructure 
    for infraElement in infra:
        infraConnections[infraElement]=conReader(infraElement)

    #--- read Capacity of Connections
    defaultCapacity = readDefaultCapacity()
    basicLoad = readBasicLoad()

    #--- add all edges to graph
    addEdges(infraConnections[infra[0]], connections[0], defaultCapacity[connections[0]], basicLoad[connections[0]])
    addEdges(infraConnections[infra[1]], connections[1], defaultCapacity[connections[1]], basicLoad[connections[1]])
    addEdges(infraConnections[infra[2]], connections[2], defaultCapacity[connections[2]], basicLoad[connections[2]])
    addEdges(infraConnections[infra[0]], connections[3], defaultCapacity[connections[3]], basicLoad[connections[3]])
    addEdges(infraConnections[infra[0]], connections[4], defaultCapacity[connections[4]], basicLoad[connections[4]])


    #--- read Cost
    global costModes
    costModes = weightReader()
    
        
def addEdges(data, connection, capacity, basicLoad):
    for row in data:
        str = row.split(";")
        #Get Gemeindekennzahlen
        location_1 = str[0].split("_")[0]
        location_2 = str[1].split("_")[0]
        #Get distance
        dist = int(str[2])
        #Get Level of Service data
        losData=1

        #Generate connection object
        con = Connection(location_1, location_2, connection, dist, losData, capacity, basicLoad)
        
        #Save edge
        infraNetworkGraph.add_edge(location_1, location_2, con=con)

##---- MAIN Djikstra      
def calc_dijkstra_withStartMode(start_node, target_node, trafficCells, first_mode, changingWeight):
    data = infraNetworkGraph.copy()
    
    ##Assign variable costs to all edges
    for u,v,d in data.edges(data=True):
        d['con'].setGlobalWeightFactors(costModes[d['con'].getConnectionType()], 80)
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
            if last_type == connections[1] or last_type == connections[3] or last_type == connections[4]:
                expand_car_nodes = False

        for u,v,d in data.edges(min_node, data=True):        
        #Skip car edges if necessary
            if (d['con'].getConnectionType() == connections[0] or d['con'].getConnectionType() == connections[2]) and not expand_car_nodes:
                continue
        #Skip edges from start_node if they do not have the correct mode
            if(u == start_node and d['con'].mode != first_mode):
                continue

            #Get weight
            #punish mode change
            if last_type == d['con'].getConnectionType():
                weight = d['con'].getWeight()
            else:
                weight = d['con'].getWeight() + changingWeight

            #Get next node
            if u != min_node:
                cur = u
            else:
                cur = v

            if cur not in shortest_paths or (weight + curr_min_weight) < shortest_paths[cur]:
                shortest_paths[cur] = (weight + curr_min_weight)
                prev[cur] = (min_node, d['con'].getConnectionType(), d['con'].distance, d['con'])

    #End Algorithm
    path = []
    connectionsList=[]
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

        #add sonnection to set of connections
        connectionsList.insert(0,previous[3])

    return path, connectionsList