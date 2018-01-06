from threading import Thread

from twisted.internet import reactor
from twisted.internet.protocol import Factory

from BLL.close_conn import close_all_conn
from assign_task import socket_method
from mylog import log
from remote.remote_control import remote_event_loop
from trans_file import UploadQueue
from user_protocol import UserProtocol

kPort = 8000


class EchoFactory(Factory):
    def __init__(self):
        self.clients = []

    @property
    def get_user_num(self):
        return self.clients.__len__()

    def buildProtocol(self, addr):
        return UserProtocol(self, addr)

    def add_client(self, client_protocol):
        self.clients.append(client_protocol)

    def delete_client(self, client_protocol):
        self.clients.remove(client_protocol)


class App:
    def __init__(self):
        self.clients = []
        self.protocol_factory = EchoFactory()

    def append_client(self):
        pass

    def run(self):
        print("echo server")
        log("SERVER UP")
        # 接受Web控制指令
        Thread(target=socket_method().run, daemon=True).start()

        # 处理远程任务，包括任务的状态和提交结果
        Thread(target=remote_event_loop, daemon=True).start()

        # 处理文件异步上传
        UploadQueue().start()

        # 服务启动时，初始化所有用户状态---未登录
        close_all_conn()
        # 监听服务
        reactor.listenTCP(kPort, self.protocol_factory)
        reactor.run()
