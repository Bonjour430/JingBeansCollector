#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import logging
import os
import sys
from time import sleep

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

import requests
from urllib3.exceptions import InsecureRequestWarning

from src.config import ua_baidu, data_path, config
from src.login import JD_Auto_Login
from src.pet_dog import PetDog
from src.plant_bean import PlantBean
from src.shop_spider import DailyShopSpider
from src.utils.utils import readCookies


def main():
    while True:
        # schedule.run_pending()
        # sleep(1)

        JD_Auto_Login().auto_login()
        sleep(2)

        # UserSign().start()
        # sleep(2)

        DailyShopSpider().start()
        sleep(3)

        PlantBean().start()
        sleep(3)

        PetDog().start()

        sleep(150 * 60)


def make_session() -> requests.Session:
    session = requests.Session()

    session.headers.update({
        'User-Agent': ua_baidu
    })

    data_file = data_path / 'cookies.json'

    if data_file.exists():
        try:
            # selenium 登录的cookies 转 requests 的cookies
            selenium_cookies = readCookies(data_file)
            requests_cookies = {}
            for cookie in selenium_cookies:
                requests_cookies[cookie['name']] = cookie['value']

            requests.utils.add_dict_to_cookiejar(session.cookies, requests_cookies)
            logging.info('# load cookies from file success.')
        except Exception as e:
            logging.info('# can not load cookies from file, try again~' + e)

    return session


def proxy_patch():
    """
    Requests 似乎不能使用系统的证书系统, 方便起见, 不验证 HTTPS 证书, 便于使用代理工具进行网络调试...
    http://docs.python-requests.org/en/master/user/advanced/#ca-certificates
    """
    import warnings
    # from requests.packages.urllib3.exceptions import InsecureRequestWarning

    class XSession(requests.Session):
        def __init__(self):
            super().__init__()
            self.verify = False

    requests.Session = XSession
    warnings.simplefilter('ignore', InsecureRequestWarning)


if __name__ == '__main__':
    if config.debug and os.getenv('HTTPS_PROXY'):
        proxy_patch()

    main()
