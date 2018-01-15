from enum import Enum

import os

from BLL.close_conn import close_conn
from BLL.getData import get_keywords, get_first_upload_file_info, get_second_upload_file_info
from BLL.userLogin import set_user_login
from mylog import error_log, log, get_curtime

from common import check_passwd, check_user_name, is_user_registed, identify_usermac, get_expired_time, register_user, \
    record_warnings, mk_keyWords_file, is_hash_here, \
    log_file_upload, update_scan_data, update_second_scan_data, FILE_KEEP_DIR, CommandStatus, update_scan_failed, \
    update_scan_second_failed

# config
from config import UploadServerConfig, FILE_TYPE, MAP_TYPE
from remote.config import MAP_CMD_STATUS, RemoteControl
from remote.remote_control import remove_from_alive, insert_2alive_list, GLOBAL_REMOTE_CONTROL
from trans_file import erase_zombie_client, EXECUTING_QUEUE, UPLOAD_QUEUE, FIRST_UPLOAD, SECOND_UPLOAD, \
    LOG_UPLOAD


class kProccessState(Enum):
    kAuthing = 1
    kNeedRegister = 2
    kAuthSuccess = 3

    kFirstScan = 10
    kSecondScan = 11
    kSelfScan = 12
    kMakeKwFail = 13
    kMakeKwSuccess = 14

    kHbt = 33

    # 任务处理失败的情况，需关闭客户端的连接
    kAuthFail = 100
    kEndConnecion = 101

    kRecvFile = 10010
    kNeedFileHash = 10011
    kNeedFileInfo = 10012
    kRecvDone = 10013

    kRemoteCtl = 10020
    kUploadFile = 10021
    kCtlSuccess = 10022
    kCtlFail = 10023


kOK = "OK"
kFail = "FAILED"
kHbt = "HBT"


class kFileState(Enum):
    kOpenFail = 1001
    kExisted = 1002
    kFileNameIsNone = 1003


