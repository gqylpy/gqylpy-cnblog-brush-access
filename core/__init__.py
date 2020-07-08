import sys
import uuid
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from concurrent.futures import ThreadPoolExecutor

from tools import db
from tools import gen_path
from tools import exec_sql

from config import DB_DIR
from config import POOL_SIZE

_thread_pool = ThreadPoolExecutor(POOL_SIZE)

_ua = 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)'

if sys.platform == 'win32':
    _chromedriver = gen_path(DB_DIR, 'chromedriver_windows')
elif sys.platform == 'darwin':
    _chromedriver = gen_path(DB_DIR, 'chromedriver_mac')
else:
    raise BaseException('Unknown system')

_cnt = 0

def fetch_data() -> tuple:
    return exec_sql(f'''
        SELECT link 
        FROM archive_cnblog
        WHERE uid IN (
          SELECT id 
          FROM user_cnblog 
          WHERE is_ok IS TRUE)
        ORDER BY id DESC
    ''', database=db.gqylpy)


def open_chrome(chromedrive_file: str) -> Chrome:
    chrome_options = Options()

    # 禁止加载图片
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    # 隐藏浏览器
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')

    # Set UA
    chrome_options.add_argument(f'user-agent="{_ua + str(uuid.uuid4())}"')

    return Chrome(chromedrive_file, chrome_options=chrome_options)


def async_task(data: tuple, chromedriver_file: str):
    bro: Chrome
    global _cnt

    try:
        bro = open_chrome(chromedriver_file)
        bro.set_page_load_timeout(30)

        for link, in data:
            try:
                bro.get(link)
                # bro.execute_script(f'window.open("{link}");')
            except TimeoutException:
                ...

    finally:
        bro.quit()

    _cnt += 1
    print(_cnt)


def main():
    while True:
        async_task(fetch_data(), _chromedriver)

        # _thread_pool.submit(
        #     async_task,
        #     fetch_data(),
        #     _chromedriver
        # )
