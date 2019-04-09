#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import logging
import os
import sys

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

import time

import requests

from src.config import data_path
from src.utils.jd_bean_api import query_shop_gift, query_shop_active
from src.utils.utils import update_session_cookies


class Shop:
    def __init__(self, vender_id, shop_id, shop_name):
        self.shop_name = shop_name
        self.vender_id = vender_id
        self.shop_id = shop_id
        self.shop_url = "https://wqshop.jd.com/mshop/gethomepage?venderid=" + self.vender_id
        self.session = requests.session()
        self.logger = logging

    def run(self):
        update_session_cookies(self.session, data_path / "cookies.json")

        query_shop_gift(self.session, self.vender_id)
        time.sleep(0.5)

        query_shop_active(self.session, self.vender_id)
        time.sleep(0.5)

        # query_shop_sign_draw(self.session, self.vender_id)
        # time.sleep(0.5)


if __name__ == '__main__':
    log_format = '%(asctime)s %(name)s[%(module)s] %(levelname)s: %(message)s'
    # logging.basicConfig(filename=log_path, format=log_format, level=logging.INFO)
    logging.basicConfig(format=log_format, level=logging.INFO)

    try:
        Shop('1000088181', '1000088181', '闪亮京东自营官方旗舰店').run()
        # db_path = data_path / "shop.db"
        # conn = sqlite3.connect(str(db_path))
        #
        # cur = conn.cursor()
        # # cur.execute("select * from shop")
        # cur.execute("select venderId from shop")
        # shop_list = cur.fetchall()

        # for shop in shop_list:
        #     Shop(shop[2], shop[3], shop[1]).run()

        # session = requests.Session()
        # update_session_cookies(session, data_path / "cookies.json")
        #
        # shop_list = ['1000000284','1000000313','1000000314','1000000450','1000000691']
        # batch_query_shop_fav_gift(session, shop_list)


    except Exception:
        logging.exception(sys.exc_info())
