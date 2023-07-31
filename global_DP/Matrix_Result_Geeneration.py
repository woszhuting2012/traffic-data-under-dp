import numpy as np
import xml.etree.ElementTree as ET
import time
import matplotlib.pyplot as plt
import sys
import pickle
from tqdm import tqdm
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import spsolve

class eq_j:
    def __init__(self,id) -> None:
        self.id = id
        self.in_list = set()
        self.out_list = set()
        self.adj_j = set()
        self.idx = -1
    
    def __eq__(self, __value: object) -> bool:
        return self.id == __value.id
        
#测试
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
#     def __init__(self,_id,_edge_list) -> None:
#         self.id = _id
#         self.edge_list = _edge_list
  
#     def get(self,attribute):
#         if attribute=='id': return self.id


# test_edge_0 = _edge('0','B','A')
# test_edge_1 = _edge('1','A','C')
# test_edge_2 = _edge('2','C','A')
# test_edge_3 = _edge('3','A','D')
# test_edge_4 = _edge('4','D','A')
# test_edge_5 = _edge('5','A','E')
# test_edge_6 = _edge('6','E','A')
# test_edge_7 = _edge('7','A','B')
# test_edge_8 = _edge('8','D','F')
# test_edge_9 = _edge('9','D','G')
# test_edge_10 = _edge('10','D','H')
# test_edge_11 = _edge('11','H','D')
# test_edge_12 = _edge('12','F','D')
# test_edge_13 = _edge('13','G','D')
# test_edge_list = [test_edge_0,test_edge_1,test_edge_2,test_edge_3,test_edge_4,test_edge_5,test_edge_6,test_edge_7,test_edge_8,test_edge_9,test_edge_10,test_edge_11,test_edge_12,test_edge_13]

# test_junction_A = _junction('A',test_edge_list)
# test_junction_B = _junction('B',[test_edge_0,test_edge_7])
# test_junction_C = _junction('C',[test_edge_1,test_edge_2])
# test_junction_D = _junction('D',[test_edge_3,test_edge_4,test_edge_8,test_edge_9,test_edge_10,test_edge_11,test_edge_12,test_edge_13])
# test_junction_E = _junction('E',[test_edge_5,test_edge_6])
# test_junction_F = _junction('F',[test_edge_8])
# test_junction_G = _junction('G',[test_edge_9])
# test_junction_H = _junction('H',[test_edge_10,test_edge_11])
# test_junction_list = [test_junction_A,test_junction_B,test_junction_C,test_junction_D,test_junction_E,test_junction_F,test_junction_G,test_junction_H]

# test_network = _network(test_edge_list,test_junction_list)

def save_variable(v,filename):
    f=open(filename,'wb')          #打开或创建名叫filename的文档。
    pickle.dump(v,f)               #在文件filename中写入v
    f.close()                      #关闭文件，释放内存。
    return filename

def load_variable(filename):
    try:
        f=open(filename,'rb')
        r=pickle.load(f)
        f.close()
        return r
    except EOFError:
        return ""
from step0_0_init import EPSILON,NET_NAME,START_TIME,TIMESTEP

def opt_least_square(_ii):
    net_tree = ET.parse(NET_NAME+".net.xml")
    net_root = net_tree.getroot()
    edge_list = net_root.findall("edge")
    #all_junction_list = net_root.findall("junction")
    #edge_list = test_edge_list
    # all_junction_list = test_junction_list

    junction_dict = {}
    # for junction in all_junction_list:
    #     if junction.get('type')=='internal':
    #         continue
    #     cur_j = eq_j(junction.get('id'))
    #     junction_list_partial.append(cur_j)
    
    #print('junction_num:%d'%len(junction_list_partial))
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
    
    save_variable(junction_dict,'junction.pkl')
 
    #data_noisy = load_variable('noisy_data/noisy_%s_%d.pkl'%(NET_NAME,START_TIME))
    data_noisy = load_variable('ptree_data/ptree_%s_%d_%d.pkl'%(NET_NAME,START_TIME,_ii))
    org_data = load_variable('origin_data/origin_%s_%d.pkl'%(NET_NAME,START_TIME))
    # data_noisy = load_variable('noisy_data/noisy_%s_%d.pkl'%('test',START_TIME))
    # org_data = load_variable('origin_data/origin_%s_%d.pkl'%('test',START_TIME))
    k = 0
    for j in junction_dict.values():
        if len(j.adj_j)>1:
            j.idx = k
            k +=1
    A = np.zeros((k,k))
    b = np.zeros((k,1))
    for j in junction_dict.values():
        #print(j.id,j.idx,j.in_list,j.out_list,j.adj_j)
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
        
    #print(opt_data)

    org_error = []
    opt_error = []
    # with open('equation/result.txt',encoding='utf-8') as file:
    #     result_data=file.readlines()
    #     for data in result_data:
    #         data = data.strip('\n')

    #org_data = {'0':4,'1':10,'2':5,'3':3,'4':6,'5':7,'6':7,'7':2}
    i=0
    # print(len(data_noisy))
    # print(len(org_data))
    #clu_data = load_variable('clu.pkl')
    for edge,data in data_noisy.items():
        org_error.append(data-org_data[edge])
        opt_error.append(opt_data[edge]-org_data[edge])
    # print('zero:%d'%cnt)
    save_variable(opt_data,'opt_data/opt_%s_%d_%d.pkl'%(NET_NAME,START_TIME,_ii))
    return org_error,opt_error

start = time.time()
org_sum_var = 0
opt_sum_var = 0
for ii in tqdm(range(1)):
    [error_org,error_opt] = opt_least_square(ii)
    org_sum_var += np.var(error_org)
    opt_sum_var += np.var(error_opt)


end = time.time()
#y1.append((error_var-opt_var)/error_var)
print("opt_var:%.3f"%opt_sum_var,"org_var:%.3f"%org_sum_var,"runtime:",end-start)
# org_data = load_variable('origin_data/origin_%s_%d.pkl'%(NET_NAME,START_TIME))
# data_noisy = load_variable('noisy_data/noisy_%s_%d.pkl'%(NET_NAME,START_TIME))
# ptree_data = load_variable('ptree_data/ptree_%s_%d.pkl'%(NET_NAME,START_TIME))
# max_edge = []
# junction_dict = load_variable('junction.pkl')
# for junction,edge_list in junction_dict.items():
#     i = 0
#     for edge in edge_list:
#         if abs(org_data[edge]-ptree_data[edge])<40 and org_data[edge]>20 and abs(data_noisy[edge]-org_data[edge])<40 and data_noisy[edge]>0:
#             i += 1
#     if i==len(edge_list)-1 and len(edge_list)>2:
#         print(edge_list)
#         for edge in edge_list:
#             print(edge,org_data[edge],ptree_data[edge],data_noisy[edge])

#for edge in max_edge:
    #print(edge,org_data[edge],data_noisy[edge])
# for edge in ['27032657#0','23296590#0','-27032657#0']:
#     print(edge,org_data[edge],data_noisy[edge],ptree_data[edge])
#plt.plot(x,y1,label='opt_least_square')

#plt.plot(x,y2,label='noisy_variance',linestyle='--')
#plt.show()

# test_result = opt_least_square(Time,Freq,1)

# test_data = [4,5,3,6,4,5,3,6]

# test_error = []
# for i in range(8):
#     test_error.append(test_data[i]-test_result[i])

# print(test_error)
# print(np.var(test_error))