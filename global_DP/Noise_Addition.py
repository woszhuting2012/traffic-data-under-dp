import sys
from global_DP.init import RETARDTIME,load_variable,save_variable,PTNode,PTree,START_TIME,NET_NAME,EPSILON,TIMESTEP,MAX_TRA
from tqdm import tqdm
import numpy as np
import copy
import time
import random
import xml.etree.ElementTree as ET
def noisy_generation(tree,epsilon):
    random_number = np.random.laplace(0,1/epsilon,1)[0]
    tree.cnt += random_number
    for child in tree.children:
        noisy_generation(child,epsilon)

def ptree_deep(tree):
    deep = 0
    if tree:
        children_deep =[]
        for child in tree.children:
            children_deep.append(ptree_deep(child))
        if children_deep:
            deep = 1 + max(children_deep)
        else:
            deep = 1
    return deep

def node_list_mean(_node_list):
    sum = 0
    for node in _node_list:
        sum += node.cnt
    return sum/len(_node_list)

def isotone(node_list):
    UPPER_BOUND = 10000
    LOWER_BOUND = -10000
    isotone_list = []
    for m in range(len(node_list)):
        max = LOWER_BOUND
        for j in range(m,len(node_list)):
            min = UPPER_BOUND
            for i in range(j+1):
                if (node_list_mean(node_list[i:j+1])<min):
                    min = node_list_mean(node_list[i:j+1])  
            if min > max: max = min
        
        isotone_list.append(max)
        
    for i in range(len(node_list)):
        node_list[i].cnt = isotone_list[i]
    return node_list

def tree_isotone(tree):
    stack = []
    stack.append(tree)
    node_list = []
    while stack:
        current_node = stack.pop()
        if node_list:
            while current_node not in (node_list[-1].children):
                node_list.pop()
        node_list.append(current_node)
        isotone(node_list)
        stack = stack + current_node.children
        if not current_node.children:
            node_list.pop()

def opt_2(tree):
    if tree.loc_t == ('loc_root','time_root'):
        for child in tree.children:
            for cchild in child.children:
                opt_2(cchild)
    else:
        if tree.children:
            sum_sibling = 0
            for child in tree.children:
                sum_sibling += child.cnt
            for child in tree.children:
                if tree.cnt < sum_sibling:
                    child.cnt += (tree.cnt - sum_sibling)/len(tree.children)
        for child in tree.children:
            opt_2(child)

def ptree_count(_T,_state,edge_id_list_partial,tree_edge_list,rest_random):
    data = {}
    stack = []
    i = 0
    for edge in edge_id_list_partial:
        data[edge] = 0
        if _state != 1:
            if edge not in tree_edge_list:
                data[edge] = rest_random[i]
                i += 1

    stack.append(_T.tree)
    while stack:
        current_node = stack.pop()
        stack = stack + current_node.children
        if current_node.loc_t != ('loc_root','time_root'):
            if current_node:
                data[current_node.loc_t[0]] += current_node.cnt

    if _state == 2:
        re_dict = load_variable('clu_re_dict.pkl')
        for edge in re_dict:
            avg_data = data[edge]/len(re_dict[edge])
            for edge2 in re_dict[edge]:
                data[edge2] = avg_data
    return data

def var_cal(processed_file,raw_file):
    raw_data = load_variable(raw_file)
    processed_data = load_variable(processed_file)
    error_list = []
    for edge,cnt in raw_data.items():
        error_list.append(cnt-processed_data[edge])

    return error_list

def random_del(L,org_l,n):
    to_delete = set(random.sample(range(len(L)), n))
    del_value = []
    for index in  to_delete:
        del_value.append(L[index])
    for val in del_value:
        org_l.remove(val)
    return org_l

start_runtime = time.time()
org_sum_var = 0
opt_sum_var = 0
max_tra = 0
edge_list_partial = []
trajectory_dict = load_variable('global_DP/trajectory_'+NET_NAME+'.pkl')
for vehicle,trajectory in trajectory_dict.items():
    edge_passed_list = []
    for current_loc_t in trajectory:
        if START_TIME<=current_loc_t[1]<START_TIME+TIMESTEP:
            if current_loc_t[0] not in edge_list_partial: edge_list_partial.append(current_loc_t[0])
            if current_loc_t[0] not in edge_passed_list:
                edge_passed_list.append(current_loc_t)
    if len(edge_passed_list) > max_tra: max_tra = len(edge_passed_list)
T = PTree()
tree_edge_list = []
trajectory_dict = load_variable('global_DP/trajectory_'+NET_NAME+'.pkl')
for vehicle,trajectory in tqdm(trajectory_dict.items()):
    current_PTNode = T.tree
    _state = 0
    for current_loc_t in trajectory:
        if START_TIME<=current_loc_t[1]<START_TIME+TIMESTEP:
            if _state !=2:
                _state = 0
                for child in current_PTNode.children:
                    if (child.loc_t[0]==current_loc_t[0]) and (child.loc_t[1]//RETARDTIME==current_loc_t[1]//RETARDTIME):
                        child.cnt += 1
                        current_PTNode = child
                        _state = 1
                if _state != 1: _state = 2    
            if _state==2:
                if (current_PTNode.loc_t[0]!=current_loc_t[0]):
                    new_node = PTNode(current_loc_t)
                    if current_loc_t[0] not in tree_edge_list:
                        tree_edge_list.append(current_loc_t[0])
                    current_PTNode.children.append(new_node)
                    current_PTNode = new_node

origin_T = copy.deepcopy(T)
max_tra = MAX_TRA
epsilon = EPSILON/max_tra

for child in tqdm(T.tree.children):
    noisy_generation(child,epsilon)

for child in tqdm(T.tree.children):
    tree_isotone(child)
opt_2(T.tree)
noisy_T = copy.deepcopy(T)

net_tree = ET.parse("Datasets/"+NET_NAME+".net.xml")
net_root = net_tree.getroot()
edge_list = net_root.findall("edge")
edge_list_all = []
for edge in edge_list:
    if edge.get('function')=="internal":
        continue
    edge_list_all.append(edge.get('id'))

n = len(edge_list_all)-len(tree_edge_list)
rest_random = np.random.laplace(0,max_tra/EPSILON,n)
result = ptree_count(origin_T,1,edge_list_all,tree_edge_list,rest_random)
save_variable(result,'global_DP/origin_%s_%d.pkl'%(NET_NAME,START_TIME))
result = ptree_count(noisy_T,0,edge_list_all,tree_edge_list,rest_random)

save_variable(result,'global_DP/noisy_%s_%d.pkl'%(NET_NAME,START_TIME))

