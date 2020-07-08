import time
import datetime

from tools import exec_sql


def fetch_all_archive():
    return exec_sql(f'''
        SELECT id 
        FROM archive_cnblog
        WHERE create_date > '2019-08-19 00:00:00'
    ''')


print(fetch_all_archive()[0])
print(len(fetch_all_archive()) / 4)
