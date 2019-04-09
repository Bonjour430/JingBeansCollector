#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import json
import logging
import os
import re
import sqlite3
import sys

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

import threading
from datetime import date
from pathlib import Path
from urllib.parse import splitquery, parse_qs

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from src.config import data_path
from src.utils.utils import findElement, writeCookies, update_chrome_cookies

re_jd_login_url = re.compile(
    r'^http[s]?://plogin.m.jd.com/user/login.action$|^http[s]?://xui.ptlogin2.qq.com/cgi-bin/xlogin$')
re_shop_url = re.compile(r"^http[s]?://shop.m.jd.com/$|^http[s]://wqshop.jd.com/mshop/gethomepage$")
re_shop_fav_url = re.compile(r"^http[s]?://wqs.jd.com/my/fav/shop_fav.shtml$")
re_shop_draw_url = re.compile(r"^http[s]?://shop.m.jd.com/mshop/shopdraw$")

db_name = 'shop.db'
table_name = 'shop'

statics_shimo_url = [
    "https://shimo.im/docs/Qorff3s6T0Uvv8aU/read",
    "https://shimo.im/docs/Dncd9hIv17cxnhfm/read",
    "https://shimo.im/docs/b4LMFBapNUMp07ym/read",
    "https://shimo.im/docs/1o95sS2ghEIcX81S/read"
]


