import pickle
START_TIME = 450
END_TIME = 900
epsilon = 1
MAX_X = 5000 #4200
MAX_Y = 5000 #3000
START_X = 0
START_Y = 0
UNIT_LEN = 5000
NET_NAME = 'pasubio'

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