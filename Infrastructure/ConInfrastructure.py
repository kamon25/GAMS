import sys
import networkx as nx

trafficNetworkGraph = nx.MultiGraph()

def bildGraph():    
    trafficNetworkGraph.add_weighted_edges_from([(1, 2, 0.8), (2, 3, 0.9),(4, 5, 0.6), (3, 5, 0.8)],mode='car')

    ############################### Continue Here!