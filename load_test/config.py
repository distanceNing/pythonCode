from default_config import get_sql_settings
from collections import namedtuple
import os

sql_config = None
sql_config = get_sql_settings()

account = str(os.getenv("DB_ACCOUNT"))
passwd = str(os.getenv("DB_PASSWD"))
host = str(os.getenv("DB_HOST"))


# sql_config['host'] = '114.215.19.63'
# 手动实现 Enum
def enum(*keys):
    return namedtuple('Enum', keys)(*range(len(keys)))


CONTROL_HOST = '0.0.0.0'
CONTROL_PORT = 50006

UPLOAD_HOST = '0.0.0.0'
UPLOAD_PORT = 50007
MAX_UPLOAD_TASK = 3

UploadServerConfig = "{IP} {PORT} {LIMIT}".format(IP="114.215.19.63", PORT=UPLOAD_PORT, LIMIT=MAX_UPLOAD_TASK)

# 定义上传文件类型
# 分别为 ‘涉密文件’、‘用户自查的扫描结果文件’， ‘远程扫描的结果文件’
FILE_TYPE = enum('confidential', 'scan_data')
MAP_TYPE = {
    "aes": FILE_TYPE.confidential,
    "rlog": FILE_TYPE.scan_data,
}

if __name__ == "__main__":
    print(sql_config)
