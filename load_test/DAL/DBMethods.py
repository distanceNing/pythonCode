#-*-coding:utf-8-*-
'''
@author:        屈亮亮
@createTime:    2016-9-13
@function:    实例化数据库连接方法
'''

from config import sql_config
import pymysql


class DBMethods:
    def __init__(self):
        self.HOST = sql_config["host"]
        self.PORT = sql_config["port"]
        self.USER = sql_config["user"]
        self.PASSWD = sql_config["passwd"]
        self.dbName = sql_config["db_name"]
    
    def connectMysql(self):
        conn = pymysql.connect(host=self.HOST, user=self.USER, passwd=self.PASSWD, db=self.dbName, port=self.PORT, charset="utf8")
        return conn


    def selectMethods(self, dbStr, num=-1): #执行数据库查询工作
        retData = None
        conn = self.connectMysql()
        cur = conn.cursor()
        cur.execute(dbStr)
        if num == -1:
            retData = cur.fetchall()
        else:
            retData = cur.fetchmany(num)
        cur.close()
        conn.close()
        return retData
    
    
    def updateMethods(self, dbStr): # 执行数据库增加，删除，修改
        conn = self.connectMysql()
        cur=conn.cursor()
        cur.execute(dbStr)
        conn.commit()
        cur.close()
        conn.close()
        retData = 1
        return retData
        
