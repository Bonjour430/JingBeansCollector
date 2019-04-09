#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import logging
import sys
from time import sleep

from selenium import webdriver

# #kbCoagent > ul > li:nth-child(1) > a
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.config import config
from src.utils.utils import findElement


class M_JD:

    def __init__(self, driver: webdriver):
        self.driver = driver
        self.first_page = 'https://m.jd.com'
        self.home_page = 'https://home.m.jd.com'
        self.login_page = 'https://plogin.m.jd.com/user/login.action'
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
            success = self.qq_auth_login()
        else:
            self.logger.info("JD m_mall logged in,no need to re-login, current url：" + self.driver.current_url)
            success = True

        # if success:
        #     try:
        #         if EC.element_to_be_clickable((By.XPATH, "//*[@id=\"pcprompt-viewpc\"]")):
        #             findElement(self.driver, (By.XPATH, "//*[@id=\"pcprompt-viewpc\"]")).click()
        #             sleep(1)
        #
        #         self.batch_unfollow_fav()
        #     except Exception:
        #         self.logger.exception(sys.exc_info())

    # 账户登录
    def account_login(self):
        try:
            findElement(self.driver, (By.ID, "username")).send_keys(config.jd["username"])
            findElement(self.driver, (By.ID, "password")).send_keys(config.jd["password"])
            findElement(self.driver, (By.ID, "loginBtn")).click()

            # 循环检测是否登陆
            while True:
                try:
                    WebDriverWait(self.driver, 10).until(EC.url_contains(self.home_page[-13:]))
                    break
                except TimeoutException:
                    if EC.visibility_of_element_located((By.XPATH, "//*[@id=\"captcha\"]")):
                        self.logger.warning("JD m-mall logging, please pic auth...")
                    continue

            self.logger.info('JD m-mall login success！')
            return True
        except Exception:
            self.logger.exception(sys.exc_info())
            return False

    # QQ授权登录, 使用前提是QQ客户端在线
    def qq_auth_login(self):
        # QQ授权登录
        try:
            qq_login = findElement(self.driver, (By.CSS_SELECTOR,
                                                 'body > section > div.wrap.loginPage > div.login-type > div.quick-login > a.J_ping.quick-qq'))
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
                    WebDriverWait(self.driver, 10).until(EC.url_contains(self.home_page[-13:]))
                    break
                except TimeoutException:
                    self.logger.warning("JD m-mall logging, please scan the QR code with QQ...")
                    continue
            self.logger.info('JD m-mall login success！')
            return True
        except Exception:
            self.logger.exception(sys.exc_info())
            return False

    # 批量取消收藏的店铺
    def batch_unfollow_fav(self):
        self.driver.get("https://wqs.jd.com/my/fav/shop_fav.shtml")

        i = 1
        while True:
            try:
                subscribe_nothing = WebDriverWait(self.driver, 3, 0.5).until(
                    EC.visibility_of_element_located((By.ID, "shoplist_nothing")))
                if subscribe_nothing and subscribe_nothing.is_displayed():
                    self.logger.info("已无收藏的店铺")
                    break

                if EC.visibility_of_element_located((By.ID, "shoplist_edit")):
                    findElement(self.driver, (By.ID, "shoplist_edit")).click()

                if EC.visibility_of_element_located((By.ID, "selectAllBtn")):
                    findElement(self.driver, (By.ID, "selectAllBtn")).click()

                if EC.visibility_of_element_located((By.ID, "multiCancle")):
                    findElement(self.driver, (By.ID, "multiCancle")).click()

                if EC.visibility_of_element_located((By.ID, "ui_btn_confirm")):
                    findElement(self.driver, (By.ID, "ui_btn_confirm")).click()

                self.logger.info("取消第{}批收藏的店铺".format(str(i)))
                i = i + 1

                sleep(2)
            except Exception as e:
                self.logger.error("批量取消收藏店铺异常...")
                break


if __name__ == '__main__':
    log_format = '%(asctime)s %(name)s[%(module)s] %(levelname)s: %(message)s'
    # logging.basicConfig(filename=log_path, format=log_format, level=logging.INFO)
    logging.basicConfig(format=log_format, level=logging.INFO)

    browser = webdriver.Chrome()
    jd = M_JD(browser)
    jd.login()
