#-*-coding:utf-8-*-
'''
@function: 数据库查询操作
@author: 屈亮亮
@createTime: 2016-10-22
'''

from .DBMethods import DBMethods


def dal_user_regist(user_num):  #获取用户是否注册
    db_str = "select registStatus from userInf where userNo='%s';"%(user_num,)
    db_conn = DBMethods()
    ret = db_conn.selectMethods(db_str)
    return ret

    
def dal_file_hash(file_hash):   #获取文件哈希
    db_str = "select count(fileHash) from fileInf where fileHash='%s';"%(file_hash,)
    db_conn = DBMethods()
    ret = db_conn.selectMethods(db_str)
    return ret


# 获取文件名
def get_depart_id(userAcc):
    dbStr = 'select keyPath, userInf.departmentId from userInf, departmentInf where userInf.departmentId = departmentInf.departmentId and userNo="%s";'
    dbStr = dbStr%(str(userAcc))
    db = DBMethods()
    ret = db.selectMethods(dbStr)
    return ret

def dal_keywords_file(department_name, province, city):    #获取关键字列表
    if province == None:
        dbStr = 'SELECT keyword, keyLever FROM keywordsInf ORDER BY keyLever'
    elif city == None:
        dbStr = 'SELECT keyword, keyLever FROM keywordsInf,departmentKey WHERE (departmentKey.departmentId'
        dbStr += ' = (SELECT departmentId  FROM departmentInf WHERE province="{0}" AND city="二级部门" AND departmentName="三级部门")'
        dbStr += 'OR (departmentName="三级部门" and province="一级部门" and city="二级部门"))'
        dbStr += ' AND keywordsInf.keyId=departmentKey.keyId ORDER BY keyLever'
        dbStr = dbStr % (str(province))
    elif department_name != u'三级部门':
        dbStr = 'SELECT keyword, keyLever FROM keywordsInf,departmentKey,departmentInf WHERE (departmentKey.departmentId'
        dbStr += ' IN (SELECT departmentId  FROM departmentInf WHERE province="{0}" AND (city="二级部门" OR city="{1}") AND (departmentName="三级部门" OR departmentName="{2}"))'
        dbStr += 'OR (departmentName="三级部门" and province="一级部门" and city="二级部门"))'
        dbStr += ' AND keywordsInf.keyId=departmentKey.keyId AND departmentInf.departmentId=departmentKey.departmentId ORDER BY keyLever'
        dbStr = dbStr.format(province,city,department_name)
    else:
        dbStr = 'select keyword, keyLever, keywordsInf.keyId, createUserId,province,city,departmentName'
        dbStr += ' from keywordsInf,departmentKey,departmentInf  where (departmentKey.departmentId'
        dbStr += ' in (select departmentId  from departmentInf where province="{0}" and city="二级部门" or city="{1}" and departmentName="{2}")'
        dbStr += 'OR (departmentName="三级部门" and province="一级部门" and city="二级部门"))'
        dbStr += ' and keywordsInf.keyId=departmentKey.keyId and departmentInf.departmentId=departmentKey.departmentId order by keyLever'
        dbStr = dbStr.format(province, city, department_name)
    db_conn = DBMethods()
    print("key:" + dbStr)
    ret = db_conn.selectMethods(dbStr)
    return ret

# 获取用于监测报警和二次扫描的关键字
def dal_special_keywords_file():
    db_str = "select keyword, keyLever from keywordsInf where keyLever=3"
    db_conn = DBMethods()
    ret = db_conn.selectMethods(db_str)
    return ret


def dal_local_file_name(file_hash):  #获取本地文件名
    db_str = "select fileLocalName from fileInf where fileHash='%s';"
    db_str %= (file_hash,)
    db_conn = DBMethods()
    ret = db_conn.selectMethods(db_str)
    return ret
    
    
def dal_get_userId(userNo):	#获取用户编号
    db_str = "select userId from userInf where userNo='%s';"
    db_str %= (userNo,)
    db_conn = DBMethods()
    ret = db_conn.selectMethods(db_str)
    return ret  
    

def dal_check_user(userNo, userPasswd):
    db_str = "select count(*) from userInf where binary userNo='%s' and binary userPasswd=password('%s');"
    db_str %= (userNo, userPasswd)
    db_conn = DBMethods()
    ret = db_conn.selectMethods(db_str)
    return ret  


def dal_check_user_name(userNo):
    db_str = "select count(*) from userInf where userNo='%s';"
    db_str %= (userNo)
    db_conn = DBMethods()
    ret = db_conn.selectMethods(db_str)
    return ret


def dal_get_login_user():
    db_str = "select userInf.userId, userIp from userInf, computerInf where userInf.userId=computerInf.userId and loginStatus=1;"
    db_conn = DBMethods()
    ret = db_conn.selectMethods(db_str)
    return ret

def dal_get_login_ip(user_no):
    db_str = "select userInf.userId, userIp from userInf, computerInf where userInf.userId=computerInf.userId and loginStatus=1 and userNo='%s';"
    db_str %= (user_no, )
    db_conn = DBMethods()
    ret = db_conn.selectMethods(db_str)
    return ret


def dal_is_need_mac(user_num):  #获取用户注册时是否需要验证MAC
    db_str = "select userLoginStatus from departmentInf where departmentId=(select departmentId from userInf where userNo='%s');"%(user_num,)
    db_conn = DBMethods()
    ret = db_conn.selectMethods(db_str)
    return ret
        

def dal_get_mac(user_num):  #获取用户注册时是否需要验证MAC
    db_str = "select hostMac, hostHD from computerInf where userId=(select userId from userInf where userNo='%s');"%(user_num,)
    db_conn = DBMethods()
    ret = db_conn.selectMethods(db_str)
    return ret


def get_depart_inf(userNo): # 获取部门信息
    db_str = "SELECT departmentName,province,city FROM departmentInf,userInf WHERE departmentInf.departmentId=userInf.departmentId AND userNo='%s';"%(userNo,)
    db_conn = DBMethods()
    ret = db_conn.selectMethods(db_str)
    return ret


def dal_get_first_file_info(uploadId):
    db_str = "select filePath from userScan where usId={0};"
    db_str = db_str.format(uploadId)
    db_conn = DBMethods()
    ret = db_conn.selectMethods(db_str)
    return ret

def dal_get_second_file_info(uploadId):
    db_str = "select filePath from secondScan where ssId={0};"
    db_str = db_str.format(uploadId)
    print("sql sentence is", db_str)
    db_conn = DBMethods()
    ret = db_conn.selectMethods(db_str)
    return ret

def dal_get_err_status(file_hash):
    db_str = "select count(*) from userErrInf where fileHash='{0}' and errStatus=2;"
    db_str = db_str.format(file_hash)
    db_conn = DBMethods()
    ret = db_conn.selectMethods(db_str)
    print("[err information] is " + db_str)
    return ret
