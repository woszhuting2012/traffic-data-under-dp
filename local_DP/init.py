import pickle
START_TIME =4800
TIMESTEP = 100
epsilon = 1

NET_NAME = 'bolognaringway'

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