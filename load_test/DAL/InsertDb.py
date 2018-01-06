#! /usr/bin/python
#-*-coding:utf-8-*-

from DAL.DBMethods import DBMethods
from pymysql.err import DatabaseError

'''
@author:        屈亮亮
@createTime:    2016-9-13
@function:      数据库插入操作
'''
def insertStream(dbStr):
    db = DBMethods()
    try:
        retIndex = db.updateMethods(dbStr)
    except DatabaseError as e:
        raise DatabaseError(e)
    
    return retIndex



def insertuserInf(userId):
    dbStr = "insert into userInf values(%d, '0', 0, '0');"%(int(userId),)
    retIndex = insertStream(dbStr)
    return retIndex


def insertcomputerInf(hostIp, hostMAC, sysName, userId):
    dbStr = "insert into computerInf values('%s', '%s', '%s', %d)"%(hostIp, hostMAC, sysName, int(userId));
    retIndex = insertStream(dbStr)
    return retIndex

def insertfileUploadingInf(userId, fileHash, fileName, fileUploadTime):
    dbStr = "insert into fileUploadingInf(userId, fileHash, fileUploadingTime, fileName) values(%s, '%s', '%s', '%s')"%(int(userId), fileHash, fileUploadTime, fileName);
    retIndex = insertStream(dbStr)
    return retIndex

def insertfileInf(fileName, fileSize, filePath, fileHash):
    dbStr = "insert into fileInf values('%s', '%s', '%s', %d)"%(fileHash, fileName, filePath, fileSize);
    retIndex = insertStream(dbStr)
    return retIndex
    
    
    