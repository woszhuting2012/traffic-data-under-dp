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

def save_variable(v,filename):
    f=open(filename,'wb')         
    pickle.dump(v,f)              
    f.close()                     
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
from init import UNIT_LEN,EPSILON,NET_NAME,block_x,block_y,START_TIME,END_TIME,TIMESTEP

def opt_least_square(block_x,block_y,_t):
    net_tree = ET.parse(NET_NAME+".net.xml")
    net_root = net_tree.getroot()
    edge_list = net_root.findall("edge")
    all_junction_list = net_root.findall("junction")

    junction_list_partial = []
    for junction in all_junction_list:
        junction_x = float(junction.get("x"))
        junction_y = float(junction.get("y"))
        if junction.get('type')=='internal':
            continue
        if block_x<=junction_x<block_x+UNIT_LEN and block_y<=junction_y<block_y+UNIT_LEN:
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

    junction_link = {} 

    for junction in junction_dict.keys():
        junction_list = []
        for edge in junction_dict[junction]:
            for edge2 in edge_list_partial:
                if edge2.get('id')==edge:
                    if edge2.get('from') not in junction_list: junction_list.append(edge2.get('from'))
                    if edge2.get('to') not in junction_list: junction_list.append(edge2.get('to'))
        junction_link.update({junction: len(junction_list)})
    junction_list = []
    edge_list = []
    i = 0
    junction_x_dict = {}

    data_noisy = load_variable('noisy_data/noisy_%d.pkl'%_t)
    org_data = load_variable('origin_data/origin_%d.pkl'%_t)

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

    x_num = len(data_noisy)
    junction_num = len(junction_list)
    dimension = x_num + junction_num
    sp_row = []
    sp_culumn = []
    sp_value = []
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

    np.set_printoptions(threshold=np.inf)
    result_data = np.linalg.solve(A,b)
    org_error = []
    opt_error = []
    i=0
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
