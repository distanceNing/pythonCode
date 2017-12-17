from twisted.internet.protocol import Protocol, Factory
# from twisted.internet.interfaces import IAddress
from client import Client


# 这个类类似于muduo中的TcpConnection
class UserProtocol(Protocol):
    def __init__(self, factory, addr):
        self.factory = factory
        self.client = Client(addr)

    # 当一个客户端连接到来的时候
    # newConnectionCallBack()

    def connectionMade(self):
        print("new connection client num is ")
        self.factory.add_client(self)
        print(self.factory.get_user_num)

    # 当一个客户端连接关闭的时候
    # clientCloseCallBack()

    def connectionLost(self, reason):
        print("a connection closed")
        self.factory.delete_client(self)
        print(self.factory.get_user_num)

    # 定义一个状态机来做协议处理，协议处理后交给Client来做具体的请求处理
    def do_parse_request(self):
        # parse request
        cmd = 1
        cmd_info = "aaa"
        self.client.process_cmd(cmd, cmd_info)

    # clientReadCallBack()
    def dataReceived(self, data):
        # As soon as any data is received, write it back
        print("recv data is ")
        print(data)
        self.transport.write(data)

    def is_connected(self):
        return self.transport.connected

    def get_user_ip(self):
        return self.client.addr


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
