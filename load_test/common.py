#! /usr/bin/python3
# -*-coding:utf-8-*-

import hashlib
import struct
import time

from BLL.getData import check_user, bll_check_user_name
from BLL.getData import get_is_need_mac, get_mac_and_hd
from BLL.getData import get_user_regist, get_file_hash, get_special_keywords_file
from BLL.setData import insert_file_inf, insert_file_upload, insert_wor_data, regist_user
from mylog import xtrace
from DAL.update import dal_update_scan_data, dal_update_second_scan_data, dal_update_scan_failed, \
    dal_update_scan_second_failed

HOST = "0.0.0.0"
PORT = 50005
BIND_INFO = (HOST, PORT)

FILE_KEEP_DIR = "/home/dev/safeDir"
NO_SPECIFIC = 'Unknown'

EVENT = {
    '0': "用户在上网时段打开涉密文件",
    '1': "用户将涉密文件拷贝到移动存储设备",
    '2': "本地磁盘扫描",
    '3': "U盘事件",
}

HEAD_FORMAT = "!3sI"
HEAD_SIZE = struct.calcsize(HEAD_FORMAT)
MAX_PACKET_SIZE = 1024
TCP_SLEEP_SECOND = 1

MonProcessList = {
    '101': "QQ.exe",
    '103': "iexplore.exe",
    '104': "QQBrowser.exe",
    '105': "360se.exe",
    '107': "firefox.exe",
    '108': "chrome.exe",
    '109': "sogouexplorer.exe",
    '110': "opera.exe",
    '111': "Maxthon.exe",
    '112': "通用浏览器",
    '201': "wps.exe"
}


class RemoteControl:
    CTL_END_SESSION = "000"
    CTL_PROCESS_LIST = "001"
    CTL_KILL_PROCESS = "002"

    CTL_RPL_OK = "COK"
    CTL_RPL_FAILED = "CNO"


class CommandStatus:
    NO_TASK = 0
    ASSIGN_TASK = 1
    EXEC_TASK = 2
    SUCCESS = 3
    FAILED = 4
    NEW_TASK = 5
    # working with monitor stuff
    BUSY = 6

    FreeState = [NO_TASK, ASSIGN_TASK, SUCCESS, FAILED]
    NeedWork = [NEW_TASK]
    TaskDone = [SUCCESS, FAILED]


# 解析注册信息为一个字典
def parse_register_info(info):
    lists = info.split('\n')
    reg = {}
    for ite in lists:
        ite = ite.strip()
        if len(ite) <= 0:
            continue

        dev = ite.split(' ')[0]
        dev_name, dev_num = dev.split(':')
        reg[dev_name] = {}
        dev_num = int(dev_num)
        reg[dev_name]['num'] = dev_num
        items = ite.split(' ')[1:]
        for (i, e) in enumerate(items):
            addr, desc = e.split('-')
            reg[dev_name][i] = (desc, addr)
    return reg




# 报警文件不上传，报警记录接口
def get_warnings(info):
    log_time, file_hash, keywords_info, op, file_name = info.split('\n')
    xtrace("log_time:{lt}, file_hash:{fh}, op:{op}, keywords_info:{im}, file_name:{fn}".format(
        lt=log_time, fh=file_hash, op=op, im=keywords_info, fn=file_name))

    # 解析事件详情
    op_num, op_items = op.split(' ', 1)

    op_details = op_items  # 记录事件详情

    match_text = ""
    print("[op_num] is " + op_num)
    print("[op_details] is " + op_details)
    if op_num == '0':
        # 解析关键字
        real_keywords = keywords_info.split(":")[0:-1]
        print("--------------------------------")
        print("[real_keywords] : " + str(real_keywords))
        for i in real_keywords:
            rank, word, nmatch, location = i.split('-')
            tmp = "(级别:{rk} 关键字:{wd} 重复次数:{nm} 位置:{ln}) ".format(
                rk=rank, wd=word, nm=nmatch, ln=location)
            print("--------------------------------")
            print("[tmp] is " + tmp)
            match_text += tmp
    else:
        # 当日志类型为 U盘事件时
        # 没有文件哈希，也没有关键字详情，只是单纯记录U盘的插入或者拔出事件
        # 记录U盘详细信息 statu: IN|usb name:可移动磁盘|serial number:2985626131|mount drive:H
        match_text = keywords_info

    ret = {}
    ret["keye_extend"] = op_details
    ret["file_hash"] = file_hash
    ret["err_oprate"] = op_details
    ret["err_code"] = op_num  # 事件编码,可以根据该·事件编码·解析日志详情, 0为用户异常信息， 1为u盘插入
    ret["key_words"] = match_text
    ret["file_name"] = file_name.replace("\\", "/")

    return ret