class Client:
    def __init__(self, addr):
        self.__user_no = None
        self.__response = ""
        self.__ctl_status = RemoteControl.CTL_NO_TASK
        self.user_addr = None
        self.process_state = kProccessState.kAuthing
        self.__kw_file = None
        self.recv_file_name = None
        self.recv_file_type = None
        self.recv_file_path = None
        self.recv_file_hash = None
        self.recv_file_arg = None
        self.__ctl_args = None
        self.current_time = get_curtime()
        self.__is_login =False

    def is_login(self):
        return self.__is_login


    def get_ctl_status(self):
        return self.__ctl_status

    def set_ctl_status(self, cmd, args):
        if self.__ctl_status != RemoteControl.CTL_NO_TASK:
            return False
        GLOBAL_REMOTE_CONTROL[self.__user_no]['status'] = CommandStatus.ON_TASK
        self.__ctl_status = cmd
        self.__ctl_args = args
        self.process_state = kProccessState.kRemoteCtl
        # 打印log
        log("GET-TASK args:", args)
        if cmd is RemoteControl.CTL_SCAN_FILES:
            log("REMOTE-CMD: SCAN_FILES {ARGS}".format(ARGS=args))
        elif cmd is RemoteControl.CTL_SCAN_SECOND:
            log("REMOTE-CMD: SCAN_SECOND {ARGS}".format(ARGS=args))
        elif cmd is RemoteControl.CTL_SCAN_SELF:
            log("REMOTE-CMD: SCAN_SELF {ARGS}".format(ARGS=args))
        elif cmd is RemoteControl.CTL_UPLOAD_FIRST:
            log("REMOTE-CMD: UPLOAD_FIRST {ARGS}".format(ARGS=args))
        elif cmd is RemoteControl.CTL_UPLOAD_SECOND:
            log("REMOTE-CMD: UPLOAD_SECOND {ARGS}".format(ARGS=args))
        elif cmd is RemoteControl.CTL_UNINSTALL:
            log("[UNINSTALL CLIENT] {ARGS}".format(ARGS=args))
        elif cmd is RemoteControl.CTL_SHUT_NETWORK:
            log("REMOTE-CMD: SHUT_NETWORK {ARGS}".format(ARGS=args))
        return True

    def get_user_no(self):
        return self.__user_no

    def get_kw_filename(self):
        return self.__kw_file

    def update_task_state(self, rst, info):
        seq = self.__user_no
        cmd = self.__ctl_status

        if cmd is RemoteControl.CTL_SCAN_SELF or cmd is RemoteControl.CTL_SCAN_FILES or \
                cmd is RemoteControl.CTL_SCAN_SECOND:
            # 更新任务执行状态: 成功、失败、正在执行中
            if rst != RemoteControl.CTL_RPL_OK:
                log("SECOND_SCAN_FILE %s FAILED" % self.__user_no)

                self.process_state = kProccessState.kCtlFail

            else:
                self.process_state=kProccessState.kCtlSuccess
                log("SECOND_SCAN_FILE %s OK" % self.__user_no)
                self.process_state = kProccessState.kCtlFail
            GLOBAL_REMOTE_CONTROL[seq]['status'] = MAP_CMD_STATUS.get(rst)
            GLOBAL_REMOTE_CONTROL[seq]['rst'] = rst
        elif cmd is RemoteControl.CTL_UPLOAD_SECOND or cmd is RemoteControl.CTL_UPLOAD_FIRST:
            if rst != RemoteControl.CTL_RPL_OK:
                self.process_state = kProccessState.kCtlFail
                if self.__ctl_status == RemoteControl.CTL_UPLOAD_FIRST:
                    log("UPLOAD_FIRST_SCAN_FILE %s FAILED" % self.__user_no)
                    update_scan_failed(self.__ctl_args)
                elif self.__ctl_status == RemoteControl.CTL_UPLOAD_SECOND:
                    log("UPLOAD_SECOND_SCAN_FILE %s FAILED" % self.__user_no)
                    update_scan_second_failed(self.__ctl_args)

            else :
                self.process_state=kProccessState.kCtlSuccess

            if self.__ctl_status == RemoteControl.CTL_UPLOAD_FIRST:
                log("UPLOAD_FIRST_SCAN_FILE %s OK" % self.__user_no)
            elif self.__ctl_status == RemoteControl.CTL_UPLOAD_SECOND:
                log("UPLOAD_SECOND_SCAN_FILE %s OK" % self.__user_no)
            GLOBAL_REMOTE_CONTROL[seq]['status'] = CommandStatus.NO_TASK
            GLOBAL_REMOTE_CONTROL[seq]['rst'] = rst
        elif cmd is RemoteControl.CTL_UNINSTALL:
            GLOBAL_REMOTE_CONTROL[seq]['status'] = CommandStatus.SUCCESS
            self.client_offline()
            self.process_state=kProccessState.kCtlSuccess
        self.__ctl_status = RemoteControl.CTL_NO_TASK

    def auth(self, text):
        # 接收并解析用户发来的信息，进行身份认证
        self.process_state = kProccessState.kAuthFail
        try:
            if text is None:
                return False
            else:
                if len(text.split('\n')) == 4:
                    user_no, user_pas, user_mac, self.user_addr = text.split('\n')
                else:
                    self.__response = "NEED FOUR ARGUMENTS:userno userpassword usermac userip"
                    return False
        except Exception as error:
            error_log("AUTH FAILED")
            print(error)
            self.__response = "WRONG ARISE ABOUT SOCKET COMMUNICATION"
            return False
        self.__user_no = user_no
        # 检查该用户是否有效(数据库中是否有该用户)
        if not check_user_name(user_no):
            self.__response = "INVALID CLIENT"
            error_log("INVALID CLIENT")
            return False

        # 检查用户名密码是否正确
        if not check_passwd(user_no, user_pas):
            self.__response = "WRONG PASSWD"
            return False

        # 检查用户是否已经注册过
        user_registed = is_user_registed(user_no)
        if user_registed:
            # 判断用户mac信息是否正确
            if identify_usermac(user_no, user_mac):
                log("%s LOGIN" % user_no)
                self.__response = kOK
                self.__response += "\n"
                self.__response += UploadServerConfig
                # 登录成功，保存用户身份
                self.__is_login =True
                self.process_state = kProccessState.kAuthSuccess
                self.insert_user_info()
                return True
            else:
                log("[login filed] userNo [%s] invalid usermac [%s]" % (user_no, user_mac))
                self.__response = "MAC_DIFF"
                return False
        # 当用户尚未注册时，返回登录失败，要求用户提供主机网卡和硬盘序列号信息
        elif not user_registed:
            self.__response = "NEED REGISTER"
            self.process_state = kProccessState.kNeedRegister
            return
        # 用户身份不合法
        self.__response = "INVALID"
        return False

    def register(self, data):
        log("REGISTER ", self.__user_no)
        if register_user(self.__user_no, data):
            self.__response = kOK
            self.__response += '\n'
            self.__response += UploadServerConfig
            self.insert_user_info()
            self.process_state = kProccessState.kAuthSuccess
            self.__is_login = True
            return True
        else:
            self.__response = kFail
            self.process_state = kProccessState.kAuthFail
            return False

    def insert_user_info(self):
        insert_2alive_list(self.__user_no)
        set_user_login(self.__user_no, self.user_addr, 1)

    # 产生要发给客户端的关键字文件
    def make_keywords_file(self, file_type):
        log("%s REQUEST %s" % (self.__user_no, file_type))
        if file_type == "Fullkeywords.txt":
            self.__kw_file = get_keywords(self.__user_no, 1)  # 全盘扫描-关键字的文件名
        elif file_type == "Fastkeywords.txt":
            self.__kw_file = get_keywords(self.__user_no, 2)  # 快速扫描-关键字的文件名
        elif file_type == "Specialkeywords.txt":  # 上线获取-特殊关键字的文件名
            self.__kw_file = get_keywords(self.__user_no, 0)
            mk_keyWords_file(self.__kw_file, self.__user_no)
        elif file_type == "Selfkeywords.txt":  # 个人自查-关键字的文件名
            local_file = get_keywords(self.__user_no, 3)
        else:
            log("error:file_type is None!")
            return kFileState.kFileNameIsNone
        if os.path.exists(self.__kw_file):
            return kFileState.kExisted

    # 根据关键字文件是否已保存在客户端，确定是否发送文件
    def send_keywords_file(self, file_type):
        file_state = self.make_keywords_file(file_type)
        if file_state == kFileState.kExisted:
            self.process_state = kProccessState.kMakeKwSuccess
            self.__response = kOK
        else:
            log("client file %s not existed!" % self.__kw_file)
            self.process_state = kProccessState.kMakeKwFail
            self.__response = kFail

    def hbt(self):
        self.__response = kHbt
        self.process_state = kProccessState.kHbt

    def scan(self, data):
        pass

    def get_addr(self):
        return self.user_addr

    def get_response(self):
        return self.__response

    def client_offline(self):
        log("%s %s OFFLINE" % (self.__user_no, self.user_addr))
        remove_from_alive(self.get_user_no())
        close_conn(self.get_user_no())
        self.process_state = kProccessState.kEndConnecion

    def process_cmd(self, cmd, cmd_info):
        if "RPL" == cmd:
            if self.process_state == kProccessState.kNeedFileHash:
                self.check_upload_existed(cmd_info, self.recv_file_arg)
            elif self.process_state == kProccessState.kNeedFileInfo:
                self.send_upload_num(cmd_info, self.recv_file_arg)
        # 远程控制执行成功，更新状态位
        elif RemoteControl.CTL_RPL_OK == cmd or RemoteControl.CTL_RPL_FAILED == cmd:
            self.update_task_state(cmd, cmd_info)
        elif "ATH" == cmd:
            if self.process_state == kProccessState.kNeedRegister:
                # 注册成功
                self.register(cmd_info)
            else:
                self.auth(cmd_info)
        elif "DNF" == cmd:
            self.send_keywords_file(cmd_info)
        elif "END" == cmd:
            self.client_offline()
        # 记录异常
        elif "LOG" == cmd:
            curt_time = get_curtime()
            record_warnings(cmd_info, self.__user_no, curt_time)
            log(cmd_info, self.__user_no, curt_time)
            self.__response = kOK
        # 接受用户报警文件
        elif "UPD" == cmd:
            self.recv_file_arg = None
            self.current_time = get_curtime()
            self.recv_file(cmd_info)
            # self.__user_socket.end_connection(self.__user_no)
            # 接收用户全盘扫描需要上传的文件
        elif "UPF" == cmd:
            self.recv_file_arg = FIRST_UPLOAD
            self.current_time = get_curtime()
            self.recv_file(cmd_info)

        # 接收用户快速扫描需要上传文件
        elif "UPS" == cmd:
            self.recv_file_arg = SECOND_UPLOAD
            self.current_time = get_curtime()
            self.recv_file(cmd_info)
        elif "INF" == cmd:
            if self.__ctl_status == RemoteControl.CTL_UPLOAD_FIRST:
                self.__response = get_first_upload_file_info(self.__ctl_args)
            elif self.__ctl_status == RemoteControl.CTL_UPLOAD_SECOND:

                self.__response = get_second_upload_file_info(self.__ctl_args)
            self.process_state = kProccessState.kUploadFile
        # 询问服务器时间和服务器过期时间
        elif "TIM" == cmd:
            if "CTM" == cmd_info:
                self.__response = get_curtime()
            elif "EPT" == cmd_info:
                self.__response = get_expired_time()
        # 与客户端保持心跳
        elif "HBT" == cmd:
            self.hbt()
        return self.process_state

    # 接收客户端文件
    def recv_file(self, file_info):
        self.process_state = kProccessState.kRecvFile
        if not os.path.exists(FILE_KEEP_DIR):
            log("MKDIRS ", FILE_KEEP_DIR)
            os.makedirs(FILE_KEEP_DIR)
        # 整合两种文件上传，需要对传入的文件信息进行特别处理
        suffix_pos = file_info.rfind(".")
        if suffix_pos == -1:
            error_log("invalid filename: %s" % file_info)
            return
        if len(file_info.split("\\")) > 1:
            array_file_info = file_info.split("\\")
            self.recv_file_name = array_file_info[len(array_file_info) - 1]
        else:
            self.recv_file_name = file_info
        file_suffix = self.recv_file_name[suffix_pos + 1:]
        self.recv_file_type = MAP_TYPE.get(file_suffix, FILE_TYPE.confidential)
        # self.recv_file_info = file_info
        self.recv_file_path = file_info[0:-4]
        # print("[file_type] : " + str(self.recv_file_type))
        self.process_state = kProccessState.kNeedFileHash


    # 仅当上传文件为 ‘涉密文件’时才检查hash
    # 因为hash保存在数据库中，对于“文件扫描结果”我们不保存它的哈希
    # 只是共用这个传输信道而已
    def check_upload_existed(self, file_hash, args):
        self.process_state = kProccessState.kNeedFileInfo

        self.recv_file_hash = file_hash

        if self.recv_file_type == FILE_TYPE.confidential:
            # 检查当前内容的文件是否已经保存在本地
            check_result = is_hash_here(self.recv_file_hash)
            log("%s UPLOAD %s HASH %s" % (self.__user_no, self.recv_file_name, self.recv_file_hash))
            if check_result:
                # send_info("RPL", , self.__user_no)
                self.__response = "EXISTED"
                log_file_upload(self.__user_no, self.recv_file_name, self.recv_file_hash, self.current_time)
                if args == FIRST_UPLOAD:
                    update_scan_data(self.recv_file_name, self.recv_file_hash, self.recv_file_path)
                elif args == SECOND_UPLOAD:
                    update_second_scan_data(self.recv_file_name, self.recv_file_hash, self.recv_file_path)
                return
        # 通知对方可以发送文件了
        self.__response = "BEGIN"
        # user_socket.send_info("RPL", "BEGIN", user_no)

    def send_upload_num(self, file_info, args):
        # 接收加密文件的 大小、密码
        print("waiting for file_size and file_passwd")
        # tmp = user_socket.get_reply_info()[1]
        file_size, file_passwd = file_info.split()
        file_size = int(file_size)

        # 通知客户端任务编号
        # 客户端通过比对服务器发送的最大任务长度，决定是否进行上传操作
        from trans_file import LAST_TASK_ID
        global LAST_TASK_ID

        erase_zombie_client(UPLOAD_QUEUE, EXECUTING_QUEUE)

        task_id = LAST_TASK_ID + 1
        LAST_TASK_ID = task_id
        executing_count = len(EXECUTING_QUEUE)
        EXECUTING_QUEUE.sort()
        # 添加任务
        if args == FIRST_UPLOAD:
            aes_type = FIRST_UPLOAD
        elif args == SECOND_UPLOAD:
            aes_type = SECOND_UPLOAD
        else:
            aes_type = LOG_UPLOAD
            self.recv_file_path = None
        task = (self.__user_no, self.recv_file_hash, self.recv_file_name, file_size, file_passwd, self.recv_file_type,
                self.current_time, aes_type, self.recv_file_path)
        UPLOAD_QUEUE[task_id] = task

        if len(EXECUTING_QUEUE) < 1:
            max_in_queue = 0
        else:
            max_in_queue = EXECUTING_QUEUE[-1]

        # 通知客户端目前正在处理的任务总数、任务队列中最大序号以及客户端的任务编号（实际上就是上传序号）
        reply_info = "{EXEC_COUNT} {MAX_IN_QUEUE} {TASK_ID}".format(EXEC_COUNT=executing_count,
                                                                    MAX_IN_QUEUE=max_in_queue, TASK_ID=task_id)
        self.__response = reply_info
