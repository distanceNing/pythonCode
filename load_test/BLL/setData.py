#-*-coding:utf-8-*-
'''
@function: 数据库插入操作
@author: 屈亮亮
@createTime: 2016-10-22
'''

from DAL.insert import dal_set_file_inf, dal_set_upload_inf,dal_set_user_err, dal_set_computer_inf, dal_alter_user_regist
from DAL.select import dal_get_userId, dal_get_err_status
from DAL.update import dal_set_uninstall_status
import time


def get_now_time():
    TIMEFORMAT='%Y-%m-%d %H:%M:%S'
    currentTime =  time.strftime(TIMEFORMAT, time.localtime())
    return currentTime


def insert_file_inf(file_hash, file_path, file_name, file_size, file_passwd):
    set_result = dal_set_file_inf(file_hash, file_path, file_name, file_size, file_passwd)
    if set_result > 0:
        return True
    else:
        return False

    
def insert_file_upload(user_num, file_name, file_hash, current_time):
    #upload_time = get_now_time()
    userId = dal_get_userId(user_num)[0][0]
    set_result = dal_set_upload_inf(file_hash, current_time, file_name, userId)
    if set_result > 0:
        return True
    else:
        return False
    
def insert_wor_data(wor_data, user_no, current_time): #用户异常操作记录
    #local_time = get_now_time()
    userId = dal_get_userId(user_no)[0][0]
    values = (userId, current_time, wor_data["file_hash"], wor_data["err_oprate"], wor_data["key_words"], \
              wor_data["err_code"], wor_data["keye_extend"], wor_data["file_name"])
    ret = dal_get_err_status(wor_data["file_hash"])[0][0]
    if ret == 0:
        set_result = dal_set_user_err(values)
        if set_result > 0:
            return True
        else:
            return False
    else:
        return True


def regist_user(user_no, pc_config):
    ret = 0
    mac = ""
    hds = ""
    if len(pc_config["MAC"]) > 0 and len(pc_config["HDS"]) > 0:
        for i in pc_config["MAC"]:
            if not isinstance(pc_config["MAC"][i], int):
                mac += str(pc_config["MAC"][i][1]) + "|"
        for i in pc_config["HDS"]:
            if not isinstance(pc_config["HDS"][i], int):
                hds += str(pc_config["HDS"][i][1]) + "|"
    userId = dal_get_userId(user_no)[0][0]
    sysVersion = pc_config.get("sysVersion", "win7")
    sysType = pc_config.get("sysType", 32)
    sysTextEditor = pc_config.get("sysTextEditor", "wps")
    values = (userId, mac, hds, sysVersion, sysType, sysTextEditor)

    ret += dal_set_computer_inf(values)
    ret += dal_alter_user_regist(user_no)
    if ret > 0:
        return True
    else:
        return False


def bll_set_uninstall_status(user_no):
    dal_set_uninstall_status(user_no)


    
