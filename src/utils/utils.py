#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import json
import os

import requests
from requests import Session
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome
from selenium.webdriver.support.wait import WebDriverWait


def readCookies(file_path):
    """
    从文件中读取cookies并返回 文件不存在则返回False
    """
    # 不存在cookies文件
    if not os.path.exists(file_path):
        print("cookies文件不存在！")
        return False
    with open(file_path, "r") as f:
        cookies = json.load(f)
    return cookies


def writeCookies(cookies, file_path):
    """
    从浏览器中向文件写入cookies
    """
    with open(file_path, "w") as f:
        json.dump(cookies, f, indent=4)


def read_data_from_file(file_path):
    """
    从文件中读取数据并返回 文件不存在则返回False
    """
    # 不存在cookies文件
    if not os.path.exists(file_path):
        print("文件不存在！".format(str(file_path)))
        return False
    with open(file_path, "r") as f:
        cookies = json.load(f)
    return cookies


def write_data_to_file(data, file_path):
    """
    从浏览器中向文件写入数据
    """
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def update_session_cookies(session: Session, cookies_path):
    selenium_cookies = readCookies(cookies_path)
    requests_cookies = {}
    for cookie in selenium_cookies:
        requests_cookies[cookie['name']] = cookie['value']

    requests.utils.add_dict_to_cookiejar(session.cookies, requests_cookies)


def update_chrome_cookies(chrome: Chrome, cookies_path):
    # 必须先访问，才能再添加cookies
    chrome.get('https://m.jd.com')
    cookies = readCookies(cookies_path)
    if cookies:
        # 如果从文件中读取到了cookies，就放入浏览器中
        for cookie in cookies:
            chrome.add_cookie(cookie)


def findElement(driver: webdriver, locator, timeout=5):
    """定位元素封装方法"""
    try:
        element = WebDriverWait(driver, timeout, 0.5).until(lambda x: x.find_element(*locator))
        return element
    except TimeoutException:
        return None
