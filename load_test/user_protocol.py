import struct
from enum import Enum

from twisted.internet.protocol import Protocol
# from twisted.internet.interfaces import IAddress
from client import Client

HEAD_FORMAT = "!3sI"


class kProccessState(Enum):
    kHbt = 1
    kAuth = 2
    kScan = 3


# 这个类类似于muduo中的TcpConnection
class UserProtocol(Protocol):
    def __init__(self, factory, addr):
        self.factory = factory
        self.client = Client(addr)
        self.process_state = kProccessState.kHbt

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

    # clientReadCallBack()
    def dataReceived(self, data):
        # As soon as any data is received, write it back
        print("recv data is ")
        print(data)

        # self.transport.write(data)
        # 定义一个状态机来做协议解析
        cmd, cmd_info = self.do_parse_request(data)

        # 协议处理后交给Client来做具体的请求处理
        self.client.process_cmd(cmd, cmd_info)

    def do_parse_request(self, recv_data):
        # parse request
        rpl = None
        rest_pkt_size = None
        recv_data_len = len(recv_data)
        try:
            rpl, rest_pkt_size = struct.unpack(HEAD_FORMAT, recv_data[:7])
        except Exception as error:
            print(error)
        cmd = rpl.decode()
        cmd_info = recv_data[7:7 + rest_pkt_size]
        return cmd, cmd_info

    def is_connected(self):
        return self.transport.connected

    def get_user_ip(self):
        return self.client.addr
