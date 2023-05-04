import xml.etree.ElementTree as ET
from init import save_variable,NET_NAME,TRA_NUM
import traci
START_TIME = 0
END_TIME = 5200

net_tree = ET.parse(NET_NAME+'.net.xml')
net_root = net_tree.getroot()
edge_list = net_root.findall("edge")
normal_edge_list = []
internal_list = []


edge_to_junction = {}
junction_list = []
junction_dict = {}
all_junction_list = net_root.findall("junction")
edge_list_partial = []
for edge in edge_list:
    if edge.get('function')=="internal":
        continue
    edge_list_partial.append(edge.get('id'))
    edge_to_junction.update({edge.get('id'):[edge.get('from'),edge.get('to')]})
    if edge.get('from') not in junction_dict:
        junction_dict.update({edge.get('from'):{"from":[edge.get('id')],"to":[]}})
    else:
        junction_dict[edge.get('from')]["from"].append(edge.get('id'))
    
    if edge.get('to') not in junction_dict:
        junction_dict.update({edge.get('to'):{"to":[edge.get('id')],"from":[]}})
    else:
        junction_dict[edge.get('to')]["to"].append(edge.get('id'))

sumocfgfile = NET_NAME + ".sumo.cfg" 
traci.start(['sumo', "-c", sumocfgfile])

trajectory_data = {}

for step in range(END_TIME):
    traci.simulationStep()
    if step<START_TIME:
        continue
    current_vehicle_IDlist = traci.vehicle.getIDList()
    for vehicle in current_vehicle_IDlist:
        edgeID = traci.vehicle.getRoadID(vehicle)
        if edgeID in edge_list_partial:
            current_loc = (edgeID,step)
            if vehicle in trajectory_data:
                pre_loc = trajectory_data[vehicle][-1]
                if pre_loc[0] != edgeID:
                    trajectory_data[vehicle].append(current_loc)
            else:
                trajectory_data[vehicle] = []
                trajectory_data[vehicle].append(current_loc)

              
traci.close()
with open('./trajectory.txt', 'w+') as f:
    for vehicle, trajectory in trajectory_data.items():
        f.write(f"{vehicle} {trajectory}\n".format(vehicle, trajectory))

save_variable(trajectory_data,'trajectory_'+NET_NAME+'_%d.pkl'%TRA_NUM)
save_variable(trajectory_data,'LDP_CODE/trajectory_'+NET_NAME+'_%d.pkl'%TRA_NUM)


