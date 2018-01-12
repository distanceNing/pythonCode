from app import App

import signal

from twisted.internet import reactor

def kill_myself(signum,frame):
    from sys import platform
    from os import system, getpid

    #kill_str = {
    #    'linux': "kill -9 {PID}",
    #    'win32': "taskkill /f /pid {PID}"
    #}
    #shut_myself = kill_str[platform].format(getpid())
    pid = getpid()
    shut_myself="kill -9 "+ str(pid)
    system(shut_myself)
    reactor.stop()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, kill_myself)
    signal.signal(signal.SIGTERM, kill_myself)
    # 加载配置文件
    the_app = App()
    the_app.run()
