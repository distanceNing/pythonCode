#! /usr/bin/python
#-*-coding:utf-8-*-

from DAL import InsertDb, SelectDb
from pymysql.err import DatabaseError
from BLL.getCurrentTime import getCurrentTime


'''
@function: 获取文件哈希数目
@author: 屈亮亮
@createTime: 2016-9-16
@inputs: 文件哈希（fileHash）
@outputs: 文件哈希个数
'''
def getHash(fileHash):
    try:
        retResult= SelectDb.selectHash(fileHash)
    except DatabaseError as e:
        raise DatabaseError(e)
    except:
        print("Error：db err.")
        raise DatabaseError(e)
    return retResult[0][0]


'''
@function: 获取文件哈希数目
@author: 屈亮亮
@createTime: 2016-9-18
@inputs: 文件MAC（hostMAC）
@outputs: userId
'''
def getUserId(hostMAC):
    try:
        retResult= SelectDb.selectUserId(hostMAC)
    except DatabaseError as e:
        raise DatabaseError(e)
    except:
        print("Error：db err.")
        raise DatabaseError(e)
    return retResult[0][0]
    
    
'''
@function: 插入上传信息
@author: 屈亮亮
@createTime: 2016-9-16
@inputs: 用户编号，上传时间，文件名，主机ip，mac地址，系统名，文件哈希（userId, uploadTime, fileName, hostIp, hostMAC, sysName, fileHash）
@outputs： 更新行数
'''
def insertUploadInfo(uploadTime, fileName, hostIp, hostMAC, sysName, fileHash): 
    
    dbIndex = 0
    userId = getCurrentTime()[-5: ]
    try:    
        dbres = SelectDb.selectMAC(hostMAC)
        if dbres[0][0] == 0:
            dbIndex += InsertDb.insertuserInf(userId)
            dbIndex += InsertDb.insertcomputerInf(hostIp, hostMAC, sysName, userId)
            
        else:
            userId = getUserId(hostMAC)
            
        dbIndex += InsertDb.insertfileUploadingInf(userId, fileHash, fileName, uploadTime)   
                 
    except DatabaseError as e:
        print(e)
        raise DatabaseError(e)
    except:
        print("Error：db err.")
        raise DatabaseError(e)
    return dbIndex


'''
@function: 插入文件信息
@author: 屈亮亮
@createTime: 2016-9-16
@inputs: 文件名，文件大小，文件位置，文件哈希（fileName, fileSize, filePath, fileHash)
@outputs： 更新行数
'''
def insertFile(fileName, fileSize, filePath, fileHash):
    try:
        InsertDb.insertfileInf(fileName, fileSize, filePath, fileHash)       
    except DatabaseError as e:
        raise DatabaseError(e)
    except:
        print("Error：db err.")
        raise DatabaseError(e)
            

