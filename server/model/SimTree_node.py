#-------------------------------------------------------------------------------
# Name:        SimTree
# Purpose:     To management SimVM
#
# Author:      Bruce
#
# Created:     28-03-2020
# Copyright:   (c) Bruce 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys
sys.path.append("..")
from treelib import Node, Tree
import pickle, json, copy, time, random
import MyNode_new
from unmannedshipv1.server import opt_db


def store(data, filename):
    # 序列化，写到本地磁盘文件
    with open(filename,'wb') as f:
        pickle.dump(data, f)

def grab(filename):
    # 反序列化，从本地文件读出原有的对象
    with open(filename,'rb') as f:
        return pickle.load(f)

def Tree_to_eChartsJSON(tree):
    #Transform the whole tree into an eCharts_JSON.
    def to_dict(tree, nid):
        ntag = tree[nid].tag
        tree_dict = {'name': ntag, 'value': int(nid), "children": []}
        #if tree[nid].expanded:
        for elem in tree.children(nid):
            tree_dict["children"].append(to_dict(tree, elem.identifier))
        if len(tree_dict["children"]) == 0:
            tree_dict.pop('children', None)
        return tree_dict
    eChartsDict = {'data': [to_dict(tree, tree.root)]}
    return json.dumps(eChartsDict)
    pass

def write2db(SimTreeID, sTree, VMpool):
    JSONTree = Tree_to_eChartsJSON(sTree)
    opt_db.insert_into_simtree(SimTreeID, JSONTree)
    print('已写入sim tree.')
    for item in VMpool:
        opt_db.insert_into_simvm(item["VMID"], json.dumps(item))
    print("已经将仿真树和其中的结点数据写入数据库.")
    pass

def write2dynTree(sTree):
    opt_db.del_dynTree()
    allNodes = sTree.all_nodes()
    for node in allNodes:
        rootId = node.tag
        children = sTree.children(rootId)
        if (children is not None) and len(children) > 0:
            childrenArr = []
            for node in children:
                leafDic = {'name': node.tag, 'value': int(node.tag)}
                childrenArr.append(leafDic)
            childDic = {'data':[{'name': rootId, 'value': int(rootId), "children": childrenArr}]}
            # print(childDic)
            opt_db.insert_into_dynTree(rootId,json.dumps(childDic))
    pass

def SimTree():

    SimTreeID = "10" + time.strftime("%y%m%d%H%M%S") + str(random.randint(1000, 9999))
    tree = Tree()
    VMpool = []
    GenVMID = time.strftime("%y%m%d%H%M%S") + str(random.randint(1000, 9999))
    # 在多船避碰中，如果要加步长控制，用VM = MyNode_new.SimVM(GenVMID, timeratio=10)
    # VM = MyNode.SimVM(GenVMID, timeratio=10)   #没加步长控制的树
    VM = MyNode_new.SimVM(GenVMID, timeratio=30)    #加上步长控制的树，需要几艘船，就留几艘

    VM.addShip(ShipID='5', VM=VM, Tick=0, Lon=123.09095589770743, Lat=30.994319395177705, Speed=8.084746870262807, Heading=273.81293419269144)
    VM.addShip(ShipID='6', VM=VM, Tick=0, Lon=122.99105741719572, Lat=30.950377188775665, Speed=5.162584360523892, Heading=6.993414728662661) 

    # VM.addShip(ShipID='5', VM=VM, Tick=0, Lon=122.99570754747069, Lat=30.923820237834015, Speed=7.825531334365747, Heading=1.6147930323435356)
    # VM.addShip(ShipID='6', VM=VM, Tick=0, Lon=122.94884692674772, Lat=31.03068336199321, Speed=5.419348724091339, Heading=124.60307208452502) 
    # VM.addShip(ShipID='7', VM=VM, Tick=0, Lon=123.07436853351133, Lat=31.009193414528056, Speed=6.432755591138994, Heading=261.4427234937846) 

    # VM.addShip(ShipID='1', VM=VM, Tick=0, Lon=123, Lat=30.916667, Speed=18, Heading=0)
    # VM.addShip(ShipID='2', VM=VM, Tick=0, Lon=123.074551, Lat=31.0535, Speed=18, Heading=230)
    # VM.addShip(ShipID='3', VM=VM, Tick=0, Lon=123.074940, Lat=30.963, Speed=16, Heading=300)
    # VM.addShip(ShipID='4', VM=VM, Tick=0, Lon=122.950364, Lat=31.0425, Speed=13, Heading=135)

