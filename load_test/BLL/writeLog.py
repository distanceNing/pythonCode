#! /usr/bin/python
#-*-coding:utf-8-*-

import os


class log:
    def __init__(self):
        self.path = "/home/jefferson/log"
        self.fileName = "log.txt"
        
        
    '''
    @author:        屈亮亮
    @createTime:    2016-9-13
    @function:      追加的方式打开文件
    '''    
    def openLog(self):
        
        if os.path.exists(self.path):
                file = os.path.join(self.path, self.fileName)
        else:
            os.makedirs(self.path)
            file = os.path.join(self.path, self.fileName)
        try: 
            print(file)   
            fw = open(file, "a")
        except:
            print("Error: log open fail.")
        return fw
    
    
    def writeFile(self, writeStr):
        
        file = self.openLog()
        file.write(writeStr)
        
        file.close()
    
    
    
    