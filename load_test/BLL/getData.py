#-*-coding:utf-8-*-

from DAL.select import dal_user_regist, dal_file_hash, get_depart_id, dal_keywords_file, dal_special_keywords_file, dal_local_file_name, dal_check_user, dal_check_user_name
from DAL.select import dal_get_login_user, dal_is_need_mac, dal_get_mac, dal_get_login_ip,get_depart_inf
import os
from DAL.select import dal_get_first_file_info, dal_get_second_file_info

def get_user_regist(user_num):  #获取用户是否注册
    get_result= dal_user_regist(user_num)
    
    if len(get_result) == 0:  #用户不存在
        return None
    
    if str(get_result[0][0]) =="1":
        return True
    else:
        return False


def get_file_hash(file_hash):    #获取文件哈希是否存在
    get_result = dal_file_hash(file_hash)
    if str(get_result[0][0]) == "0":
        return False
    else:
        return True

# 获取关键字文件全路径，以部门编号为基准命名存储各类关键字的文件名，needStatus表示获取关键字的类别
def get_keywords(user_no, needStatus):   #获取关键字文件夹，部门编号
    file_path, file_name = get_depart_id(user_no)[0]
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    if needStatus == 0:
        file_name = str(file_name) + 'special.txt'
    elif needStatus == 1:
        file_name = str(file_name) + 'full.txt'
    elif needStatus == 2:
        file_name = str(file_name) + 'fast.txt'
    elif needStatus == 3:
        file_name = str(file_name) + 'self.txt'
    local_file = os.path.join(file_path, file_name)
    return local_file

    
def get_keywords_file(user_no): #获取关键字列表
    department_name, province, city = get_depart_inf(user_no)[0]
    get_result = dal_keywords_file(department_name, province, city)
    ret = ""
    if len(get_result) <= 0:
        return ret
    
    for i in get_result:
        ret += str(i[1]) + "-" + str(i[0]) + "\n"
        
    return ret


def get_special_keywords_file(user_no):
    ret = ""
    department_name, province, city = get_depart_inf(user_no)[0]
    get_result = dal_keywords_file(department_name, province, city)
    for i in get_result:
        ret += str(i[1]) + "-" + str(i[0]) + "\n"
    return ret


def get_local_file_name(file_hash): #获取本地文件名
    get_result = dal_local_file_name(file_hash)
    ret = ""
    if len(get_result) <= 0 or len(get_result[0]) <= 0:
        return ret
    ret = get_result[0][0]
    return ret


def check_user(user_no, user_passwd):   #验证用户名和密码
    get_result = dal_check_user(user_no, user_passwd)
    if get_result[0][0] > 0:
        return True 
    else:
        return False


def bll_check_user_name(user_no):
    get_result = dal_check_user_name(user_no)
    if get_result[0][0] > 0:
        return True
    else:
        return False


def get_login_user():
    get_result = dal_get_login_user()
    ret = []
    if len(get_result) > 0:
        for index in get_result:
            ret.append([index[0], index[1]])
    
    return ret



def get_is_need_mac(user_num):    #获取用户是否需要绑定MAC
    get_result = dal_is_need_mac(user_num)
    if str(get_result[0][0]) == "0":
        return True
    else:
        return False
    
    
def get_mac_and_hd(user_num):   #获取用户的mac地址和硬盘序列号
    get_result = dal_get_mac(user_num)
    ret = {}
    if len(get_result) > 0:
        ret["mac"] = get_result[0][0]
        ret["hd"] = get_result[0][1]
    else:
        ret["mac"] = ""
        ret["hd"] = ""
    return ret


def get_login_ip(userNo):
    get_result = dal_get_login_ip(userNo)
    ret = {}
    if len(get_result) > 0:
        ret["userId"] = get_result[0][0]
        ret["ip"] = get_result[0][1]
    
    return ret


def get_first_upload_file_info(uploadId):
    get_result = dal_get_first_file_info(uploadId)
    ret = ""
    if len(get_result) > 0:
        ret = get_result[0][0]
    return ret

def get_second_upload_file_info(uploadId):
    get_result = dal_get_second_file_info(uploadId)
    ret = ""
    if len(get_result) > 0:
        ret = get_result[0][0]
    return ret
