#! /usr/bin/python3
# -*-coding:utf-8-*-

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

    CTL_SCAN_FILES = "003"  # 扫描硬盘所有涉密文件
    CTL_SHUT_NETWORK = "004"  # 关闭网络,只保留与本服务器通信的网络连接
    CTL_UNINSTALL = "005"  # 远程卸载客户端
    CTL_SCAN_SECOND = "006"
    CTL_UPLOAD_FIRST = "007"
    CTL_UPLOAD_SECOND = "008"
    CTL_SCAN_SELF = "009"
    CTL_RPL_OK = "COK"
    CTL_RPL_FAILED = "CNO"


class CommandStatus:
    NO_TASK = 0
    ASSIGN_TASK = 1
    EXEC_TASK = 2
    SUCCESS = 3
    FAILED = 4
    NEW_TASK = 5
    BUSY = 6  # working with monitor stuff

    FreeState = [NO_TASK, ASSIGN_TASK, SUCCESS, FAILED]
    NeedWork = [NEW_TASK]
    TaskDone = [SUCCESS, FAILED]


MAP_CMD_STATUS = {
    "RUN": CommandStatus.EXEC_TASK,
    "OK": CommandStatus.SUCCESS,
    "FAILED": CommandStatus.FAILED
}

if __name__ == '__main__':
    print("GET", MAP_CMD_STATUS.get('RUN'))
    print(MAP_CMD_STATUS)