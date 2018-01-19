#-*-coding:utf-8-*-


'''
@function: 数据库更新
@author: 屈亮亮
@createTime: 2016-10-22
'''
from DAL.DBMethods import DBMethods


def dal_set_loginStatus(userId, userIp, status):
    db_str = "update userInf, computerInf set loginStatus=%s, userIp='%s' where userInf.userId=%s and userInf.userId=computerInf.userId"%(str(status), userIp, str(userId))
    db_conn = DBMethods()
    ret = db_conn.updateMethods(db_str)
    return ret


# 这个数据库接口中，用户给返回的是userId 而不是userNO
# 因此不需要再次获取userId
def DAL_update_user_scan_status(user_id, status):
    db = DBMethods()
    values = (status, user_id)
    dbStr = 'update computerInf set userScanStatus="%s" where userId="%s";'
    dbStr = dbStr%values
    ret = db.updateMethods(dbStr)
    return ret

# 重置用户第一次扫描文件上传状态
def DAL_update_user_first_upload_status(user_id, status):
    db = DBMethods()
    values = (status, user_id)
    dbStr = 'update userScan set uploadStatus="%s" where userId="%s" and uploadStatus=1;'
    dbStr = dbStr % values
    ret = db.updateMethods(dbStr)
    return ret

# 重置用户第二次扫描文件上传状态
def DAL_update_user_second_upload_status(user_id, status):
    db = DBMethods()
    values = (status, user_id)
    dbStr = 'update secondScan set uploadStatus="%s" where userId="%s" and uploadStatus=1;'
    dbStr = dbStr % values
    ret = db.updateMethods(dbStr)
    return ret


# 更新一次扫描记录
def dal_update_scan_data(file_name, file_hash, file_path):
    dbStr = 'update userScan set uploadStatus=2, fileHash="%s", fileName="%s" where filePath="%s";'%(file_hash, file_name, file_path)
    db = DBMethods()
    ret = db.updateMethods(dbStr)
    return ret

# 更新二次扫描记录
def dal_update_second_scan_data(file_name, file_hash, file_path):
    dbStr = 'update secondScan set uploadStatus=2, fileHash="%s", fileName="%s" where filePath="%s";' % (
    file_hash, file_name, file_path)
    db = DBMethods()
    ret = db.updateMethods(dbStr)
    print("[SECOND_UPDATE_SCAN_FILE] : " + dbStr)
    return ret

# 一次扫描文件上传失败
def dal_update_scan_failed(usId):
    usId = int(usId)
    dbStr = 'update userScan set uploadStatus=3 where usId=%d;' % (usId)
    db = DBMethods()
    ret = db.updateMethods(dbStr)
    return ret

# 二次扫描文件上传失败
def dal_update_scan_second_failed(ssId):
    ssId = int(ssId)
    dbStr = 'update secondScan set uploadStatus=3 where ssId=%d;' % (ssId)
    db = DBMethods()
    ret = db.updateMethods(dbStr)
    return ret


def dal_set_uninstall_status(user_no):
    dbStr = 'update userInf set registStatus=0,loginStatus=0 where userNo="%s";' % (user_no)
    db = DBMethods()
    ret = db.updateMethods(dbStr)
    return ret




