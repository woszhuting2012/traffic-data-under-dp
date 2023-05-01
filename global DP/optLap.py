import ctypes
import csv
import re
import numpy as np
import xml.etree.ElementTree as ET
import time
import matplotlib.pyplot as plt
import sys
import pickle
from tqdm import tqdm

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
# test_edge_8 = _edge('8','D','F')
# test_edge_9 = _edge('9','D','G')
# test_edge_10 = _edge('10','D','H')
# test_edge_11 = _edge('11','H','D')
# test_edge_list = [test_edge_0,test_edge_1,test_edge_2,test_edge_3,test_edge_4,test_edge_5,test_edge_6,test_edge_7]

# test_junction_A = _junction('A',test_edge_list,501,501)
# test_junction_B = _junction('B',[test_edge_0,test_edge_7],501,501)
# test_junction_C = _junction('C',[test_edge_1,test_edge_2],501,501)
# test_junction_D = _junction('D',[test_edge_3,test_edge_4,test_edge_8,test_edge_9,test_edge_10,test_edge_11],501,501)
# test_junction_E = _junction('E',[test_edge_5,test_edge_6],501,501)
# test_junction_F = _junction('F',[test_edge_8],1,1)
# test_junction_G = _junction('G',[test_edge_9],1,1)
# test_junction_H = _junction('H',[test_edge_10,test_edge_11],1,1)
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
SEN = 1
from step0_0_init import UNIT_LEN,EPSILON,NET_NAME,block_x,block_y,START_TIME,END_TIME,TIMESTEP

