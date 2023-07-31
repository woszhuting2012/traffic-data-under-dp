import xml.etree.ElementTree as ET
from global_DP.init import save_variable,NET_NAME
import traci
import sys
START_TIME = 0
END_TIME = 20000

sumocfgfile = 'Datasets/' + NET_NAME + ".sumo.cfg" 
traci.start(['sumo', "-c", sumocfgfile])

vehicle_processed = []
trajectory_data = {}
trajectory_data_saved = {}
for step in range(END_TIME):
    traci.simulationStep()
    if step<START_TIME:
        continue
    current_vehicle_IDlist = traci.vehicle.getIDList()
    for vehicle in current_vehicle_IDlist:
        if vehicle not in vehicle_processed:
            route = traci.vehicle.getRoute(vehicle)
            first = 1

            for edge in route:
                loc = (edge,-1)
                if first:
                    trajectory_data[vehicle] = []
                    first = 0
                trajectory_data[vehicle].append(loc)
            vehicle_processed.append(vehicle)
        cur_edge = traci.vehicle.getRoadID(vehicle)
        cur_loc = (cur_edge,-1)
        if trajectory_data[vehicle].count(cur_loc):
            cur_idx = trajectory_data[vehicle].index(cur_loc)
            trajectory_data[vehicle][cur_idx]=(cur_edge,step)
            
traci.close()

save_variable(trajectory_data,'global_DP/trajectory_'+NET_NAME+'.pkl')
save_variable(trajectory_data,'local_DP/trajectory_'+NET_NAME+'.pkl')



