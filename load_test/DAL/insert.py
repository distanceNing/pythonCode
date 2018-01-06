#-*-coding:utf-8-*-
'''
@function: 数据库查询操作
@author: 屈亮亮
@createTime: 2016-10-22
'''

from .DBMethods import DBMethods


def dal_set_file_inf(file_hash, file_path, file_name, file_size, file_passwd):  #插入文件信息
    values = (file_hash, file_name, file_path, str(file_size), str(file_passwd))
    db_str = "insert into fileInf values('%s', '%s', '%s', '%s', '%s')"%values
    db_conn = DBMethods()
    try:
        ret = db_conn.updateMethods(db_str)
    except:
        ret = 0
    finally:
        return ret

def dal_set_upload_inf(file_hash, upload_time, file_name, user_num):    #插入文件上传信息
    values = (str(user_num), file_hash, file_name, str(upload_time))
    db_str = "insert into fileUploadInf(userId, fileHash, fileName, uploadTime) values(%s, '%s', '%s', '%s');"%values
    db_conn = DBMethods()
    try:
        ret = db_conn.updateMethods(db_str)
    except:
        ret = 0
    finally:
        return ret


def dal_set_user_err(data): #插入用户异常操作记录
    db_str = "insert into userErrInf(userId, errTime, fileHash, errOperate, keyWords, errCode, keyExtend, fileName) \
        values(%s, '%s', '%s', '%s', '%s', %s, '%s', '%s');"%data
    
    db_conn = DBMethods()
    try:
        ret = db_conn.updateMethods(db_str)
        print("[ERR SQL] : " + db_str)
    except:
        ret = 0
    finally:
        return ret

def dal_set_computer_inf(data): #设置主机信息
    db_str = "insert into computerInf(userId, hostMac, hostHD, sysVersion, sysType, sysTextEditor) values(%s, '%s', '%s', '%s', '%s', '%s')" % data
    db_conn = DBMethods()
    try:
        ret = db_conn.updateMethods(db_str)
    except:
        ret = 0
    finally:
        return ret

def dal_alter_user_regist(user_no):     #更新注册状态
    db_str = "update userInf set registStatus=1 where userNo='%s';"%user_no
    db_conn = DBMethods()
    ret = db_conn.updateMethods(db_str)
    return ret

def dal_set_loginLog(userId, status, hostIp, time):
    db_str = "insert into loginLog(userId, ltime, lhostIp, lstatus) values('%s', '%s', '%s', %s)"%(str(userId), str(time), str(hostIp), str(status))
    db_conn = DBMethods()
    try:
        ret = db_conn.updateMethods(db_str)
    except:
        ret = 0
    finally:
        return ret    
    
# 保存一次扫描记录
def insert_sacn_data(userId, fileName, filePath, scanTime, keywords, context):
    db_str = "insert into userScan(userId, fileName, filePath, scanTime, keywords, keyExtend) values('%s', '%s', '%s', \
      '%s', '%s', '%s')"%(userId, fileName, filePath,scanTime, keywords, context)
    db_conn = DBMethods()
    try:
        ret = db_conn.updateMethods(db_str)
    except:
        ret = 0
    finally:
        return ret

# 保存个人扫描记录
def insert_local_scan_data(userId, fileName, filePath, scanTime, keywords, context):
    db_str = "insert into selfCheck(userId, fileName, filePath, scanTime, keywords, keyExtend) values('%s', '%s', '%s', \
      '%s', '%s', '%s')" % (userId, fileName, filePath, scanTime, keywords, context)
    db_conn = DBMethods()
    try:
        ret = db_conn.updateMethods(db_str)
    except:
        ret = 0
    finally:
        return ret

# 保存智能扫描记录
def insert_second_scan_data(userId, fileName, filePath, scanTime, keywords, context):
    db_str = "insert into secondScan(userId, fileName, filePath, scanTime, keywords, keyExtend) values('%s', '%s', '%s', \
          '%s', '%s', '%s')" % (userId, fileName, filePath, scanTime, keywords, context)
    db_conn = DBMethods()
    try:
        ret = db_conn.updateMethods(db_str)
    except:
        ret = 0
    finally:
        return ret
