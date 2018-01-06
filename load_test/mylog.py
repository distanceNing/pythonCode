import inspect
import time

DEBUG = True

TRACE_FOPMAT = "[{TIME}] DEBUG {OUT}"
ERROR_LOG_FOPMAT = "[{TIME}] *ERROR* {FILENAME} {FUNC} {LINE} {OUT}"
LOG_FOPMAT = "[{TIME}] {OUT}"
SOCKET_IN  = "SOCKET<=="
SOCKET_OUT = "SOCKET==>"

if DEBUG:
    LOG_FOPMAT = "[{TIME}] EVENT {OUT}"


def get_curtime():
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))


def error_log(*args):
    cur_time = get_curtime()
    output = ''.join(args).replace('\n', ' ')

    callerframerecord = inspect.stack()[1]
    record = callerframerecord[0]
    frame = inspect.getframeinfo(record)
    print(ERROR_LOG_FOPMAT.format(TIME=cur_time, OUT=output, \
        FILENAME=frame.filename, FUNC=frame.function, LINE=frame.lineno))


def log(*args):
    """

    :rtype:
    """
    cur_time = get_curtime()
    output = ''.join(args).replace('\n', ' ')
    print(LOG_FOPMAT.format(TIME=cur_time, OUT=output))


def xtrace(*args):
    if not DEBUG:
        return
    cur_time = get_curtime()
    output = ''.join(args).replace('\n', ' ')
    print(TRACE_FOPMAT.format(TIME=cur_time, OUT=output))
