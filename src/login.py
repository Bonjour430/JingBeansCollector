#!/usr/bin/env python 
# -*- coding:utf-8 -*-
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from src.config import data_path
from src.utils.jd_login_selenium import JD
from src.utils.m_jd_login_selenium import M_JD
from src.utils.utils import readCookies, writeCookies

jd_first_page = 'https://jd.com/'
jd_home_page = 'https://home.jd.com/'
jd_login_page = 'https://passport.jd.com/new/login.aspx'

m_jd_first_page = 'https://m.jd.com'
m_jd_home_page = 'https://home.m.jd.com'
m_jd_login_page = 'https://plogin.m.jd.com/user/login.action'

class JD_Auto_Login:
    def __init__(self):
        # 打开用于登陆的chrome浏览器
        ua_win10_chrome = "(Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
        options = Options()
        options.add_argument("user-agent=" + ua_win10_chrome)
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        self.browser = webdriver.Chrome(options=options)
        self.browser.set_page_load_timeout(60)
        self.browser.set_script_timeout(30)
        self.browser.implicitly_wait(20)
        # 必须先访问，才能再添加cookies
        self.browser.get(jd_first_page)

    def auto_login(self):
        # 读取文件中的cookies
        cookies_path = data_path / 'cookies.json'
        cookies = readCookies(cookies_path)
        if cookies:
            # 如果从文件中读取到了cookies，就放入浏览器中
            for cookie in cookies:
                self.browser.add_cookie(cookie)

        # 登录京东PC端
        JD(self.browser).login()
        sleep(1)

        # 登录京东移动端
        M_JD(self.browser).login()
        sleep(1)

        self.browser.get("https://wqs.jd.com/pet-dog/index.html")
        self.browser.get("https://pro.m.jd.com/mall/active/NJ1kd1PJWhwvhtim73VPsD1HwY3/index.html")

        writeCookies(self.browser.get_cookies(), cookies_path)
        sleep(2)

        self.browser.quit()


if __name__ == '__main__':
    JD_Auto_Login().auto_login()