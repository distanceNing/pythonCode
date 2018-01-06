#! /usr/bin/python
#-*-coding:utf-8-*-

from DAL.DBMethods import DBMethods
from pymysql.err import DatabaseError

'''
@function:      数据库查询操作
@author:        屈亮亮
@createTime:    2016-9-17
@inputs:        查询字符串
@outputs：      查询结果集
'''
def selectStream(dbStr):
    db = DBMethods()
    try:
        retIndex = db.selectMethods(dbStr)
    except DatabaseError as e:
        raise DatabaseError(e)
    
    return retIndex


'''
@function:      获取文件哈希
@author:        屈亮亮
@createTime:    2016-9-17
@inputs:        文件哈希（fileHash）
@outputs：      查询结果集
'''
def selectHash(fileHash):
    
    dbStr = "select count(*) from fileInf where fileHash='%s';"%(fileHash, )
    retResult = selectStream(dbStr)
    return retResult


'''
@function:      获取mac地址
@author:        屈亮亮
@createTime:    2016-9-17
@inputs:        主机MAC地址（hostMAC）
@outputs：      查询结果集
'''
def selectMAC(hostMAC):
    
    dbStr = "select count(*) from computerInf where cptHostMAC='%s';"%(hostMAC, )
    retResult = selectStream(dbStr)
    return retResult


'''
@function:      获取userId
@author:        屈亮亮
@createTime:    2016-9-18
@inputs:        主机MAC地址（hostMAC）
@outputs：      查询结果集
'''
def selectUserId(hostMAC):
    dbStr = "select userId from computerInf where cptHostMAC='%s';"%(hostMAC, )
    retResult = selectStream(dbStr)
    return retResult
    
    