# 获取服务到期时间
def get_expired_time():
    return "2027-06-14 12:12:12"


def kill_myself():
    from sys import platform
    from os import system, getpid

    kill_str = {
        'linux': "kill -9 {PID}",
        'win32': "taskkill /f /pid {PID}"
    }
    shut_myself = kill_str[platform].format(getpid())
    system(shut_myself)


def cal_file_hash(file_path):
    with open(file_path, 'rb') as f:
        md5obj = hashlib.md5()
        md5obj.update(f.read())
        filehash = md5obj.hexdigest()
        return filehash


# 创建关键字文件
def mk_keyWords_file(local_file, user_no):
    keywords = get_special_keywords_file(user_no)
    try:
        op = open(local_file, 'w', encoding='utf-8')
        op.write(keywords)
        op.close()
        return True
    except:
        return False


# 检查用户当前登录主机的mac地址是否与用户注册时
# 提交的mac地址一致，只有一致才允许登录
def identify_usermac(user_no, mac_addr):
    if get_is_need_mac(user_no):
        macs = get_mac_and_hd(user_no)
        mac_list = [mac for mac in macs['mac'].split('|') if len(mac.strip())]
        ret = mac_addr.strip() in mac_list
        return ret
    else:
        return True


def insert_user2DB(user_no, pc_config):  # 数据库接口--注册用户名、主机信息
    ret = regist_user(user_no, pc_config)
    return ret


def pro_local_file_name(file_name):
    return str(time.time()) + "." + file_name.rsplit(".", 2)[1] + "." + file_name.rsplit(".", 2)[2]


def check_passwd(user_no, user_pas):
    ret = check_user(user_no, user_pas)
    return ret


def check_user_name(user_no):
    ret = bll_check_user_name(user_no)
    return ret


# 数据库接口--当前hash值对应的文件是否存在
def is_hash_here(file_hash):
    ret = get_file_hash(file_hash)
    return ret


def set_file_inf(file_hash, file_path, file_name, file_size, file_passwd):
    ret = insert_file_inf(file_hash, file_path, file_name, file_size, file_passwd)
    return ret


# 数据库接口--文件上传记录
def log_file_upload(user_no, file_name, file_hash, current_time):
    ret = insert_file_upload(user_no, file_name, file_hash, current_time)
    return ret


# 将数据库接口--判断用户是否注册过
def is_user_registed(user_no):
    ret = get_user_regist(user_no)
    return ret


# 记数据库接口--记录警报日志
def record_warnings(info, user_no, current_time):
    wor_data = get_warnings(info)
    insert_wor_data(wor_data, user_no, current_time)
    return True


# 更改一次扫描记录
def update_scan_data(file_name, file_hash, file_path):
    file_path = file_path.replace("\\", "/")
    dal_update_scan_data(file_name, file_hash, file_path)
    return True


# 更改二次扫描记录
def update_second_scan_data(file_name, file_hash, file_path):
    file_path = file_path.replace("\\", "/")
    dal_update_second_scan_data(file_name, file_hash, file_path)
    return True


# 一次扫描文件上传失败
def update_scan_failed(usId):
    dal_update_scan_failed(usId)
    return True


# 二次扫描文件上传失败
def update_scan_second_failed(ssId):
    dal_update_scan_second_failed(ssId)
    return True


# 解析数据
def register_user(user_no, data):
    pc_info = parse_register_info(data)
    if insert_user2DB(user_no, pc_info):
        return True
    return False
