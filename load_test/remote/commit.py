#encoding: utf8

SELF_RESULT = 0
SCAN_RESULT = 1
SECOND_RESULT = 2

from DAL.select import dal_get_userId
from DAL.update import DAL_update_user_scan_status, DAL_update_user_upload_status
from DAL.insert import insert_sacn_data, insert_local_scan_data, insert_second_scan_data
from mylog import xtrace, log, error_log

# 数据接口---初始化用户的扫描状态
def init_scan_status(userNo):
    userId = dal_get_userId(userNo)[0][0]

    # 初始化扫描状态--未扫描
    DAL_update_user_scan_status(userId, 0)

    return True

# 数据接口---重置用户的上传文件状态
def update_user_upload_status(userNo):
    userId = dal_get_userId(userNo)[0][0]
    DAL_update_user_upload_status(userId, 0)
    return True


# 数据接口---保存扫描结果
def commit_scan_files(scan_data, user_no, self_check):
    _user_id = dal_get_userId(user_no)
    if len(_user_id) < 1 or len(_user_id[0]) < 1:
        xtrace("dal_get_userId(%s): " % user_no)
        print("return:", _user_id)
        return False
    else:
        user_id = _user_id[0][0]
        xtrace("%s ==> %s" % (user_no, user_id))

    print("[COMMITTING_FILES]")

    # 即使扫描数据为空，也应该刷新自己的状态位
    # data 为None 说明扫描没有结果
    if scan_data is None:
        log("detect data is None then just update the client scan_status")
        DAL_update_user_scan_status(user_id, 0)
        return False

    for file_name, file_path, scan_time, keywords, context in scan_data:
        xtrace("[COMMITING]:", user_no, file_name, file_path, scan_time, keywords, context)
        if self_check == SELF_RESULT:
            insert_local_scan_data(user_id, file_name, file_path, scan_time, keywords, context)
        elif self_check == SCAN_RESULT:
            insert_sacn_data(user_id, file_name, file_path, scan_time, keywords, context)
        elif self_check == SECOND_RESULT:
            insert_second_scan_data(user_id, file_name, file_path, scan_time, keywords, context)

    # 设置扫描状态--完成
    log("commit done update the client scan_status")
    DAL_update_user_scan_status(user_id, 0)

    return True

