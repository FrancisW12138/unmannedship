"""
操作MySQL数据库工具集，目前插入操作为简单的分表单条插入，有待优化为通用插入
"""
import sys
sys.path.append("..")
import mysql.connector
from unmannedshipv1.cfg import mysql_cfg


def link_mysql(db="idac"):
    mydb = mysql.connector.connect( \
        host = mysql_cfg.get("host", "127.0.0.1"),\
        port = mysql_cfg.get("port", 3306),\
        user = mysql_cfg.get("user", "user1"),\
        passwd = mysql_cfg.get("password", "hello"),\
        database = mysql_cfg.get("db", db),\
        charset = mysql_cfg.get("charset", "utf8")\
    )
    return mydb


# --------------------------------------------------------
""" 
创建数据库之后初始化数据数据表 谨慎操作
如果您已经建立了数据库和数据表，则无需此操作 
此操作用于完全没有建立数据库和数据表的用户
注意：您仍需要手动创建数据库 新建用户 并为之分配此数据库的相关权限

在调用 init_mysql() 之前，您应当在root用户下执行下列操作：
1. 创建新的数据库 idac 
2. 创建新用户 名：user1 密码：hello
3. 为用户 user1 分配 idac 数据库相关权限 

在此之后调用 init_mysql() 此函数会自动向数据库中添加数据表并设置各个字段的类型，
init_mysql() 的默认参数 db='idac' 一般您无法修改即可，除非您特别指定了别的数据库进行连接。
"""
def init_mysql(db='idac'):
    mydb = link_mysql("idac")
    cursor = mydb.cursor()
    sql1 = "CREATE TABLE sim_tree (TREEID VARCHAR (64) PRIMARY KEY, data MEDIUMTEXT)"
    sql2 = "CREATE TABLE sim_vm (VMID VARCHAR (64) PRIMARY KEY, data MEDIUMTEXT)"
    sql3 = "CREATE TABLE voimg (imgID VARCHAR (64) PRIMARY KEY, VMID VARCHAR (64), data MEDIUMBLOB)"
    cursor.execute(sql1)
    cursor.execute(sql2)
    cursor.execute(sql3)
    mydb.close()  # 关闭数据库连接
    print("init mysql on database '{}' succeed, created 3 tables.".format(db))

# --------------------------------------------------------

def del_dynTree():
    mydb = link_mysql()
    cursor = mydb.cursor()
    sql_del = "delete from dyn_tree"
    # print(sql_insert)
    cursor.execute(sql_del)
    mydb.commit()  # 提交插入操作
    print("dyn_tree table clean.")
    mydb.close()  # 关闭数据库连接
    pass


def insert_into_dynTree(rootId, children):
    mydb = link_mysql()
    cursor = mydb.cursor()
    sql_insert = "INSERT INTO dyn_tree (rootId,children) VALUES (%s, %s)"
    # print(sql_insert)
    cursor.execute(sql_insert, (rootId, children))
    mydb.commit() # 提交插入操作
    print("1 record inserted.")
    mydb.close()  # 关闭数据库连接
    pass


def insert_into_simtree(TREEID, data):
    """
    将 仿真树 数据插入表 sim_tree
    :TREEID : varchar string 数字序列,
    :data ： JSON格式的字符串
    """
    mydb = link_mysql()
    cursor = mydb.cursor()
    sql_insert = "INSERT INTO sim_tree (TREEID, data) VALUES (%s, %s)"
    # print(sql_insert)
    cursor.execute(sql_insert, (TREEID, data))
    mydb.commit() # 提交插入操作
    print("1 record inserted.")
    mydb.close()  # 关闭数据库连接
    pass

def insert_into_simvm(VMID, data):
    """ 
    将VM数据插入表sim_vm 
    :VMID : varchar string 数字序列,
    :data : JSON格式的字符串
    """
    mydb = link_mysql()
    cursor = mydb.cursor()
    sql_insert = "INSERT INTO sim_vm (VMID, data) VALUES (%s, %s)"
    # print(sql_insert)
    cursor.execute(sql_insert, (VMID, data))
    mydb.commit() # 提交插入操作
    print("1 record inserted.")
    mydb.close()  # 关闭数据库连接
    pass

# 将图片插入数据库的方式暂时不用
def insert_into_voimg(imgID, VMID, data):
    """ 
    将VM仿真过程中生成的voimg图片插入表 voimg 
    :imgID : varchar string 数字序列,
    :VMID : 所属VM ,varchar string 数字序列,
    :data : 二进制字节流
    """
    mydb = link_mysql()
    cursor = mydb.cursor()
    sql_insert = "INSERT INTO voimg (imgID, VMID, data) VALUES (%s, %s, %s)"
    # print(sql_insert)
    cursor.execute(sql_insert, (imgID, VMID, data))
    mydb.commit() # 提交插入操作
    print("1 record inserted.")
    mydb.close()  # 关闭数据库连接
    pass

def select_from_simtree(TREEID):
    """ 
    从表sim_tree中查询tree数据
    :TREEID : 查询的TREE,
    :return : data = (TREEID, data)
    """
    mydb = link_mysql()
    cursor = mydb.cursor()
    sql_select = "SELECT TREEID, data FROM sim_tree WHERE TREEID = {}".format(TREEID)
    cursor.execute(sql_select)
    # data = cursor.fetchall()
    data = cursor.fetchone() # TREEID是唯一的，两者结果是一致的
    mydb.close()
    return data

def select_from_dyntree(TREEID):
    mydb = link_mysql()
    cursor = mydb.cursor()
    sql_select = "SELECT rootId, children FROM dyn_tree WHERE rootId = {}".format(TREEID)
    cursor.execute(sql_select)
    data = cursor.fetchone() # TREEID是唯一的，两者结果是一致的
    mydb.close()
    return data

def select_first_tree():
    mydb = link_mysql()
    cursor = mydb.cursor()
    sql_select = "SELECT rootId, children FROM dyn_tree limit 1"
    cursor.execute(sql_select)
    data = cursor.fetchone()
    mydb.close()
    return data

def select_lastest_tree():
    """
    从表sim_tree中查询最新的一条tree数据
    : return: (TREEID, data)
    """
    mydb = link_mysql()
    cursor = mydb.cursor()
    sql_select = "SELECT TREEID, DATA FROM sim_tree WHERE TREEID = (SELECT MAX(TREEID) FROM sim_tree)"
    cursor.execute(sql_select)
    data = cursor.fetchone() 
    mydb.close()
    return data

def select_from_simvm(VMID):
    """ 
    从表sim_vm中查询VM数据 
    :VMID : 查询的VM,
    :return : data = (VMID, data)
    """
    # print("进入数据库操作函数vm")
    mydb = link_mysql()
    cursor = mydb.cursor()
    sql_select = "SELECT VMID, data FROM sim_vm WHERE VMID = {}".format(VMID)
    cursor.execute(sql_select)
    # data = cursor.fetchall()
    data = cursor.fetchone() # VMID是唯一的，两者结果是一致的
    mydb.close()
    return data
    
# 从数据库中查询一张图片
def select_from_voimg(imgID):
    """ 
    从表voimg中查询标识为 imgID 的VM的imgs 
    :imageid : 查询img所属的ID,
    :return : data = (imgID, VMID, data)
    """
    mydb = link_mysql()
    cursor = mydb.cursor()
    sql_select = "SELECT imgID, VMID, data FROM voimg WHERE imgID = '{}'".format(imgID)
    cursor.execute(sql_select)
    data = cursor.fetchone() # 
    mydb.close()
    return data
