# -*- coding:utf-8 -*-

import socket
import struct
from remote.remote_control import assign_remote_task, get_task_result
from remote.config import RemoteControl as CMD_TYPE
from config import CONTROL_HOST, CONTROL_PORT
from mylog import log

HOST = CONTROL_HOST
PORT = CONTROL_PORT


def oprate_data(method, thing, data):  # 处理ip_list
    if data.find('|') > 0:
        data_list = data.split("|")[0:-1]
    else:
        data_list = [data]
    ret = ""
    # 按照用户编号，分配“获取用户网络进程命令”
    if method == "GET" and thing == "PORT":
        for userNo in data_list:
            # print(ret_port)
            assign_remote_task(userNo, CMD_TYPE.CTL_PROCESS_LIST)
        # 获取当前部门所有在线主机运行的网络进程
        for userNo in data_list:
            record = userNo + ',' + get_task_result(userNo) + "|"
            ret += record
        log("[REMOTE RESULT]", ret)
        # return ret_port
    elif method == "CLOSE" and thing == "PORT":
        for i in data_list:
            tmp = i.split(",")
            userNo = tmp[0]
            program = [x for x in tmp[1:] if len(x) > 1]
            print("Program:", program)  # 客户端处理program
            assign_remote_task(userNo, CMD_TYPE.CTL_KILL_PROCESS, program)
            ret = "OK"
    elif method == "CLOSE" and thing == "NET":
        ret = "OK"
        log("[CONTRL-CLOSE-NET]")
        for userNo in data_list:
            assign_remote_task(userNo, CMD_TYPE.CTL_SHUT_NETWORK, "SHUT")
            log("SHUTDOWN NETWORK FOR ", userNo)
    elif method == "OPEN" and thing == "NET":
        ret = "OK"
        log("[CONTRL-OPEN-NET]")
        for userNo in data_list:
            log("OPEN NETWORK FOR ", userNo)
            assign_remote_task(userNo, CMD_TYPE.CTL_SHUT_NETWORK, "OPEN")
    elif method == "REMOVE" and thing == "SELF":
        ret = "OK"
        for userNo in data_list:
            log("UNINSTALL APP FROM %s " % userNo)
            is_ok = assign_remote_task(userNo, CMD_TYPE.CTL_UNINSTALL)
            if not is_ok:
                ret = "FAILED"
    return ret


# 远程控制--->扫描用户全盘文件
def oprate_data_sacnf(method, thing, userNo):
    ret = {True: "OK", False: "FAILED"}
    is_ok = False

    if thing == "FILE":
        is_ok = assign_remote_task(userNo, CMD_TYPE.CTL_SCAN_FILES)
    elif thing == "SELF":
        is_ok = assign_remote_task(userNo, CMD_TYPE.CTL_SCAN_SELF)
    elif thing == "SECOND":
        is_ok = assign_remote_task(userNo, CMD_TYPE.CTL_SCAN_SECOND, "SECOND")

    return ret[is_ok]


# 远程控制--->卸载客户端
def oprate_client_uninstall(method, thing, userNo):
    if method == "REMOVE" and thing == "SELF":
        ret = "OK"
        assign_remote_task(userNo, CMD_TYPE.CTL_UNINSTALL, "CLIENT-UNINSTALL")

    return ret


# 远程控制--->上传扫描文件
def oprate_data_upload(method, thing, data):
    userNo = data.split("|")[1]
    uploadId = data.split("|")[0]
    ret = {True: "OK", False: "FAILED"}
    is_ok = False
    if thing == "FILE1":
        is_ok = assign_remote_task(userNo, CMD_TYPE.CTL_UPLOAD_FIRST, uploadId)
    elif thing == "FILE2":
        is_ok = assign_remote_task(userNo, CMD_TYPE.CTL_UPLOAD_SECOND, uploadId)
    return ret[is_ok]


class socket_method:
    def __init__(self):
        self.socket = self.init_socket()
        self.inputs = [self.socket]
        self.outputs = []

    def init_socket(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen(10)
        log("WebProxy Listened at %s:%d" % (HOST, PORT))
        return server_socket

    def recv_data(self, sock):
        bite = False
        s = struct.calcsize("I")
        try:
            length, = struct.unpack("I", sock.recv(s))
            bite = sock.recv(length)
        except:
            print("not data recv")
        finally:
            return bite

    def get_data(self, info):
        frm = "10s10sI950s"
        method, thing, size, data = struct.unpack(frm, info)
        method = method.decode("utf-8").strip("\0")
        thing = thing.decode("utf-8").strip("\0")
        data = data.decode("utf-8").strip("\0")
        if len(data) - size != 0:
            return False

        return method, thing, data

    def set_values(self, method, thing, data=""):
        values = (method.encode("utf-8"), thing.encode("utf-8"), len(data), data.encode("utf-8"))
        return values

    def pack_messages(self, values):
        frm = "I10s10sI950s"
        length = struct.calcsize(frm)
        pack_data = struct.pack(frm, length, *values)
        return pack_data

    def send_data(self, method, thing, conn, data):
        values = self.set_values(method, thing, data)
        data = self.pack_messages(values)
        conn.send(data)

    def close_conn(self, conn, adress):
        conn.close()

    def run(self):
        if not self.socket:
            return False

        while 1:
            conn, address = self.socket.accept()

            while 1:
                length = self.recv_data(conn)

                if length and length != 0:
                    method, thing, data = self.get_data(length)
                    if method == "GET" and thing == "PORT":
                        if data == "OK":
                            self.send_data(method, thing, conn, "OK")
                            break
                        else:
                            data = oprate_data(method, thing, data)
                            self.send_data(method, thing, conn, data)

                    elif method == "CLOSE" and thing == "PORT":
                        if data == "OK":
                            self.send_data(method, thing, conn, data)
                            break
                        else:
                            data = oprate_data(method, thing, data)
                            self.send_data(method, thing, conn, data)
                    elif method == "CLOSE" and thing == "NET":
                        if data == "OK":
                            self.send_data(method, thing, conn, data)
                            break
                        else:
                            data = oprate_data(method, thing, data)
                            self.send_data(method, thing, conn, data)

                    elif method == "OPEN" and thing == "NET":
                        if data == "OK":
                            self.send_data(method, thing, conn, data)
                            break
                        else:
                            data = oprate_data(method, thing, data)
                            self.send_data(method, thing, conn, data)

                    elif method == "SCAN":
                        if data == "OK":
                            self.send_data(method, thing, conn, data)
                            break
                        else:
                            data = oprate_data_sacnf(method, thing, data)
                            self.send_data(method, thing, conn, data)
                    elif method == "REMOVE" and thing == "SELF":
                        if data == "OK":
                            self.send_data(method, thing, conn, data)
                            break
                        else:
                            data = oprate_data(method, thing, data)
                            self.send_data(method, thing, conn, data)
                    elif method == "UPLOAD":
                        if data == "OK":
                            self.send_data(method, thing, conn, data)
                            break
                        else:
                            data = oprate_data_upload(method, thing, data)
                            self.send_data(method, thing, conn, data)

                else:
                    break

            self.close_conn(conn, address)


if __name__ == '__main__':
    sock = socket_method()
    sock.run()
