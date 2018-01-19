#! /usr/bin/python3
#-*-coding:utf-8-*-
from BLL.getData import get_login_user, get_login_ip
from DAL.insert import dal_set_loginLog
from DAL.update import dal_set_loginStatus
from BLL.userLogin import get_current_time
from remote.commit import init_scan_status, update_user_upload_status

def close_all_conn():
    login_user_list = get_login_user()
    if len(login_user_list) == 0:
        return True
    for index in login_user_list:
        current_time = get_current_time()
        dal_set_loginLog(index[0], 0, index[1], current_time)
        dal_set_loginStatus(index[0], index[1], 0)
    return True

def close_conn(user_no):
    current_time = get_current_time()
    login_user_list = get_login_ip(user_no)
    dal_set_loginLog(login_user_list["userId"], 0, login_user_list["ip"], current_time)
    dal_set_loginStatus(login_user_list["userId"],login_user_list["ip"], 0)
    # 更新用户扫描状态和上传状态
    init_scan_status(user_no)
    update_user_upload_status(user_no)
    return True
    
    
