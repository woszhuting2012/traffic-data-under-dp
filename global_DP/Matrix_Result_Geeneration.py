import numpy as np
import xml.etree.ElementTree as ET
import time
import matplotlib.pyplot as plt
from tqdm import tqdm

from global_DP.init import NET_NAME,START_TIME,save_variable,load_variable
class eq_j:
    def __init__(self,id) -> None:
        self.id = id
        self.in_list = set()
        self.out_list = set()
        self.adj_j = set()
        self.idx = -1
    
    def __eq__(self, __value: object) -> bool:
        return self.id == __value.id

def opt_least_square():
    net_tree = ET.parse("Datasets/"+NET_NAME+".net.xml")
    net_root = net_tree.getroot()
    edge_list = net_root.findall("edge")
    junction_dict = {}
    edge_id_list_partial = []
    edge_list_partial = []
    for edge in edge_list:
        if edge.get('function')=="internal":
            continue
        edge_id_list_partial.append(edge.get('id'))
        edge_list_partial.append(edge)
        if edge.get('from') not in junction_dict:
            from_j = eq_j(edge.get('from'))
            junction_dict[edge.get('from')] = from_j
        junction_dict[edge.get('from')].out_list.add(edge.get('id'))
        junction_dict[edge.get('from')].adj_j.add(edge.get('to'))
        
        if edge.get('to') not in junction_dict:
            to_j   = eq_j(edge.get('to'))
            junction_dict[edge.get('to')] = to_j
        junction_dict[edge.get('to')].in_list.add(edge.get('id'))
        junction_dict[edge.get('to')].adj_j.add(edge.get('from'))
 
    data_noisy = load_variable('global_DP/ptree_%s_%d.pkl'%(NET_NAME,START_TIME))
    org_data = load_variable('global_DP/origin_%s_%d.pkl'%(NET_NAME,START_TIME))
    k = 0
    for j in junction_dict.values():
        if len(j.adj_j)>1:
            j.idx = k
            k +=1
    A = np.zeros((k,k))
    b = np.zeros((k,1))
    for j in junction_dict.values():
        if j.idx == -1:
            continue
        sum_in = 0
        sum_out = 0
        for edge in j.in_list:
            sum_in += data_noisy[edge]
        for edge in j.out_list:
            sum_out += data_noisy[edge]
        b[j.idx][0] = sum_in - sum_out
        A[j.idx][j.idx] = (len(j.in_list | j.out_list))/2
        for j_adj_id in j.adj_j:
            j_adj = junction_dict[j_adj_id]
            if j_adj.idx != -1:
                A[j.idx][j_adj.idx] = -(len((j.in_list & j_adj.out_list)|(j.out_list & j_adj.in_list)))/2
    lambda_list = np.linalg.solve(A,b)

    opt_data = {}
    for edge in edge_list_partial:
        data = data_noisy[edge.get('id')]
        from_j = junction_dict[edge.get('from')]
        to_j = junction_dict[edge.get('to')]
        if len(from_j.adj_j)>1:
            data = data + lambda_list[from_j.idx][0]/2
        if len(to_j.adj_j)>1:
            data = data - lambda_list[to_j.idx][0]/2
        opt_data[edge.get('id')] = data

    noisy_error = []
    opt_error = []
    for edge,data in data_noisy.items():
        noisy_error.append(data-org_data[edge])
        opt_error.append(opt_data[edge]-org_data[edge])
    save_variable(opt_data,'global_DP/opt_%s_%d.pkl'%(NET_NAME,START_TIME))
    return noisy_error,opt_error

start = time.time()

[error_noisy,error_opt] = opt_least_square()
 
end = time.time()

print("opt_var:%.3f"%error_opt,"noisy_var:%.3f"%error_noisy,"runtime:",end-start)
