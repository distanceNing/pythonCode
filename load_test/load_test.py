from twisted.internet import reactor
from user_protocol import EchoFactory

kPort = 8000

if __name__ == '__main__':
    print("echo server")
    reactor.listenTCP(kPort, EchoFactory())
    reactor.run()
