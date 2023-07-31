RETARDTIME = 100
EPSILON = 1
START_TIME = 450
END_TIME = 900
block_x = 500
block_y = 500
UNIT_LEN = 2500
NET_NAME = 'bolognaringway'
TRA_NUM = 0
TIMESTEP = 450
MAX_TRA = 7
import pickle

class PTNode:
    def __init__(self, _loc_t, _cnt=1):
        self.loc_t = _loc_t
        self.cnt = _cnt
        self.children = []
    
    def __str__(self):
        return 'loc_t: %s_%d ' % self.loc_t + ' cnt: %d' % self.cnt
    
    def __eq__(self, other):
        result = False
        if isinstance(other, PTNode):
            if self.loc_t[0] == other.loc_t[0]:
                if self.loc_t[1]//RETARDTIME == other.loc_t[1]//RETARDTIME:
                    if self.cnt == other.cnt:
                        result = True
        return result

class PTree:
    def __init__(self, tree_root=('loc_root','time_root'), tree_root_cnt=-1):
        self.count = 0
        self.tree = PTNode(tree_root,tree_root_cnt)
        self.if_node_exist = False
        self.search_result = None
        self.search_result_children = []

    def add(self, node, parent=None):
        if parent == None:
            # 如果parent为None，则默认其父节点为root节点
            root_children = self.tree.children
            root_children.append(node)
            self.tree.children = root_children
        else:
            self.add_recursion(parent, node, self.tree)

    def to_graph_recursion(self, tree, G):
        '''
        将节点加入到图中
        '''
        G.add_node((tree.loc_t,tree.cnt))
        for child in tree.children:
            G.add_nodes_from([(tree.loc_t,tree.cnt), (child.loc_t,child.cnt)])
            G.add_edge((tree.loc_t,tree.cnt), (child.loc_t,child.cnt))
            self.to_graph_recursion(child, G)

    def add_recursion(self, parent, node, tree):
        '''
        增加节点时使用的递归函数
        '''
        if parent == tree:
            tree.children.append(node)
            return 1

        for child in tree.children:
            if child == parent:
                children_list = child.children
                children_list.append(node)
                child.children = children_list
                break
            else:
                self.add_recursion(parent, node, child)

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
