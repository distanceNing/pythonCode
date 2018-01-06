#! /usr/bin/python3
def get_sql_settings():
    sql_config = {
        "host": "127.0.0.1",
        "port": 3306,

        "db_name": "safeDb",
        "user": "root",
        "passwd": "xaut.qll",
    }
    return sql_config


if __name__ == '__main__':
    print(get_sql_settings())
