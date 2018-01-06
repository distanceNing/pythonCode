#-*-coding:utf-8-*-

import time
from DAL.insert import dal_set_loginLog
from DAL.update import dal_set_loginStatus
from DAL.select import dal_get_userId

def get_current_time():
    ISOTIMEFORMAT='%Y-%m-%d %X'
    current_time =time.strftime( ISOTIMEFORMAT, time.localtime() ) 
    return current_time

def set_user_login(userNo, hostIp, status):
    current_time = get_current_time()
    userId = dal_get_userId(userNo)[0][0]
    ret = dal_set_loginLog(userId, status, hostIp, current_time)
    ret += dal_set_loginStatus(userId, hostIp, status)
    return ret
