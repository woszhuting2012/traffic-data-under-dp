from sklearn.cluster import KMeans
import xml.etree.ElementTree as ET
import sys
from step0_0_init import save_variable,load_variable,block_x,block_y,UNIT_LEN,START_TIME,END_TIME,NET_NAME,TRA_NUM,RETARDTIME,PTNode,PTree,EPSILON,TIMESTEP,MAX_TRA
import numpy as np
from tqdm import tqdm
import copy
import random
GROUP = 100
from scipy.spatial import distance
import time
def replace_edge(x,y,edge_to_loc):
    first = 1
    min_edge = None
    for edge,loc in edge_to_loc.items():
        d = distance.euclidean((x,y),loc)        
        if first:
            min_d = d
            min_edge = edge
            first = 0
        else:
            if d<min_d:
                min_d = d
                min_edge = edge
    return min_edge

def noisy_generation(tree,epsilon):
    random_number = np.random.laplace(0,1/epsilon,1)[0]
    tree.cnt += random_number
    #if tree.cnt<0: tree.cnt=0
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
        #print(len(node_list))
        if node_list:
            while current_node not in (node_list[-1].children):
                node_list.pop()
        #print(len(node_list))
        node_list.append(current_node)
        #print(len(node_list))
        isotone(node_list)
        #print(len(stack))
        stack = stack + current_node.children
        if not current_node.children:
            node_list.pop()
        #print(len(node_list))

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

def ptree_count(_T,_state,edge_id_list_partial,tree_edge_list,rest_random,_t):
    #normal_edge_IDlist = ['L1','L2','L3','L4']
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
                if _t <= current_node.loc_t[1] < _t+TIMESTEP:
                    data[current_node.loc_t[0]] += current_node.cnt

    if _state == 2:
        re_dict = load_variable('clu_re_dict.pkl')
        for edge in re_dict:
            avg_data = data[edge]/len(re_dict[edge])
            for edge2 in re_dict[edge]:
                data[edge2] = avg_data
    #print(data)
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

start_time = time.time()
net_tree = ET.parse(NET_NAME+".net.xml")
net_root = net_tree.getroot()
edge_list = net_root.findall("edge")
junction_list_partial = []
junction_dict = {}
junction_loc = {}
edge_to_loc = {}
all_junction_list = net_root.findall("junction")
for junction in all_junction_list:
    junction_x = float(junction.get("x"))
    junction_y = float(junction.get("y"))
    junction_loc[junction.get('id')] = (junction_x,junction_y)
    if block_x<=junction_x<block_x+UNIT_LEN and block_y<=junction_y<block_y+UNIT_LEN:
        junction_list_partial.append(junction.get("id"))
edge_id_list_partial = []
loc_list = []
for edge in edge_list:
    if edge.get('function')=="internal":
        continue
    if edge.get('from') in junction_list_partial or edge.get('to') in junction_list_partial:
        edge_id_list_partial.append(edge.get('id'))
        edge_to_loc[edge.get('id')] = junction_loc[edge.get('from')]
        loc_list.append(junction_loc[edge.get('from')])
#print('junction:%d'%len(junction_list_partial))
trajectory_dict = load_variable('trajectory_'+NET_NAME+'_%d.pkl'%TRA_NUM)
model = KMeans(n_clusters=GROUP,random_state=0).fit(loc_list)
clu_center = model.cluster_centers_
# min_x = 20000
# max_x = 0
# min_y = 20000
# max_y = 0
# for loc in loc_list:
#     if loc[0]>max_x: max_x = loc[0]
#     if loc[0]<min_x: min_x = loc[0]
#     if loc[1]>max_y: max_y = loc[1]
#     if loc[1]<min_y: min_y = loc[1]

# print(min_x,max_x,min_y,max_y)
opt_sum_var = 0
for t in tqdm(range(START_TIME,END_TIME,TIMESTEP)):
    for vehicle,trajectory in trajectory_dict.items():
        edge_passed_list = []
        for current_loc_t in trajectory:
            if t <= current_loc_t[1] < t+TIMESTEP:
                if current_loc_t[0] not in edge_id_list_partial:
                    continue
                if current_loc_t[0] not in edge_passed_list:
                    edge_passed_list.append(current_loc_t)
        if len(edge_passed_list)>=MAX_TRA:
            trajectory_dict[vehicle] = random_del(edge_passed_list,trajectory,len(edge_passed_list)-MAX_TRA)
    edge_list_test = []
    re_dict = {}
    for vehicle,trajectory in trajectory_dict.items():
        for i in range(len(trajectory)):
            if t <= trajectory[i][1] < t + TIMESTEP:
                if trajectory[i][0] not in edge_id_list_partial:
                    continue
                (x,y) = clu_center[model.labels_[loc_list.index(edge_to_loc[trajectory[i][0]])]]
                step = trajectory[i][1]
                cur_loc = trajectory[i][0]
                if cur_loc not in edge_list_test:
                    edge_list_test.append(cur_loc)
                re_loc = replace_edge(x,y,edge_to_loc)
                if re_loc not in re_dict:
                    re_dict[re_loc] = [cur_loc]
                else:
                    if cur_loc not in re_dict[re_loc]:
                        re_dict[re_loc].append(cur_loc)
                trajectory[i] = (re_loc,step)
    save_variable(trajectory_dict,'cluster_data/tra_clu.pkl')
    save_variable(re_dict,'clu_re_dict.pkl')

    T = PTree()
    tree_edge_list = []
    for vehicle,trajectory in trajectory_dict.items():
        current_PTNode = T.tree
        _state = 0
        '''
        state 0: 开始搜索
        state 1: 找到相同轨迹
        state 2: 未找到相同轨迹
        '''
        for current_loc_t in trajectory:
            if t < current_loc_t[1] < t + TIMESTEP:
                if current_loc_t[0] not in edge_id_list_partial:
                    continue
                # print(current_loc_t)
                # print(type(current_loc_t[1]))
                # sys.exit(0)
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

    #save_variable(tree_edge_list,'tree_edge_list.pkl')

    origin_T = copy.deepcopy(T)
    epsilon = EPSILON/MAX_TRA

    for child in T.tree.children:
        noisy_generation(child,epsilon)
    noisy_T = copy.deepcopy(T)
    #save_variable(T,save_file+'_test1.pkl')

    #T = load_variable('ptree_noisy_test1.pkl')
    #T.show_tree()
    for child in T.tree.children:
        tree_isotone(child)
    #T.show_tree()
    opt_2(T.tree)
    ptree_T = copy.deepcopy(T)
    #save_variable(T,filename + '_opt_2_test1.pkl')

    #tree_edge_list = load_variable('tree_edge_list.pkl')
    #edge_id_list_partial = load_variable('edge_id_partial.pkl')
    #max_tra = load_variable('max_tra.pkl')
    #print(len(edge_id_list_partial))
    n = len(edge_id_list_partial)-len(tree_edge_list)
    #print('random:%d'%n)
    rest_random = np.random.laplace(0,MAX_TRA/EPSILON,n)
    result = ptree_count(ptree_T,2,edge_id_list_partial,tree_edge_list,rest_random,t)
    save_variable(result,'clu.pkl')
    error_opt = var_cal('clu.pkl','origin_data/origin_%d.pkl'%t)
    mse_opt = np.var(error_opt)
    opt_sum_var += mse_opt
    

end_time = time.time()
run_time = end_time - start_time
print('clu_time: %.1f'%run_time,'clu_var: %.1f'%(opt_sum_var/(END_TIME-START_TIME)*TIMESTEP))