def opt_least_square(block_x,block_y,_t):
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
        if block_x<=junction_x<block_x+UNIT_LEN and block_y<=junction_y<block_y+UNIT_LEN:
            junction_list_partial.append(junction.get("id"))
    
    #print('junction_num:%d'%len(junction_list_partial))
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
            junction_in[edge.get('id')] = edge.get('to')
            junction_out[edge.get('id')] = edge.get('from')

    junction_dict = {}
    for edge in edge_list_partial:
        if edge.get('from') not in junction_dict:
            junction_dict.update({edge.get('from'):[edge.get('id')]})
        else:
            junction_dict[edge.get('from')].append(edge.get('id'))
        
        if edge.get('to') not in junction_dict:
            junction_dict.update({edge.get('to'):[edge.get('id')]})
        else:
            junction_dict[edge.get('to')].append(edge.get('id'))
    save_variable(junction_dict,'junction.pkl')

    for junction in junction_dict.keys():
        junction_dict[junction] = set(junction_dict[junction])

    junction_link = {} # 每个路口连接的路口数量(包括自身)

    for junction in junction_dict.keys():
        junction_list = []
        for edge in junction_dict[junction]:
            for edge2 in edge_list_partial:
                if edge2.get('id')==edge:
                    if edge2.get('from') not in junction_list: junction_list.append(edge2.get('from'))
                    if edge2.get('to') not in junction_list: junction_list.append(edge2.get('to'))
        junction_link.update({junction: len(junction_list)})
    #print(data_processed)
    junction_list = []
    edge_list = []
    i = 0
    junction_x_dict = {}

    data_noisy = load_variable('noisy_data/noisy_%d.pkl'%_t)
    org_data = load_variable('origin_data/origin_%d.pkl'%_t)
    #epsilon = EPSILON/MAX_TRA
    # for edge in edge_id_list_partial:
    #     if edge not in data_noisy:
    #         data_noisy.update({edge:np.random.laplace(0,1/epsilon,1)[0]})
    #         org_data.update({edge:0})
    #data_noisy = {'0':5.25,'1':9.15,'2':7.21,'3':7.26,'4':6,'5':5.35,'6':6.65,'7':4.73}
    #记录路口和边包含的数据编号
    for edge,data in data_noisy.items():
        if edge in junction_in:
            if junction_link[junction_in[edge]]>2 and (junction_in[edge] in junction_list_partial):
                if junction_in[edge] not in junction_list :
                    junction_list.append(junction_in[edge])
                    junction_x_dict.update({junction_in[edge]: [i]})
                else:
                    junction_x_dict[junction_in[edge]].append(i)
        if edge in junction_out:
            if junction_link[junction_out[edge]]>2 and (junction_out[edge] in junction_list_partial):
                if junction_out[edge] not in junction_list:
                    junction_list.append(junction_out[edge])
                    junction_x_dict.update({junction_out[edge]: [-i]})
                else:
                    junction_x_dict[junction_out[edge]].append(-i)
        i += 1

    # junction_test = junction_list[0]
    # print(junction_test)
    # print(junction_x_dict[junction_test])
    # for x_test in junction_x_dict[junction_test]:
    #     if x_test>0: print(data_list[x_test])
    #     else: print(data_list[-x_test]) 
    # edge_test = edge_list[0]
    # print(edge_test)
    # print(edge_x_dict[edge_test])
    # for x_test in edge_x_dict[edge_test]:
    #     if x_test>0: print(data_list[x_test])
    #     else: print(data_list[-x_test])
    x_num = len(data_noisy)
    #print(junction_list)
    junction_num = len(junction_list)
    dimension = x_num + junction_num
    #print('x_num:%d, '%x_num+'junction_num:%d, '%junction_num)
    sp_row = [] #sp: 稀疏
    sp_culumn = []
    sp_value = []
    ##生成系数矩阵和常向量
    A = np.zeros((dimension,dimension))
    b = np.zeros((dimension,1))
    i = 0
    for edge,data in data_noisy.items():
        b[i][0] = data
        A[i][i] = 1
        sp_row.append(i)
        sp_culumn.append(i)
        sp_value.append(1)
        if edge in junction_in:
            if junction_in[edge] in junction_list:
                A[i][x_num+junction_list.index(junction_in[edge])] = 0.5
                sp_row.append(i)
                sp_culumn.append(x_num+junction_list.index(junction_in[edge]))
                sp_value.append(0.5)
        if edge in junction_out:
            if junction_out[edge] in junction_list:
                A[i][x_num+junction_list.index(junction_out[edge])] = -0.5
                sp_row.append(i)
                sp_culumn.append(x_num+junction_list.index(junction_out[edge]))
                sp_value.append(-0.5)
        i += 1

    for junction in junction_list:
        for x in junction_x_dict[junction]:
            if x < 0:
                A[i][-x] = -1
                sp_row.append(i)
                sp_culumn.append(-x)
                sp_value.append(-1)
            else:
                A[i][x] = 1
                sp_row.append(i)
                sp_culumn.append(x)
                sp_value.append(1)
        i += 1

    #np.savetxt("equation/matrix.txt", A, fmt="%01f", delimiter=" ")
    np.savetxt("equation/constant.txt", b, fmt="%f", delimiter=" ")
    filename = open('equation/row.txt', 'w')  
    for value in sp_row:  
        filename.write(str(value)+' ') 
    filename.close()  

    filename = open('equation/column.txt', 'w')  
    for value in sp_culumn:  
        filename.write(str(value)+' ') 
    filename.close()  

    filename = open('equation/value.txt', 'w')  
    for value in sp_value:  
        filename.write(str(value)+' ') 
    filename.close() 

    # lib = ctypes.cdll.LoadLibrary('./solve_cpp.so')
    # lib.solve_cpp(len(sp_row),dimension)
    np.set_printoptions(threshold=np.inf)
    result_data = np.linalg.solve(A,b)
    #print(result_data)
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
    clu_data = load_variable('clu.pkl')
    cnt = 0
    for edge,data in org_data.items():
        org_error.append(data-data_noisy[edge])
        opt_error.append(data-result_data[i])
        i += 1
        if data==0:
            cnt +=1
        if edge=='23189459#0'or edge=='23189459#1' or edge=='23271841#0':
            print(edge,result_data[i-1],data_noisy[edge],clu_data[edge])
    # print('zero:%d'%cnt)
    return org_error,opt_error


y1 = []
y2 = []
y3 = []

start = time.time()
org_sum_var = 0
opt_sum_var = 0
for t in tqdm(range(START_TIME,END_TIME,TIMESTEP)):
    [error_org,error_opt] = opt_least_square(block_x,block_y,t)
    org_sum_var += np.var(error_org)
    opt_sum_var += np.var(error_opt)
end = time.time()
#y1.append((error_var-opt_var)/error_var)
print("opt_var:%.3f"%(opt_sum_var/(END_TIME-START_TIME)*TIMESTEP),"org_var:%.3f"%(org_sum_var/(END_TIME-START_TIME)*TIMESTEP),"runtime:",end-start)
org_data = load_variable('origin_data/origin_%d.pkl'%450)
data_noisy = load_variable('noisy_data/noisy_%d.pkl'%450)
ptree_data = load_variable('ptree.pkl')
max_edge = []
junction_dict = load_variable('junction.pkl')
for junction,edge_list in junction_dict.items():
    i = 0
    for edge in edge_list:
        if abs(org_data[edge]-ptree_data[edge])<40 and org_data[edge]>20 and abs(data_noisy[edge]-org_data[edge])<40 and data_noisy[edge]>0:
            i += 1
    if i==len(edge_list)-1 and len(edge_list)>2:
        print(edge_list)
        for edge in edge_list:
            print(edge,org_data[edge],ptree_data[edge],data_noisy[edge])

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