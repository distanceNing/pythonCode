from twisted.internet import reactor
from twisted.internet.protocol import Factory

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
        reactor.listenTCP(kPort, self.protocol_factory)
        reactor.run()
