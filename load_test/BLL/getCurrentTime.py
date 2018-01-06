#! /usr/bin/python
#-*-coding:utf-8-*-
import time


def getCurrentTime():
    
    TIMEFORMAT='%Y-%m-%d %H:%M:%S'
    currentTime =  time.strftime(TIMEFORMAT, time.localtime())
    return currentTime

def getCurrentTimeTwo():
    
    TIMEFORMAT='%Y%m%d%H%M%S'
    currentTime =  time.strftime(TIMEFORMAT, time.localtime())
    return currentTime