class DailyShopSpider(threading.Thread):

    def __init__(self):
        super(DailyShopSpider, self).__init__(name='Shop-Spider')
        self.url = "https://shimo.im/docs/Qorff3s6T0Uvv8aU/read"
        self.logger = logging

        path = data_path / str(date.today())
        if not path.exists():
            Path.mkdir(path, parents=True)

        self.short_links_path = path / "short_links.json"
        self.short_url_total = {}
        self.short_url_new = {}

        self.shop_info_path = path / "shop_info.json"
        self.shop_total = {}
        self.shop_new = {}

        self.conn = None
        self.cur = None

    def init_db(self):
        try:
            db_path = data_path / db_name
            self.conn = sqlite3.connect(str(db_path))
            create_table_sql = "CREATE TABLE IF NOT EXISTS shop(id integer primary key autoincrement,shopName varchar(255),venderId varchar(32) unique NOT NULL,shopId varchar(32) unique,shopUrl varchar(255))"
            # self.conn.execute(create_table_sql)
            self.cur = self.conn.cursor()
            self.cur.execute(create_table_sql)
            self.conn.commit()

        except Exception:
            self.logger.exception(sys.exc_info())

    def init_browser(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Linux; Android 8.1.0; CLT-AL00 Build/HUAWEICLT-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/63.0.3239.83 Mobile Safari/537.36 T7/10.13 baiduboxapp/10.13.0.10 (Baidu; P1 8.1.0)")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        # add_extension 添加浏览器扩展
        # chrome_options.add_extension('d:\crx\AdBlock_v2.17.crx')  # 自己下载的crx路径

        prefs = {}
        # 设置这两个参数就可以避免密码提示框的弹出
        prefs["credentials_enable_service"] = False
        prefs["profile.password_manager_enabled"] = False
        # 禁止图片加载
        # prefs["profile.managed_default_content_settings.images"] = 2

        chrome_options.add_experimental_option("prefs", prefs)

        self.browser = webdriver.Chrome(options=chrome_options)
        self.browser.set_page_load_timeout(60)
        self.browser.implicitly_wait(10)

        update_chrome_cookies(self.browser, data_path / "cookies.json")

    def run(self):
        self.logger.info("{} start...".format(self.name))

        self.init_browser()
        self.init_db()

        if self.short_links_path.exists():
            with open(self.short_links_path, 'r') as f:
                self.short_url_total = json.load(f)
                self.logger.info(
                    "collect {} short links at last time, detail:{}".format(str(len(self.short_url_total)), str(self.short_url_total)))

        if self.shop_info_path.exists():
            with open(self.shop_info_path, "r") as f:
                self.shop_total = json.load(f)
                self.logger.info("collect {} shops at last time,detail: {}".format(str(len(self.shop_total)), str(self.shop_total)))

        collected_urls = self.collect_short_links(self.url)
        if len(collected_urls) == 0:
            self.logger.info("no short links collected this time...")
            return

        for key, value in collected_urls.items():
            if not self.short_url_total.get(key):
                self.short_url_new[key] = value

        for key, value in self.short_url_new.items():
            self.short_url_total[key] = value

        self.logger.info("collect {} short links at this time,total short links:{}".format(str(len(self.short_url_new)), str(len(self.short_url_total))))

        for link in self.short_url_new:
            self.collect_shop_info(link)

        self.logger.info("collect {} shops at this time, total shops:{}".format(str(len(self.shop_new)), str(len(self.shop_total))))

        with open(self.short_links_path, "w") as f:
            json.dump(self.short_url_total, f, indent=4)

        with open(self.shop_info_path, "w") as f:
            json.dump(self.shop_total, f, indent=4, ensure_ascii=False)

        writeCookies(self.browser.get_cookies(), data_path / 'cookies.json')
        self.browser.quit()

    def get_html(self, url):
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            # 这里我们知道百度贴吧的编码是utf-8，所以手动设置的。爬去其他的页面时建议使用：
            # r.encoding = r.apparent_encoding
            # r.encoding = 'utf-8'
            return r.text
        except Exception:
            self.logger.exception(sys.exc_info())

            return None

    def collect_short_links(self, url):
        short_links = {}
        try:
            html = self.get_html(url)
            if html:
                soup = BeautifulSoup(html, 'lxml')
                ql_editor = soup.find_all('div', attrs={'class': "ql-editor"})[0]
                for a in ql_editor.find_all('a', attrs={'class': 'ql-link'}):
                    short_links[a['href']] = 1
        except:
            self.logger.exception(sys.exc_info())

        return short_links

    def collect_shop_info(self, short_link):
        try:
            self.browser.get(short_link)

            title = self.browser.title.title()
            long_link = self.browser.current_url

            self.logger.info(title + " : " + long_link)

            if long_link is None or len(long_link) <= 0:
                return None

            path_part, param_part = splitquery(long_link)
            params = parse_qs(param_part) if param_part else None
            if re.match(re_jd_login_url, path_part):
                self.logger.error("please login first...")
                # JD_Auto_Login().auto_login()
                # time.sleep(1)
                #
                # update_chrome_cookies(worker_browser)
                # time.sleep(3)
            if re.match(re_shop_url, path_part):
                shop_name = self.browser.title.title()

                shop_id_element = findElement(self.browser, (By.XPATH, "//*[@id=\"searchform\"]/input[2]"))
                shop_id = shop_id_element.get_attribute("value") if shop_id_element else ""

                vender_id_element = findElement(self.browser, (By.XPATH, "//*[@id=\"searchform\"]/input[3]"))
                vender_id = vender_id_element.get_attribute("value") if vender_id_element else ""

                shop_url = "https://wqshop.jd.com/mshop/gethomepage?venderid=" + vender_id
                shop_info = {'shopName': shop_name, 'venderId': vender_id, 'shopId': shop_id, 'shopUrl': shop_url}

                # Shop(vender_id, shop_id, shop_name).run()

                if self.shop_total.get(vender_id, None) is None:
                    self.logger.info("new shop: {}".format(str(shop_info)))
                    self.shop_total[vender_id] = shop_info
                    self.shop_new[vender_id] = shop_info

                insert_sql = "insert or replace into {}(shopName,venderId,shopId,shopUrl) values('{}','{}','{}','{}')".format(
                    table_name,
                    shop_name, vender_id, shop_id, shop_url)
                self.cur.execute(insert_sql)
                self.conn.commit()

            elif re.match(re_shop_draw_url, path_part) and params:
                vender_id = params.get('venderid') or params.get('venderId')
                if vender_id:
                    url = "https://wqshop.jd.com/mshop/gethomepage?venderid=" + vender_id[0]
                    self.collect_shop_info(url)

        except Exception:
            self.logger.exception(sys.exc_info())


if __name__ == '__main__':
    log_format = '%(asctime)s %(name)s[%(module)s] %(levelname)s: %(message)s'
    # logging.basicConfig(filename=log_path, format=log_format, level=logging.INFO)
    logging.basicConfig(format=log_format, level=logging.INFO)

    DailyShopSpider().start()
