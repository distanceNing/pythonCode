#! /usr/bin/python3
# -*-coding:utf-8-*-

import time
import threading
from mylog import log
from .commit import commit_scan_files, init_scan_status
from .config import RemoteControl, CommandStatus
from .parse_scan_data import parse_scan_files

global_mutex = threading.Lock()
FIRST_UPLOAD = 1
SECOND_UPLOAD = 2

# 'seq': [ip, userNum, userName]
GLOBAL_ALIVE_HOSTS = dict()
GLOBAL_ALIVE_HOSTS['COUNT'] = 0

# 'CurAssignSeqs':[seq ...]
# 'seq': {}
GLOBAL_REMOTE_CONTROL = {}


def is_user_logined(user_num):
    return user_num in GLOBAL_REMOTE_CONTROL


def insert_2alive_list(seq):
    with global_mutex:
        GLOBAL_REMOTE_CONTROL[seq] = {}
        GLOBAL_REMOTE_CONTROL[seq]['status'] = CommandStatus.NO_TASK
        GLOBAL_REMOTE_CONTROL[seq]['cmd'] = None
        GLOBAL_REMOTE_CONTROL[seq]['args'] = None
        GLOBAL_REMOTE_CONTROL[seq]['rst'] = None

    # 初始化用户扫描状态
    init_scan_status(seq)

    return True


# 客户端下线
def remove_from_alive(seq):
    with global_mutex:
        if GLOBAL_REMOTE_CONTROL.get(seq, 0) != 0:
            GLOBAL_REMOTE_CONTROL.pop(seq)


# check if a client is executing task
def is_client_on_task(seq):
    try:
        if GLOBAL_REMOTE_CONTROL[seq]['cmd'] != None:
            return True
    except Exception:
        return False


# 服务端无事可做时,允许接收远程控制指令,设置其状态为 空闲
def set_remote_free(seq):
    user_no = str(seq)
    GLOBAL_REMOTE_CONTROL[user_no]['status'] = CommandStatus.NO_TASK


# 撤销任务
def cancel_task(seq, force_cancel=False):
    # 'seq': [CommandStatus, CmdInformation, ResultDetails]
    if seq not in GLOBAL_REMOTE_CONTROL:
        return False
    # 强制撤销任务
    if force_cancel:
        print("removing task ...")
        GLOBAL_REMOTE_CONTROL[seq]['status'] = CommandStatus.NO_TASK
        GLOBAL_REMOTE_CONTROL[seq]['cmd'] = ''
        return True

    # 当任务完成后,撤销任务
    if GLOBAL_REMOTE_CONTROL[seq]['status'] in CommandStatus.TaskDone:
        GLOBAL_REMOTE_CONTROL[seq]['status'] = CommandStatus.NO_TASK
        GLOBAL_REMOTE_CONTROL[seq]['cmd'] = ''
        return True
    else:
        # 如果任务没有完成,显示当前状态
        print(GLOBAL_REMOTE_CONTROL[seq]['status'])
    return False




# 下发任务
def assign_remote_task(user_no, cmd, args='None'):
    seq = user_no
    print("[GLOBAL_REMOTE_CONTROL] : " + str(GLOBAL_REMOTE_CONTROL))
    # print("[GLOBAL_REMOTE_CONTROL[seq]['status']]" + str(GLOBAL_REMOTE_CONTROL[seq]['status']))
    if user_no in GLOBAL_REMOTE_CONTROL and GLOBAL_REMOTE_CONTROL[seq]['status'] in CommandStatus.FreeState:
        GLOBAL_REMOTE_CONTROL[seq]['status'] = CommandStatus.NEW_TASK
        GLOBAL_REMOTE_CONTROL[seq]['cmd'] = cmd
        GLOBAL_REMOTE_CONTROL[seq]['args'] = args
        log("[ASSIGN-TASK-OK] {user_no} {CMD} {ARGS}".format(user_no=user_no, CMD=cmd, ARGS=args))
        return True
    log("[ASSIGN-TASK-FAILED] {user_no} {CMD} {ARGS}".format(user_no=user_no, CMD=cmd, ARGS=args))
    return False


# 获取命令执行结果
def get_task_result(userNo):
    ret = ""
    max_wait_seconds = 60 * 5
    print("[get_task_result]", userNo)

    while max_wait_seconds > 0 and GLOBAL_REMOTE_CONTROL[userNo]['status'] not in CommandStatus.TaskDone:
        print("[get_task_result] state [%d] mat_wait_seconds [%d] ..." % (
            GLOBAL_REMOTE_CONTROL[userNo]['status'], max_wait_seconds))
        time.sleep(1)
        max_wait_seconds -= 1

    ret = GLOBAL_REMOTE_CONTROL[userNo]['rst']
    GLOBAL_REMOTE_CONTROL[userNo]['status'] = CommandStatus.NO_TASK
    return ret


# 数据提交中心
def remote_event_loop():
    while True:
        time.sleep(5)
        for user_no in GLOBAL_REMOTE_CONTROL:
            status = GLOBAL_REMOTE_CONTROL[user_no]['status']

            # 如果任务执行结束
            if status in CommandStatus.TaskDone:
                cmd = GLOBAL_REMOTE_CONTROL[user_no]['cmd']
                rst = GLOBAL_REMOTE_CONTROL[user_no]['rst']
                if status is CommandStatus.FAILED:
                    data = None
                elif status is CommandStatus.SUCCESS:
                    data = parse_scan_files(rst)
                if cmd == RemoteControl.CTL_SCAN_FILES:
                    commit_scan_files(data, user_no, 1)
                elif cmd == RemoteControl.CTL_SCAN_SELF:
                    commit_scan_files(data, user_no, 0)
                elif cmd == RemoteControl.CTL_SCAN_SECOND:
                    commit_scan_files(data, user_no, 2)
                log("[remote_event_loop] %s taskdone." % user_no)
                print("status:", status, "TaskDone:", CommandStatus.TaskDone)
                # 当任务运行成功后，则更新其状态
                cancel_task(user_no)


def set_ok_results(user_no, data):
    if GLOBAL_REMOTE_CONTROL.get(user_no, 0) == 0:
        print("%s is not in GLOBAL_REMOTE_CONTROL" % user_no)
        return False

    # 填充结果
    GLOBAL_REMOTE_CONTROL[user_no]['rst'] = data
    # 更新任务状态
    GLOBAL_REMOTE_CONTROL[user_no]['status'] = CommandStatus.SUCCESS
    return True


def set_failed_results(user_no, data):
    if GLOBAL_ALIVE_HOSTS.get(user_no, 0) == 0:
        return False

    # 填充结果
    GLOBAL_REMOTE_CONTROL[user_no]['rst'] = data
    # 更新任务状态
    GLOBAL_REMOTE_CONTROL[user_no]['status'] = CommandStatus.FAILED
    return True
