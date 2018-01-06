#-*-coding:utf-8-*-
'''
@author: 屈亮亮
@createTime:2016-09-26
@function:线程池操作
'''


import queue
import threading
import sys


workQueue = queue.Queue()
maxThreads = 30
minThreads = 10
currentThreads = None
expendThreads = 5


class MyThread( threading.Thread ):
    
    def __init__( self, timeout=30, **kwargs ):
        threading.Thread.__init__(self, kwargs=kwargs)
        self.timeout = timeout
        self.setDaemon(True)

    
    '''
    @author: 屈亮亮
    @createTime:2016-09-26
    @function: 线程运行程序
    '''
    def run(self):
        while(True):
            try:
                global workQueue
                func, args = workQueue.get(timeout=self.timeout)
                func(args[0], args[1])
            except queue.Empty:
                global currentThreads
                 
                global minThreads
                if currentThreads - minThreads > 0:
                    currentThreads -= 1
                    self.join()
                    break
                continue
            except:
                print(sys.exc_info())
                raise
        
    
class ThreadPool:
    def __init__(self):
        self.__createThreadPool()
    
    
    '''
    @author: 屈亮亮
    @createTime:2016-09-26
    @function: 创建线程池
    '''
    def __createThreadPool( self ):
        global currentThreads
        global minThreads
        currentThreads = minThreads
        
        for i in range(minThreads):
            thread = MyThread()
            thread.start()
            thread.join()

    
    '''
    @author: 屈亮亮
    @createTime:2016-09-26
    @function: 线程池添加任务
    @inputs: 函数，函数参数（func, args）
    '''               
    def add_job(self, func, *args):
        global workQueue
        workQueue.put((func, args))
        
        global currentThreads
        global expendThreads

        if workQueue.qsize() - currentThreads > expendThreads:
            self.addThreads()
     
    
    '''
    @author: 屈亮亮
    @createTime:2016-09-26
    @function: 增加线程
    '''
    def addThreads(self):
        global maxThreads
        global currentThreads
        global expendThreads
         
        if maxThreads - currentThreads < expendThreads:
            for i in range(expendThreads):
                thread = MyThread()
                thread.start()
                thread.join()
