#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import logging
import sys
from time import sleep

from selenium import webdriver

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.config import config
from src.utils.utils import findElement


class JD:

    def __init__(self, driver: webdriver):
        self.driver = driver
        self.first_page = 'https://jd.com/'
        self.home_page = 'https://home.jd.com/'
        self.login_page = 'https://passport.jd.com/new/login.aspx'
        self.logger = logging

    def login(self):
        # 这里利用一个技巧，直接去访问一个需要登录后才能访问的地址home_page，
        # 如果当前没有登录，则会自动跳转到登录页面login_page，并且登录成功后，又自动回到home_page
        # 同时这又方便判断是否登录成功，如果持有登录成功过的cookie,则直接就能显示home_page
        self.driver.get(self.home_page)
        sleep(3)
        # 访问PC端个人中心https://home.jd.com，如果当前是未登录状态，会自动跳转到登录界面，如果已经登录，则能直接进入到个人中心
        if self.login_page in self.driver.current_url:
            # self.account_login()
            self.qq_auth_login()
        else:
            self.logger.info("JD PC platform logged in,no need to login now,current url:" + self.driver.current_url)

    # 账户登录
    def account_login(self):
        try:
            # 账户登陆
            findElement(self.driver, (
            By.CSS_SELECTOR, '#content > div.login-wrap > div.w > div > div.login-tab.login-tab-r')).click()
            findElement(self.driver, (By.ID, "loginname")).send_keys(config.jd["username"])
            findElement(self.driver, (By.ID, "nloginpwd")).send_keys(config.jd["password"])
            findElement(self.driver, (By.ID, "loginsubmit")).click()

            # 循环检测是否登陆
            while True:
                try:
                    WebDriverWait(self.driver, 10).until(EC.url_contains(self.home_page[-12:]))
                    break
                except TimeoutException:
                    if EC.visibility_of_element_located(
                            (By.CSS_SELECTOR, "# JDJRV-wrap-loginsubmit > div > div > div")):
                        self.logger.info("JD PC logging,please pic auth...")
                    continue

            self.logger.info('JD PC login success！')
            return True
        except Exception:
            self.logger.exception(sys.exc_info())
            return False

    # QQ授权登录, 使用前提是QQ客户端在线
    def qq_auth_login(self):
        try:
            # QQ授权登录
            qq_login = findElement(self.driver, (By.CSS_SELECTOR, '#kbCoagent > ul > li:nth-child(1)'))
            if qq_login is None:
                self.logger.info("QQ授权登录 未找到")
                return False

            qq_login.click()
            sleep(2)

            # 切换到最新打开的窗口
            window_handles = self.driver.window_handles
            self.driver.switch_to.window(window_handles[-1])
            self.logger.info(self.driver.title)

            # 切换iframe
            i_frame = WebDriverWait(self.driver, 5).until(lambda d: d.find_element_by_id('ptlogin_iframe'))
            self.driver.switch_to.frame(i_frame)

            # 点击头像进行授权登录
            qq_face = findElement(self.driver, (By.XPATH, '//*[@id="qlogin_list"]/a[1]'))
            if qq_face and qq_face.is_displayed:
                qq_face.click()
            # else:
            #     self.logger.warning("QQ未登录，只能扫描登录")
            #     # qr_area = WebDriverWait(self.driver, 5).until(lambda d: d.find_element_by_id('qr_area'))
            #     # print()

            # 循环检测是否登陆
            while True:
                try:
                    WebDriverWait(self.driver, 10).until(EC.url_contains(self.home_page[-12:]))
                    break
                except TimeoutException as e:
                    self.logger.warning("Please scan the QR code with QQ " + str(e.msg))
                    continue

            self.logger.info('JD PC login success with QQ auth！')
            return True
        except Exception:
            self.logger.exception(sys.exc_info())
            return False


if __name__ == '__main__':
    log_format = '%(asctime)s %(name)s[%(module)s] %(levelname)s: %(message)s'
    # logging.basicConfig(filename=log_path, format=log_format, level=logging.INFO)
    logging.basicConfig(format=log_format, level=logging.INFO)

    browser = webdriver.Chrome()
    jd = JD(browser)
    jd.login()
