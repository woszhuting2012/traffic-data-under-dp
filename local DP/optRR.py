import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
from LDP_step0 import load_variable
from LDP_step0 import START_TIME, END_TIME, epsilon, START_X, START_Y, UNIT_LEN,NET_NAME
from math import exp
import numpy as np
import random
from tqdm import tqdm
import time
# class _network:
#     def __init__(self,_edge_list,_junction_list) -> None:
#         self.edge = _edge_list
#         self.junction = _junction_list
    
# class _edge:
#     def __init__(self,_id,_from,_to) -> None:
#         self.id = _id
#         self.from_junction = _from
#         self.to_junction = _to
#     def get(self,attribute):
#         if attribute=='id': return self.id
#         elif attribute=='from': return self.from_junction
#         elif attribute=='to': return self.to_junction

# class _junction:
#     def __init__(self,_id,_edge_list,_x,_y) -> None:
#         self.id = _id
#         self.edge_list = _edge_list
#         self.x = _x
#         self.y = _y
#     def get(self,attribute):
#         if attribute=='id': return self.id
#         elif attribute=='x': return self.x
#         elif attribute=='y': return self.y


# test_edge_0 = _edge('0','B','A')
# test_edge_1 = _edge('1','A','C')
# test_edge_2 = _edge('2','C','A')
# test_edge_3 = _edge('3','A','D')
# test_edge_4 = _edge('4','D','A')
# test_edge_5 = _edge('5','A','E')
# test_edge_6 = _edge('6','E','A')
# test_edge_7 = _edge('7','A','B')
# test_edge_list = [test_edge_0,test_edge_1,test_edge_2,test_edge_3,test_edge_4,test_edge_5,test_edge_6,test_edge_7]

# test_junction_A = _junction('A',test_edge_list,1,1)
# test_junction_B = _junction('B',[test_edge_0,test_edge_7],1,1)
# test_junction_C = _junction('C',[test_edge_1,test_edge_2],1,1)
# test_junction_D = _junction('D',[test_edge_3,test_edge_4],1,1)
# test_junction_E = _junction('E',[test_edge_5,test_edge_6],1,1)
# test_junction_list = [test_junction_A,test_junction_B,test_junction_C,test_junction_D,test_junction_E]

# test_network = _network(test_edge_list,test_junction_list)

def random_del(L,n):
    to_delete = set(random.sample(range(len(L)), n))
    del_value = []
    for index in  to_delete:
        del_value.append(L[index])
    for val in del_value:
        L.remove(val)


def random_out(_edge_list_out, _real_out):
    n = len(_edge_list_out)
    if n==0:
        n = 1
        _edge_list_out.append(None)
    p = 1/(exp(epsilon)+n)
    #print(p)
    random_number = random.random()
    random_loc = _real_out
    #print("n="+str(n))
    for i in range(n):
        if random_number<p*(i+1):
            random_loc = _edge_list_out[i]
            break
    #print(_edge_list_out,_real_out,random_loc,random_number)
    return random_loc

start_time = time.time()
net_tree = ET.parse(NET_NAME+".net.xml")
net_root = net_tree.getroot()
edge_list = net_root.findall("edge")
all_junction_list = net_root.findall("junction")
# edge_list = test_edge_list
# all_junction_list = test_junction_list

junction_list_partial = []
for junction in all_junction_list:
    junction_x = float(junction.get("x"))
    junction_y = float(junction.get("y"))
    if junction.get('type')=='internal':
        continue
    if START_X<=junction_x<=START_X+UNIT_LEN and START_Y<=junction_y<=START_Y+UNIT_LEN:
        junction_list_partial.append(junction.get("id"))
edge_id_list_partial = []
edge_list_partial = []
junction_in = {}
junction_out = {}
for edge in edge_list:
    if edge.get('function')=="internal":
        continue
    if edge.get('from') in junction_list_partial or edge.get('to') in junction_list_partial:
        edge_id_list_partial.append(edge.get('id'))
        edge_list_partial.append(edge)
print(len(edge_list_partial))
print(len(junction_list_partial))
trajectory_data = load_variable('trajectory_'+NET_NAME+'.pkl')
remove = 1
if remove:
    max_tra = 7
    for vehicle,trajectory in trajectory_data.items():
        edge_passed_list = []
        for current_loc_t in trajectory:
            if START_TIME < current_loc_t[1] < END_TIME:
                if current_loc_t[0] not in edge_id_list_partial:
                    continue
                if current_loc_t[0] not in edge_passed_list:
                    edge_passed_list.append(current_loc_t[0])
        if len(edge_passed_list)>=max_tra:
            random_del(trajectory,len(edge_passed_list)-max_tra)
#print(junction_list_partial)
per_sum = 0
for i in tqdm(range(1)):
    junction_dict = {}
    origin_data = {}
    noisy_data = {}
    edge_to_junction = {}
    for edge in edge_list_partial:
        if edge.get('function')=="internal":
            continue
        origin_data.update({edge.get('id'):0})
        noisy_data.update({edge.get('id'):0})
        edge_to_junction.update({edge.get('id'):[edge.get('from'),edge.get('to')]})
        if edge.get('from') not in junction_dict:
            junction_dict.update({edge.get('from'):{"from":[edge.get('id')],"to":[]}})
        else:
            junction_dict[edge.get('from')]["from"].append(edge.get('id'))
        
        if edge.get('to') not in junction_dict:
            junction_dict.update({edge.get('to'):{"to":[edge.get('id')],"from":[]}})
        else:
            junction_dict[edge.get('to')]["to"].append(edge.get('id'))
        