<<<<<<< HEAD
    # VM.addShip(ShipID='5', VM=VM, Tick=0, Lon=122.78251262605687, Lat=31.030339834029483, Speed=9.960740667693244, Heading=99.35475841161396)
    # VM.addShip(ShipID='6', VM=VM, Tick=0, Lon=122.91593423176747, Lat=30.903070437389857, Speed=6.567974823839184, Heading=36.315680123326075)
    # VM.addShip(ShipID='7', VM=VM, Tick=0, Lon=123.16479312101988, Lat=31.10671033810767, Speed=9.340500934800755, Heading=232.93268147711885)
    # VM.addShip(ShipID='8', VM=VM, Tick=0, Lon=122.88336673620816, Lat=31.054371217595232, Speed=6.000810507258333, Heading=117.837424187753)


    # VM.addShip(ShipID='5', VM=VM, Tick=0, Lon=122.89673777456287, Lat=30.832089608976606, Speed=8.848345027598416, Heading=27.713393008874263)
    # VM.addShip(ShipID='6', VM=VM, Tick=0, Lon=123.15163160556298, Lat=30.89612461371427, Speed=7.966307883378466, Heading=308.4994185800324)       
    # VM.addShip(ShipID='7', VM=VM, Tick=0, Lon=123.20101644832525, Lat=31.071256357258765, Speed=8.796110863864833, Heading=246.83059677710295)     
    # VM.addShip(ShipID='8', VM=VM, Tick=0, Lon=123.0018758459291, Lat=30.797875974749463, Speed=9.47776867519516, Heading=359.8496008933768)
    
    # VM.addShip(ShipID='5', VM=VM, Tick=0, Lon=122.27635620986185, Lat=30.91045053935861, Speed=6.617090188738684, Heading=82.02363676507208)
    # VM.addShip(ShipID='6', VM=VM, Tick=0, Lon=122.64482997740878, Lat=30.373875824263077, Speed=7.329999359404412, Heading=26.01443700424323)
    # VM.addShip(ShipID='7', VM=VM, Tick=0, Lon=122.5290069652373, Lat=30.35791175566669, Speed=8.001724620154114, Heading=32.15868495957398)
    # VM.addShip(ShipID='8', VM=VM, Tick=0, Lon=122.44092367295826, Lat=30.7089463984612, Speed=5.949657769093346, Heading=58.84954022565689)
    

    # VM.addShip(ShipID='5', VM=VM, Tick=0, Lon=122.91677022057087, Lat=30.89483647405028, Speed=14.062328229558924, Heading=35.07735406133116)
    # VM.addShip(ShipID='6', VM=VM, Tick=0, Lon=122.90908229496722, Lat=31.10101207102319, Speed=14.084472678091256, Heading=143.24041522144256)
    # VM.addShip(ShipID='7', VM=VM, Tick=0, Lon=123.074834816289, Lat=31.113526888662822, Speed=14.037255603505326, Heading=209.02726543072043)
    # VM.addShip(ShipID='8', VM=VM, Tick=0, Lon=122.87828079796927, Lat=30.984319408560985, Speed=11.466001116357138, Heading=81.44145312806675)
    
    # VM.addShip(ShipID='5', VM=VM, Tick=0, Lon=123.27195999687933, Lat=31.06204246263263, Speed=14.668622641808101, Heading=255.59313117551187)
    # VM.addShip(ShipID='6', VM=VM, Tick=0, Lon=123.05392843794088, Lat=31.246428750551765, Speed=14.980444046622505, Heading=190.90957606445)
    # VM.addShip(ShipID='7', VM=VM, Tick=0, Lon=123.00790597335934, Lat=30.768143958307327, Speed=13.70768986979356, Heading=358.37417829322374)
    # VM.addShip(ShipID='8', VM=VM, Tick=0, Lon=123.18911675514303, Lat=31.12249738025927, Speed=12.105957381682785, Heading=233.1762337921036)


=======
    VM.addShip(ShipID='5', VM=VM, Tick=0, Lon=123.12024061852294, Lat=31.081119277424886, Speed=7.39537055423542, Heading=232.87910063539232)
    VM.addShip(ShipID='6', VM=VM, Tick=0, Lon=123.11281626654447, Lat=30.99325453641464, Speed=5.477632791913566, Heading=274.64862254731236)
    VM.addShip(ShipID='7', VM=VM, Tick=0, Lon=122.82079841948959, Lat=30.95271396294126, Speed=9.012856459608294, Heading=72.07561280196485)    
    
    
>>>>>>> 7de171b26b90ea034829cf5f8f432317250d198a
    parent = None

    def CreatVMTree(tree, vm, parent):
        will_branch, simdata, gotten_VM = vm.Run(40)

        # Data = {"VMID": my_self.id, "SimData": VM.GetSimData(), "NextStepData":gotten_VM}
        Data = {"VMID": vm.id, "VM_prob": vm.VM_prob, "SimData": simdata}
        tree.create_node(identifier=Data["VMID"], parent=parent)
        VMpool.append(Data)

        if will_branch: 
            for item in gotten_VM:
                # Recursion: 递归调用 生成新的结点
                tree = CreatVMTree(tree, item, parent=Data["VMID"])
        return tree

    tree = CreatVMTree(tree, VM, parent)
    return tree, SimTreeID, VMpool

def format2file(sTree, VMpool, file="./data.csv"):
    tag_list = []
    final = []
    leaves = sTree.leaves()
    for leaf in leaves:
        tag_list.append(leaf.tag)
    
    for tag in tag_list:
        for VM in VMpool:
            if VM['VMID'] == tag:
                # final.append({"tag": tag, "prob": VM['VM_prob']})
                final.append(str(tag) + ',' + str(VM['VM_prob']) + ',未碰撞\n')
                break
    
    with open(file, "w", encoding="utf-8") as f:
        f.writelines('tag,prob,碰撞情况\n')
        f.writelines(final)

def main():
    # opt_db.init_mysql()
    sTree, SimTreeID, VMpool = SimTree()
    print('SimTreeID: ', SimTreeID)
    print(Tree_to_eChartsJSON(sTree))
    sTree.show()
    # write2dynTree(sTree)
    # write2db(SimTreeID, sTree, VMpool)
    
    # format2file(sTree, VMpool, file="./data.csv")

    # for item in VMpool:
    #     print("VMID: ", item["VMID"])
    # print("pause.")


if __name__ == '__main__':
    main()
