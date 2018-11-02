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

    bicycle_sum_trips = 0


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
        elif tempConnection.mode == "publicTransport":
            pt_sum_trips += tempConnection.stepLoad[-1]
            if tempConnection.infrastructure == "bus":
                pt_bus_trips += tempConnection.stepLoad[-1]
            elif tempConnection.infrastructure == "train":
                pt_train_trips += tempConnection.stepLoad[-1]
        elif tempConnection.mode == "bicycle":
            bicycle_sum_trips += tempConnection.stepLoad[-1]

    
    ####################
    # plot sum trips

    n_modes=3
    sumtrips=(car_sum_trips,pt_sum_trips, bicycle_sum_trips)
    fig, ax = plt.subplots()

    index = np.arange(n_modes)
    bar_width = 0.35
    rects1 = ax.bar(index, sumtrips, bar_width, label='trips')

    ax.set_ylabel('trips')
    ax.set_title('Sum Modal Split')
    ax.set_xticks(index )
    ax.set_xticklabels(('Car','PT', 'Bicycel'))

    fig.savefig('Pic/sumTrips.png')

    ############
    # plot for each Infrastructure and mode
    n_modes=5
    sumtrips=(car_autobahn_trips,car_countryroad_trips,pt_bus_trips, pt_train_trips, pt_sum_trips)
    fig, ax = plt.subplots()

    index = np.arange(n_modes)
    bar_width = 0.35
    rects1 = ax.bar(index, sumtrips, bar_width, label='trips')

    ax.set_ylabel('trips')
    ax.set_title('Sum Modal Split')
    ax.set_xticks(index )
    ax.set_xticklabels(('Car_autobahn', 'Car_countryroad','PT_bus', 'PT_train', 'Bicycle'))

    fig.savefig('Pic/sumTripsInfra.png')

def plotModalSplitOverAllCells(trafficCellDict):
    path='Pic/ModalSplitCells.png'
    
    car_sum_trips=0
    pt_sum_trips=0
    bicycle_sum_trips = 0
    walk_sum_trips = 0
    
    for tC in trafficCellDict.values():
        for modeTrips in tC.purposeDestinationMode['work'].values():
            for mode, trips in modeTrips.items():
                if mode == 'car':
                    car_sum_trips += trips
                elif mode == 'publicTransport':
                    pt_sum_trips += trips
                elif mode == 'bicycle':
                    bicycle_sum_trips += trips
                elif mode == 'walk':
                    walk_sum_trips += trips
                else:
                    print('Wrong Mode for Plot sum - plotModalSplitOverAllCells')
    
    n_modes=4
    sumtrips=(car_sum_trips,pt_sum_trips, bicycle_sum_trips, walk_sum_trips)
    fig, ax = plt.subplots()

    index = np.arange(n_modes)
    bar_width = 0.35
    rects1 = ax.bar(index, sumtrips, bar_width, label='trips')

    ax.set_ylabel('trips')
    ax.set_title('Sum Modal Split for TrafficCells')
    ax.set_xticks(index )
    ax.set_xticklabels(('Car','PT', 'Bicycle', 'Walk'))

    fig.savefig(path)