# with open('./LDP_DATA/junction.txt', 'w+') as f:
#     for junction,edge in junction_dict.items():
#         f.write(str(junction)+' '+str(edge)+"\n")

# t00 = [('0',0),('1',1)]
# t01 = [('0',0),('3',1)]
# t02 = [('0',0),('5',1)]
# t03 = [('2',0),('3',1)]
# t04 = [('2',0),('5',1)]
# t05 = [('2',0),('7',1)]
# t06 = [('4',0),('5',1)]
# t07 = [('4',0),('7',1)]
# t08 = [('4',0),('1',1)]
# t09 = [('6',0),('7',1)]
# t10 = [('6',0),('1',1)]
# t11 = [('6',0),('3',1)]

# trajectory_data = {}
# N = 1000
# M = round(np.log10(N))
# #print(M)
# for i in range(N):
#     if i<N//12+1: trajectory_data.update({str(i).zfill(M):t00})
#     elif i<N//12*2+1: trajectory_data.update({str(i).zfill(M):t01})
#     elif i<N//12*3+1: trajectory_data.update({str(i).zfill(M):t02})
#     elif i<N//12*4+2: trajectory_data.update({str(i).zfill(M):t03})
#     elif i<N//12*5+2: trajectory_data.update({str(i).zfill(M):t04})
#     elif i<N//12*6+2: trajectory_data.update({str(i).zfill(M):t05})
#     elif i<N//12*7+3: trajectory_data.update({str(i).zfill(M):t06})
#     elif i<N//12*8+3: trajectory_data.update({str(i).zfill(M):t07})
#     elif i<N//12*9+3: trajectory_data.update({str(i).zfill(M):t08})
#     elif i<N//12*10+4: trajectory_data.update({str(i).zfill(M):t09})
#     elif i<N//12*11+4: trajectory_data.update({str(i).zfill(M):t10})
#     else: trajectory_data.update({str(i).zfill(M):t11})

    for vehicle,trajectory in trajectory_data.items():
        last_loc = None
        for loc_t in trajectory:
            if loc_t[1]<START_TIME or loc_t[1]>END_TIME:
                break
            if loc_t[0] not in edge_id_list_partial:
                continue
            origin_data[loc_t[0]] += 1
            if not last_loc:
                tmp = random_out([], loc_t[0])
                if tmp:
                    noisy_data[tmp] += 1
            else:
                for junction in junction_dict:
                    if junction_dict[junction]['to'].count(last_loc):
                        edge_list_out = []
                        for edge in junction_dict[junction]['from']:
                            if edge!=loc_t[0]:
                                edge_list_out.append(edge)
                        tmp = random_out(edge_list_out, loc_t[0])
                        if tmp:
                            noisy_data[tmp] += 1
            last_loc = loc_t[0]

    rr_time = time.time()                  
    opt_data = {}
    for edge in noisy_data:
        junction = edge_to_junction[edge][0]
        # reverse_edge = None
        # for edge_1 in junction_dict[junction]['to']:
        #     if edge_to_junction[edge_1][0] == edge_to_junction[edge][1]:
        #         reverse_edge = edge_1
        #         break
        # if reverse_edge:
        #     reverse_edge_data = noisy_data[reverse_edge]
        # else:
        #     reverse_edge_data = 0
        n_edge = len(junction_dict[junction]['from'])
        sum = 0
        for edge_2 in junction_dict[junction]['from']:
            sum += noisy_data[edge_2]
        q = 1/(exp(epsilon)+n_edge-1)
        p = 1 - (n_edge-1)*q

        edge_opt_data = round((noisy_data[edge]-q*(sum))/(p-q))
        if n_edge == 1:
            edge_opt_data = round(edge_opt_data/(exp(epsilon)/(exp(epsilon)+1)))
        opt_data.update({edge:edge_opt_data})
    zero_data = []
    for edge in origin_data:
        if origin_data[edge] == 0:
            zero_data.append(edge)
    for edge in zero_data:
        del origin_data[edge]
        del noisy_data[edge]
        del opt_data[edge]
    error_opt = []
    for edge in origin_data:
        error_opt.append(origin_data[edge]-opt_data[edge])
    # print(origin_data)
    # print(noisy_data)
    # print(opt_data)
    error_origin = []
    xnt = 0
    for edge in origin_data:
        if origin_data[edge] == 0:
            xnt += 1
        error_origin.append(origin_data[edge]-noisy_data[edge])

    # print(len(origin_data))
    # print(np.var(error_origin))
    # print(xnt)
    # print(np.var(error_opt))
    org_mse = np.sqrt(np.var(error_origin))
    opt_mse = np.sqrt(np.var(error_opt))
    percent = (org_mse-opt_mse)/org_mse
    per_sum += percent
    opt_time = time.time()
    # for edge in ['23189459#0','23189459#1','23271841#0']:
    #     print(edge,origin_data[edge],noisy_data[edge],opt_data[edge])
    print('rr:%f,opt:%f'%((rr_time-start_time),(opt_time-start_time)))
data_sum = 0
for edge,data in origin_data.items():
    data_sum += data
print(data_sum/len(origin_data))
print(per_sum)
