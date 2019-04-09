#!/usr/bin/env python 
# -*- coding:utf-8 -*-

import os
import sys

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

import itchat
from selenium import webdriver

from src.main import main


@itchat.msg_register('Text')
def text_reply(msg):
    global flag
    message = msg['Text']
    fromName = msg['FromUserName']
    toName = msg['ToUserName']

    # logging.error('# 收到命令: ' + message + ",From:" + fromName + ",to:" + toName)
    print('# 收到命令: ' + message + ",From:" + fromName + ",to:" + toName)

    if toName == 'filehelper':
        itchat.send(sendMsg, fromName)
        if message == "打卡":
            main()
            global driver
            chromedriver = r"D:\DevPlatform\chromedriver\chromedriver.exe"
            os.environ['webdriver.chromedriver'] = chromedriver
            driver = webdriver.Chrome(chromedriver)


if __name__ == '__main__':
    sendMsg = u"{消息助手}：暂时无法回复"
    usageMsg = u"使用方法：\n1.开启打卡脚本：打卡\n" \
               u"2.发送验证码：验证码\n3.重新获取验证码：再次获取验证码\n" \
               u"4.帮同事打卡：代打卡\n5.输入验证码：直接回复四位验证码\n" \
               u"6.查看打卡是否成功：结果\n"

    print('开始登陆itchat')
    itchat.auto_login()
    itchat.send(usageMsg, 'filehelper')
    global_var_list = []
    itchat.run
