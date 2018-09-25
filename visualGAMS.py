import numpy as np
import matplotlib.pyplot as plt
from collections import namedtuple


def plotConnectionComparison(connection1, connection2):
    plt.figure()
    plt.plot(connection1.occupancy, label=connection1.getConnectionType())
    plt.plot(connection2.occupancy, label=connection2.getConnectionType())
    plt.ylabel('Auslastung')
    plt.legend()
    plt.savefig('Pic/occupy.png')


    plt.figure()
    plt.plot(connection1.stepLoad, label=connection1.getConnectionType())
    plt.plot(connection2.stepLoad, label=connection2.getConnectionType())
    plt.ylabel('trips')
    plt.legend()
    plt.savefig('Pic/trips.png')

def plotModalSplitConnections(trafficCellDict):
    connections = set()
    path='Pic'
   
    car_sum_trips=0
    car_autobahn_trips = 0
    car_countryroad_trips= 0
    

    pt_sum_trips=0
    pt_bus_trips=0
    pt_train_trips=0


    for trafficCell in trafficCellDict.values():
        for cellValues in trafficCell.pathConnectionList.values():
            for modeValues in cellValues.values():
                connections = connections.union(set(modeValues))
    
    for tempConnection in connections:
        if tempConnection.mode == "car":
            car_sum_trips += tempConnection.stepLoad[-1]
            if tempConnection.infrastructure == "countryroad":
                car_countryroad_trips += tempConnection.stepLoad[-1]
            elif tempConnection.infrastructure == "autobahn":
                car_autobahn_trips += tempConnection.stepLoad[-1]
        if tempConnection.mode == "publicTransport":
            pt_sum_trips += tempConnection.stepLoad[-1]
            if tempConnection.infrastructure == "bus":
                pt_bus_trips += tempConnection.stepLoad[-1]
            elif tempConnection.infrastructure == "train":
                pt_train_trips += tempConnection.stepLoad[-1]
    
    ####################
    # plot sum trips

    n_modes=2
    sumtrips=(car_sum_trips,pt_sum_trips)
    fig, ax = plt.subplots()

    index = np.arange(n_modes)
    bar_width = 0.35
    rects1 = ax.bar(index, sumtrips, bar_width, label='trips')

    ax.set_ylabel('trips')
    ax.set_title('Sum Modal Split')
    ax.set_xticks(index )
    ax.set_xticklabels(('Car','PT'))

    fig.savefig('Pic/sumTrips.png')

    ############
    # plot for each Infrastructure and mode
    n_modes=4
    sumtrips=(car_autobahn_trips,car_countryroad_trips,pt_bus_trips, pt_train_trips)
    fig, ax = plt.subplots()

    index = np.arange(n_modes)
    bar_width = 0.35
    rects1 = ax.bar(index, sumtrips, bar_width, label='trips')

    ax.set_ylabel('trips')
    ax.set_title('Sum Modal Split')
    ax.set_xticks(index )
    ax.set_xticklabels(('Car_autobahn', 'Car_countryroad','PT_bus', 'PT_train'))

    fig.savefig('Pic/sumTripsInfra.png')

    
    




        
        