def plotModalSplitOverAllCellsStacked(trafficCellDict):
    path='Pic/ModalSplitCellsStacked.png'
    car_sum_trips=0
    pt_sum_trips=0
    bicycle_sum_trips = 0
    walk_sum_trips = 0
    
    for tC in trafficCellDict.values():
        for modeTrips in tC.purposeDestinationMode['work'].values():
            for mode, trips in modeTrips.items():
                if mode == 'car':
                    car_sum_trips += trips
                elif mode == 'publicTransport':
                    pt_sum_trips += trips
                elif mode == 'bicycle':
                    bicycle_sum_trips += trips
                elif mode == 'walk':
                    walk_sum_trips += trips
                else:
                    print('Wrong Mode for Plot sum - plotModalSplitOverAllCells')
    
    
    sumtrips=car_sum_trips + pt_sum_trips +bicycle_sum_trips +walk_sum_trips
    car_sum_trips =(car_sum_trips/sumtrips) * 100
    pt_sum_trips = (pt_sum_trips/sumtrips) * 100
    bicycle_sum_trips = (bicycle_sum_trips /sumtrips) * 100
    walk_sum_trips = (walk_sum_trips/sumtrips)*100
    index = np.arange(1)
    bar_width = 0.35

    fig = plt.figure()
    p1 = plt.bar(index, car_sum_trips, bar_width)
    p2 = plt.bar(index, pt_sum_trips, bar_width, bottom = car_sum_trips)
    p3 = plt.bar(index, bicycle_sum_trips, bar_width,  bottom = (car_sum_trips+ pt_sum_trips))
    p4 = plt.bar(index, walk_sum_trips, bar_width,  bottom = (car_sum_trips+ pt_sum_trips+ bicycle_sum_trips))

    plt.ylabel('Percent')
    plt.title("Modal Split stacked")
    plt.legend((p1[0], p2[0], p3[0], p4[0]), ('Car', 'PT', 'Bicycle', 'Walk'))

    fig.savefig(path)


def plotModalSplitwithinCells(trafficCellDict):
    path='Pic/ModalSplitwithinCells.png'
    
    car_sum_trips=0
    pt_sum_trips=0
    bicycle_sum_trips = 0
    walk_sum_trips = 0
    
    for tcID, tC in trafficCellDict.items():
        for destination, modeTrips in tC.purposeDestinationMode['work'].items():
            if destination == tcID:
                for mode, trips in modeTrips.items():
                    if mode == 'car':
                        car_sum_trips += trips
                    elif mode == 'publicTransport':
                        pt_sum_trips += trips
                    elif mode == 'bicycle':
                        bicycle_sum_trips += trips
                    elif mode == 'walk':
                        walk_sum_trips += trips
                    else:
                        print('Wrong Mode for Plot sum - plotModalSplitOverAllCells')
            else:
                continue
    
    n_modes=4
    sumtrips=(car_sum_trips,pt_sum_trips, bicycle_sum_trips, walk_sum_trips)
    fig, ax = plt.subplots()

    index = np.arange(n_modes)
    bar_width = 0.35
    rects1 = ax.bar(index, sumtrips, bar_width, label='trips')

    ax.set_ylabel('trips')
    ax.set_title('Sum Modal Split within TrafficCells')
    ax.set_xticks(index)
    ax.set_xticklabels(('Car','PT', 'Bicycle', 'Walk'))

    fig.savefig(path)

def plotModalSplitBetweenCells(trafficCellDict):
    path='Pic/ModalSplitBetweenCells.png'
    
    car_sum_trips=0
    pt_sum_trips=0
    bicycle_sum_trips = 0
    walk_sum_trips = 0
    
    for tcID, tC in trafficCellDict.items():
        for destination, modeTrips in tC.purposeDestinationMode['work'].items():
            if destination != tcID:
                for mode, trips in modeTrips.items():
                    if mode == 'car':
                        car_sum_trips += trips
                    elif mode == 'publicTransport':
                        pt_sum_trips += trips
                    elif mode == 'bicycle':
                        bicycle_sum_trips += trips
                    elif mode == 'walk':
                        walk_sum_trips += trips
                    else:
                        print('Wrong Mode for Plot sum - plotModalSplitOverAllCells')
            else:
                continue
    
    n_modes=4
    sumtrips=(car_sum_trips,pt_sum_trips, bicycle_sum_trips, walk_sum_trips)
    fig, ax = plt.subplots()

    index = np.arange(n_modes)
    bar_width = 0.35
    ax.bar(index, sumtrips, bar_width, label='trips')

    ax.set_ylabel('trips')
    ax.set_title('Sum Modal Split within TrafficCells')
    ax.set_xticks(index)
    ax.set_xticklabels(('Car','PT', 'Bicycle', 'Walk'))

    fig.savefig(path)







        
        