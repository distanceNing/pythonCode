# -*- coding:utf-8 -*-

import os
import time

from mylog import error_log, log

ISOTIMEFORMAT = '%Y-%m-%d %X'


# rec 接收一个扫描结果的字典
# 打包为一个结果列表
def parse_scan_files(data_dict):
    if data_dict is None:
        return None
    data = []
    scan_time = time.strftime(ISOTIMEFORMAT, time.localtime())

    for file_path, (keywords, context) in data_dict.items():
        if file_path.find('\\') > 0:
            file_path = file_path.replace('\\', '/')
        file_name = file_path.rsplit('/', 1)[-1]
        data.append([file_name, file_path, scan_time, keywords, context])
    return data


def parse_scan_items(match_dict, file_name):
    if not isinstance(match_dict, dict):
        error_log("[MISMATCH ARGS]")
        return False

    if file_name is None or not os.path.exists(file_name):
        error_log("[%s] not exists" % file_name)
        return False

    _data = open(file_name, "rb").read().decode(errors='replace')

    details = [_line.strip() for _line in _data.split('\n') if len(_line.strip()) != 0]

    if len(details) < 1:
        error_log("EMPTY SCAN LOG")
    elif len(details) == 1 and details[0] == 'EMPTY':
        log("CLIENT IS CLEAN")
        return True

    # 开始解析扫描结果
    for line in details:
        # ignore empty line
        if len(line) < 3:
            continue
        try:
            path, match, key_extend = line.strip().split('|')
            # print("path:%s match: %s key_extend: %s" % (path, match, key_extend))
            match_dict[path] = (match, key_extend)
        except Exception as error:
            error_log("ERROR PARSE SCAN_ITEMS")
            print(error)
    return True
