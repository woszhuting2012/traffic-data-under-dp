import pickle
START_TIME = 450
END_TIME = 900
epsilon = 1
MAX_X = 5000 #4200
MAX_Y = 5000 #3000
START_X = 0
START_Y = 0
UNIT_LEN = 5000
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