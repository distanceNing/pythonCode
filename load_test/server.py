from threading import Thread
import ssl

from twisted.internet import reactor,ssl
from twisted.internet.protocol import Factory

from BLL.close_conn import close_all_conn
from assign_task import socket_method
from common import CommandStatus
from mylog import log
from remote.remote_control import remote_event_loop, GLOBAL_REMOTE_CONTROL
from trans_file import UploadQueue
from user_protocol import UserProtocol

kPort = 50005


class UserProtocolFactory(Factory):
    def __init__(self, app):
        self.the_app = app

    def buildProtocol(self, addr):
        return UserProtocol(self, addr)

    def add_client(self, user_no, client_protocol):
        self.the_app.add_client(user_no, client_protocol)

    def delete_client(self, user_no):
        self.the_app.delete_client(user_no)


class Server:
    def __init__(self):
        self.online_clients = {}
        self.protocol_factory = UserProtocolFactory(self)

    def add_client(self, user_no, client_protocol):
        self.online_clients[user_no] = client_protocol

    def delete_client(self, user_no):
        if self.online_clients.get(user_no) is not None:
            self.online_clients.pop(user_no)

    def check_remote_task(self):
        #user_list = self.online_clients.keys()
        # 向客户端派遣远程控制任务
        invaild_clients = []
        for seq in self.online_clients.keys():
            # 非法客户标识
            user_protocol = self.online_clients[seq]
            if user_protocol.is_timeout():
                invaild_clients.append(seq)
                continue
            if GLOBAL_REMOTE_CONTROL.get(seq) is None:
                continue
            # 当前没有任务
            if GLOBAL_REMOTE_CONTROL[seq]['status'] is CommandStatus.NO_TASK:
                continue
            elif GLOBAL_REMOTE_CONTROL[seq]['status'] is CommandStatus.NEW_TASK:
                log("[%s] I get a task" % seq)
                cmd = GLOBAL_REMOTE_CONTROL[seq]['cmd']
                # 统一提取任务参数
                args = GLOBAL_REMOTE_CONTROL[seq]['args']
                user_protocol.ctl_client(cmd, args)
        for user in invaild_clients:
            self.online_clients[user].end_connection()
        # 每5秒检查一次web端是否有下发命令，客户端是否掉线
        reactor.callLater(5, self.check_remote_task)

    def run(self):
        log("SERVER UP")
        # 接受Web控制指令
        Thread(target=socket_method().run, daemon=True).start()

        # 处理远程任务，包括任务的状态和提交结果
        Thread(target=remote_event_loop, daemon=True).start()

        sslContext = ssl.DefaultOpenSSLContextFactory(
            'CA/key.pem',  # 私钥
            'CA/cert.pem',  # 公钥
        )

        # 处理文件异步上传
        UploadQueue().start()

        # 服务启动时，初始化所有用户状态---未登录
        close_all_conn()
        # 监听服务
        reactor.listenSSL(kPort, self.protocol_factory, sslContext)
        reactor.callWhenRunning(self.check_remote_task)
        #reactor.listenTCP(kPort, self.protocol_factory)
        reactor.run()
