# 所有的客户端上传文件将会被统一处理
# 而不是在为‘每个客户端分配的线程内部处理’
# 以此基础，实现文件异步传输、网络流量控制
import os
import socket
import threading
from common import FILE_KEEP_DIR, MAX_PACKET_SIZE,\
    pro_local_file_name, set_file_inf, log_file_upload, update_scan_data, update_second_scan_data
from config import FILE_TYPE, UPLOAD_HOST, UPLOAD_PORT, MAX_UPLOAD_TASK
from mylog import xtrace, log, error_log
from remote.parse_scan_data import parse_scan_items
from remote.remote_control import is_user_logined
from remote.remote_control import set_ok_results, set_failed_results

LAST_TASK_ID = 0
UPLOAD_QUEUE = dict()
EXECUTING_QUEUE = []

LOG_UPLOAD = 0
FIRST_UPLOAD = 1
SECOND_UPLOAD = 2

def erase_zombie_client(task_queue, exec_tasks):
    delta = []

    # 如果该任务对应的用户名已经掉线
    for task_id, task in task_queue.items():
        user_no = task[0]
        if not is_user_logined(user_no):
            delta.append(task_id)

    for task_id in delta:
        if task_id in task_queue:
            log("delete task_queue {TASK_ID}".format(TASK_ID=task_id))
            task_queue.pop(task_id)
        if task_id in exec_tasks:
            log("delete exec_tasks {TASK_ID}".format(TASK_ID=task_id))
            exec_tasks.remove(task_id)

    return True


def download_file(sock, seq):
    user_no, file_hash, file_name, file_size, file_passwd, file_type, current_time, aes_status, file_path = UPLOAD_QUEUE.get(seq)

    ori_file_name = file_name
    # 针对涉密文件，我们统一命名
    if file_type != FILE_TYPE.scan_data:
        file_name = pro_local_file_name(file_name)

    # 本地文件统一保存路径
    file_local_path = os.path.join(FILE_KEEP_DIR, file_name)

    rest_size = file_size

    xtrace("Begin Receive [%s %d]" % (file_name, file_size))
    xtrace("%s %s %s bytes passwd: [%s]" % (user_no, file_local_path, file_size, file_passwd))

    # 接收文件
    fp = open(file_local_path, "wb")
    while rest_size:
        buf = sock.recv(MAX_PACKET_SIZE)
        rest_size -= len(buf)
        fp.write(buf)
    fp.close()

    log("UPLOAD %s finished" % ori_file_name)

    # 仅当上传文件为 ‘涉密文件’时才记录此次上传操作
    if file_type == FILE_TYPE.confidential:
        set_file_inf(file_hash, FILE_KEEP_DIR, file_name, file_size, file_passwd)
        log_file_upload(user_no, ori_file_name, file_hash, current_time)
        if aes_status == FIRST_UPLOAD:
            update_scan_data(file_name, file_hash, file_path)
        elif aes_status == SECOND_UPLOAD:
            update_second_scan_data(file_name, file_hash, file_path)

    elif file_type == FILE_TYPE.scan_data:
        print("BEGIN PARSE SCAN_DATA")
        match_dict = {}
        if parse_scan_items(match_dict, file_local_path):
            set_ok_results(user_no, match_dict)
        else:
            set_failed_results(user_no, None)

    # 从任务队列中取消该任务
    xtrace("thread finished")

    # 取消"正在执行"任务记录
    EXECUTING_QUEUE.remove(seq)
    # 删除该任务
    UPLOAD_QUEUE.pop(seq)
    return True





# UploadQueue
class UploadQueue(threading.Thread):

    def __init__(self):
        super().__init__()
        self.sock = self.init_sock()
        self.client_info = {}

    @staticmethod
    def init_sock():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((UPLOAD_HOST, UPLOAD_PORT))
        sock.listen(MAX_UPLOAD_TASK)

        log("UploadThread listening %s:%d" % (UPLOAD_HOST, UPLOAD_PORT))
        return sock

    def run(self):
        while True:
            client_fd, (clnt_addr, clnt_port) = self.sock.accept()
            log("get connection from %s:%d" % (clnt_addr, clnt_port))
            # if len(self.client_info) <= MAX_UPLOAD_TASK:
            # 以IP地址为键，sockfd 为值，保存已经建立连接的客户端

            # 客户端报告自己的`任务编号`
            try:
                seq = client_fd.recv(8).decode()
                seq = int(seq)
                task = UPLOAD_QUEUE.get(seq, 0)
            except Exception:
                client_fd.send("-1".encode())
                client_fd.close()
                continue               

            if seq <= 0:
                # invalid task_id
                error_log("invalid task_id [%d]" % seq)
                client_fd.send("-1".encode())
                client_fd.close()
                continue

            exec_task_count = len(EXECUTING_QUEUE)

            # 根据`任务编号`没有找到任务，直接断开连接
            if not isinstance(task, tuple):
                log("failed to get upload task for [%d]" % seq)
                # NO TASK FOUND
                client_fd.send("-2".encode())
                client_fd.close()
                continue

            # 返回还需等待的任务总数，0 表示不需要等待，可以上传了
            if exec_task_count >= MAX_UPLOAD_TASK:
                EXECUTING_QUEUE.sort()
                wait_tasks = seq - EXECUTING_QUEUE[-1]
                if wait_tasks < 0:
                    wait_tasks = 0
                client_fd.send(str(wait_tasks))
            else:
                client_fd.send('0'.encode())
                EXECUTING_QUEUE.append(seq)
                tk = threading.Thread(target=download_file, args=(client_fd, seq))
                # 设置该属性后，则不必处理‘线程回收’工作
                tk.setDaemon(True)
                tk.start()

