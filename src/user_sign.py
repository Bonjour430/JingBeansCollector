#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import json
import logging
import os
import random
import re
import sys

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

import threading
import time
from urllib.parse import splitquery, parse_qs

import requests
from bs4 import BeautifulSoup
from pyquery import PyQuery

from src.config import data_path
from src.utils.utils import update_session_cookies

"""签到任务"""


class UserSign(threading.Thread):

    def __init__(self):
        super(UserSign, self).__init__(name="用户签到")
        self.session = requests.session()
        self.job_success = False
        self.logger = logging

        self.mall_sign_url = {}
        self.vender_sign_url = {}

        self.view_ad_url = []

    def run(self):

        self.logger.info('Job Start: {}'.format(self.name))

        update_session_cookies(self.session, data_path / "cookies.json")

        self.jd_app_bean_sign()
        time.sleep(1)

        self.jd_jr_sign()
        time.sleep(1)

        self.jd_double_sign()
        time.sleep(1)

        self.jd_vip_sign()
        time.sleep(1)

        self.jr_gb_sign_zq()
        time.sleep(1)

        self.jr_gb_sign_flip_draw()
        time.sleep(1)

        self.vender_sign_url[
            u'九阳'] = "https://lzkj-isv.isvjcloud.com/sign/sevenDay/signActivity?activityId=d16c168d37fb45da85525c6eec163691&venderId=1000001465"
        self.vender_sign_url[
            u'疯狂的小狗旗舰店'] = "https://lzkj-isv.isvjcloud.com/sign/signActivity?activityId=4844402dfae64b98818e5735dbfe5e43&venderId=686353"
        self.vender_sign_url[
            u'gb好孩子'] = "https://lzkj-isv.isvjcloud.com/sign/signActivity?activityId=cd3bf71e1ccd4d9d9b915fb221440570&venderId=1000003448"
        self.vender_sign_url[
            u'劲牌京东旗舰店'] = "https://lzkj-isv.isvjcloud.com/sign/signActivity?activityId=f5e1391b946949eebc84703a3bbe8c95&venderId=1000016385"
        self.vender_sign_url[
            u'古井贡酒京东自营旗舰店'] = "https://lzkj-isv.isvjcloud.com/sign/signActivity?activityId=73da082bb3174787a6ea770ec328aabf&venderId=1000015663"
        self.vender_sign_url[
            u'得宝'] = "https://lzkj-isv.isvjcloud.com/sign/signActivity?activityId=c440ad0e29314e80a554a69d8eece225&venderId=1000010410"
        self.vender_sign_url[
            u'黑武士'] = "https://lzkj-isv.isvjcloud.com/sign/sevenDay/signActivity?activityId=160b72646209448fae694c0ebaad74a9&venderId=1000105445"
        self.vender_sign_url[
            u'滴露'] = "https://lzkj-isv.isvjcloud.com/sign/sevenDay/signActivity?activityId=ad8378885b3548c99566f409f1476fe0&venderId=206265"
        self.vender_sign_url[
            u'尼康'] = "https://lzkj-isv.isvjcloud.com/sign/signActivity?activityId=45984224f90446c996eb008370d94e8f&venderId=10008806"
        self.vender_sign_url[
            u'海信'] = "https://lzkj-isv.isvjcloud.com/sign/sevenDay/signActivity?activityId=81561fc8c98440aaa3e1117b083aa97c&venderId=1000002261"
        self.vender_sign_url[
            u'斯米克磁砖'] = "https://lzkj-isv.isvjcloud.com/sign/signActivity?activityId=2f34da86596a4274ba3e074bf477f280&venderId=681974"
        # self.vender_sign_url[
        #     u'霸王醉'] = "https://lzkj-isv.isvjcloud.com/sign/sevenDay/signActivity?activityId=ebdd8d25d5d34aed91c236c2944bb3a8&venderId=656920"
        self.vender_sign_url[
            u'科龙(Kelon)'] = "https://lzkj-isv.isvjcloud.com/sign/sevenDay/signActivity?activityId=f84e0a2a372e4c50993ce5badecdb169&venderId=1000000900"
        # self.vender_sign_url[
        #     u'布鲁雅尔'] = "https://lzkj-isv.isvjcloud.com/sign/sevenDay/signActivity?activityId=a70400245707438b947b3c192ec2693d&venderId=1000002484"
        self.vender_sign_url[
            u'心想'] = "https://lzkj-isv.isvjcloud.com/sign/sevenDay/signActivity?activityId=e56c3b1a22694bd5a536bdee903393a5&venderId=665082"
        self.vender_sign_url[
            u'名龙堂'] = "https://lzkj-isv.isvjcloud.com/sign/signActivity?activityId=eb086dc3fb3945488692399273e049d2&venderId=751337"
        self.vender_sign_url[
            u'笛爱儿'] = "https://lzkj-isv.isvjcloud.com/sign/signActivity?activityId=7f3f0acd103149f0b0d9942788e9eb11&venderId=1000091580"
        self.vender_sign_url[
            u'蒲江馆'] = "https://lzkj-isv.isvjcloud.com/sign/signActivity?activityId=cdb4760e6f264427b8ff7288bfe32909&venderId=647014"
        self.vender_sign_url[
            u'商旅宝'] = "https://lzkj-isv.isvjcloud.com/sign/signActivity?activityId=d0a5946e774b4a0aa415d1dbda06d820&venderId=19244"
        self.vender_sign_url[
            u'维达多康'] = "https://lzkj-isv.isvjcloud.com/sign/signActivity?activityId=10ef499073454450b4a7753452e2144c&venderId=1000121201"

        for key, value in self.vender_sign_url.items():
            self.vender_sign_up(key, value)

        self.mall_sign_url[u'京东清洁馆'] = "https://pro.m.jd.com/mall/active/2Tjm6ay1ZbZ3v7UbriTj6kHy9dn6/index.html"
        self.mall_sign_url[u'京东个护'] = "https://pro.m.jd.com/mall/active/NJ1kd1PJWhwvhtim73VPsD1HwY3/index.html"
        self.mall_sign_url[u'母婴馆'] = "https://pro.m.jd.com/mall/active/bVs9EG4MMK4zKdqVt86UFABX2en/index.html"
        self.mall_sign_url[u'微信签到有礼'] = "https://pro.m.jd.com/mall/active/2PaRTYZBTCt6CTg1NSV58wo5rwQx/index.html"
        self.mall_sign_url[u'京东超市'] = "https://pro.m.jd.com/mall/active/aNCM6yrzD6qp1Vvh5YTzeJtk7cM/index.html"
        self.mall_sign_url[u'京鱼座智能'] = "https://pro.m.jd.com/mall/active/2C4Az1JUCWN8f3Y6xaxHbzTLkUzC/index.html"
        self.mall_sign_url[u'拍拍二手签到'] = "https://pro.m.jd.com/mall/active/3S28janPLYmtFxypu37AYAGgivfp/index.html"
        # self.sign_url[u'京东礼品卡'] = "https://pro.m.jd.com/mall/active/2nTmRwG2r7d83rQNumvf5stQzB1h/index.html"

        for key, value in self.mall_sign_url.items():
            self.mall_sign_up(key, value)

        self.view_ad_url.append(
            "https://m.jr.jd.com/btyingxiao/advertMoney/html/collar.html?iframeSrc=https%3A%2F%2Fccc-x.jd.com%2Fdsp%2Fnc%3Fext%3DaHR0cDovL3JlLm0uamQuY29tL2l0ZW0vMjAzMzk5NzQxOTguaHRtbD9yZV9kY3A9NF85ZXpWcDBWb2t1U1RIRHhnbE01SDJlQWJUYVdhMzdqeFg2czFxbXRUMFJjUjhYODdMdWV5MFR3YlFuYkJqQTNiQWlFVUUtbkNMOEhycWhOb1hRWWZOdGVsYjFJN1VnSXlyQkV3aGphUDBoNXBVNnJiQ1N5RzJ0ZldxWkIxU3Z0YjNmYlNtRjgwSF9oclM2S1dZNEZOS3VqZ0l6TkJydzNXX2xtZHkzbVl4d0NQV2lXV3VNUWZHZzQ0ZVppbmxyNDhsenFpNnE0Zk03NFdncWlUcDV0cDE0ZXRzS1FzT1QwQjBvdklRNXNVb1RZbkJEcTBmLWdlaFdScDJTZVRaLWRaQjBBQi02V2hVJTNEJnR5cGU9MQ%26log%3D0AVESKz4pwDkDsdr5j9u2SVgzKcX_ijkI3BoBo953LtElTNERR5qsSXP0WzUPielbIsrUwv5G3pYXyEX-hOlO1fx5X4ReQn6aTZibX3P5jlnpNYGX51Mbtw1fNz6NNVot6-crDmL5ULihguFdnrTO0oXqDGYU7l-7ak3UbOx-4gv4Ow0Vp0Yw5fO0O795C95FGfdCLZ0VLsTolc1lVYF4AZEHA5_KkOIzwNl1UDO-6EPiRmaa_t_7oy_e2XeDQHup4FbSIqgSzAdSK6AP05xUsZRmM-yhmdVuE3X3aSVh4IyWsyKRPquSM-Y_-tavKr4cJ1YeY6Z48_P2YNtFqDLAuO60hFTN5xWCPTM5Y4wxER9_EASaw35EuqOgW1jb7OfN8QZbrebTfblz2K_D3p4C_GQPsnb_Gf7eDeAlPptHXHOa4VIL12Q2DOrZbZ4r8rj%26v%3D404&adId=-1042849196")
        self.view_ad_url.append(
            "https://m.jr.jd.com/btyingxiao/advertMoney/html/collar.html?iframeSrc=https%3A%2F%2Fccc-x.jd.com%2Fdsp%2Fnc%3Fext%3DaHR0cDovL2l0ZW0ubS5qZC5jb20vcHJvZHVjdC8yMjAwMzQzLmh0bWw%26log%3DH3J1f0wVj0F4NcR9dEtzqmofnupZW21KCXtQ5gB--S9d4nkxuJciH4dHE6qetX9R2rgjtFEz-iS7Thyo84M1gqBZDNnY36zpyLcKL0YEoKW3hj8oyUFTqqtFmOKUIW-BXb-k9VOoZfvT0oIn4X3mZaafcfkZ3S3eqX4jzwgtrBPy1mLi5L88K3UCwjZaOM4ytY6iz5SQXPZq0NSM72_ybWC2sKvMd0znu-PPRi3liqrxpzoomVdFxCQtFApiMsgXxlrLAH-Dd3oGc0M64qMkwSmCGInxsJzz7wxNJbh7ow0QO1iHQYxoYajaLVkZjBV6EF6KTTQXUPCNVffg72cy6TdTEHCbQpQ9HhgFZtCrMHnfAF9b9YOnaZ1YNe7L-Ed3gLw3NgZkqAm3XCw3Gw3rDQ%26v%3D404&adId=531454248")
        self.view_ad_url.append(
            "https://m.jr.jd.com/btyingxiao/advertMoney/html/collar.html?iframeSrc=https%3A%2F%2Fccc-x.jd.com%2Fdsp%2Fnc%3Fext%3DaHR0cDovL3JlLm0uamQuY29tL2l0ZW0vMjg3NTI2Njc3NTkuaHRtbD9yZV9kY3A9NDZaV2l6WlVWb2t1aFAwUENzV0FHQUtlQWJUYVdhM21qeFg2czFxbXRUMFJjUjhYN3JMdWZ5MFR3YlE2YkJqQTNjNVVFMEUtdEZiLUhycXFMOUxSbG1ESjNpRGxOaGk4MHNVMDdvQ29rM2JXSnh2WllsOTY0SFlvZ0E3eEFkWXo4LUNvTUhiWjZRRGhuYkd3S21vMUE5bW5tUndfTkIzdDMzZTJrb0s3MUlrclgtaW1XbS1PWnZEdzRmcVEyMzg4LThsMF9qRDNwdkFzVHNHQWZNS0ZPWm91RVN0c00xT1MwSVVwdnpSNGY0dC1nVHQ3cTBVVWdzZkhQM1BJMDdGOXBQTWZBSG1tWFY2N3JMWmU3QlVpcUNtTnpqLWNJSWFqJnR5cGU9MQ%26log%3DJHNsT1cVQI1RK9sKqMmcTndzYGyf9_zA5ThYAYBU6yBtFOCPZC2nljo3cWqFb8SWbsgPeB19Y6ZjoHuL3eLluWsFAaNL_3EQe39It7wWXw0DdvMaEMaa4HeNSqhUpxYG3vDPu9tt7j3uNuRkR5TeSs7f6E83Kp9uVdTgWTw3e_XiTJ6vYQQI3HLWgPtrxARXxBtyyzva3t7GtCkGIc-E_lwIMqWJQKN8XXldfQu_C900owokdtsPk14ve-t_1gulpCQTOPqwdbaSvY_eQl7wTSvHEUi_-rfDo_1bZdAEfX-wcM_nOp1hBS3TSuXyG9QGoh0BaC_fgm7NMTMIh7LycasyD9iinUso6W9pi0Ic9tz9lAOhBIbnVm6XGMKkN9Huv4KuTBP4Txe0B_Xyfqvs_DiWA1hX_KMmT8uPHmguqrba3-p-_aBv0Is9emAf5i72UWpJxy_1pqbCH8tXmePaBw%26v%3D404&adId=-1910831221")
        for url in self.view_ad_url:
            self.jr_view_ad(url)

        self.daily_draw_sign()
        time.sleep(0.5)

        self.enterprise_purchase()
        time.sleep(0.5)

    def jd_app_bean_sign(self):
        """京东App领京豆"""
        job_name = "京东App领京豆"
        index_url = "https://bean.m.jd.com/"

        try:
            info_headers = {
                'Host': 'api.m.jd.com',
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': index_url
            }
            info_body = {"source": "", "monitor_refer": "", "rnVersion": "3.9", "rnClient": "1",
                         "monitor_source": "bean_m_bean_index"}
            info_api = "https://api.m.jd.com/client.action?functionId=findBeanIndex&body=" + json.dumps(info_body) \
                       + "&appid=ld&client=android&clientVersion=&networkType=&osVersion=&uuid=&jsonp=jsonp"

            r = self.session.get(info_api, headers=info_headers).text
            if 'jsonp' not in r:
                self.logger.error("{} 获取签到信息，网络请求失败...".format(job_name))
                return

            as_json = json.loads(r[6:-2])
            if as_json['code'] != '0' or 'errorCode' in as_json or 'errorMessage' in as_json:
                self.logger.error("{} 获取签到信息，数据异常...".format(job_name))
                return

            data = as_json['data']
            # 根据测试, 1 表示已签到, 2 表示未签到, 3 表示未登录
            if data['status'] is "1":
                self.logger.info(
                    "{} 已签到，当前有 {} 京豆,连续签到 {} 天".format(job_name, str(data['totalUserBean']),
                                                        str(data['continuousDays'])))
                return
            elif data['status'] is "2":
                sign_body = {"monitor_refer": "", "rnVersion": "3.9", "fp": "-1", "shshshfp": "-1", "shshshfpa": "-1",
                             "referUrl": "-1", "userAgent": "-1", "jda": "-1", "monitor_source": "bean_m_bean_index"}
                sign_api = "https://api.m.jd.com/client.action?functionId=signBeanIndex&body=" + json.dumps(sign_body) \
                           + "&appid=ld&client=android&clientVersion=&networkType=&osVersion=&uuid=&jsonp=jsonp"

                sign_headers = {
                    'Host': 'api.m.jd.com',
                    'Accept': '*/*',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Referer': 'https://bean.m.jd.com/bean/signIndex.action'
                }

                r = self.session.get(sign_api, headers=sign_headers).text
                if 'jsonp' not in r:
                    self.logger.error("{} 签到，网络请求失败...".format(job_name))
                    return

                as_json = json.loads(r[6:-2])
                if as_json['code'] != '0' or 'errorCode' in as_json or 'errorMessage' in as_json:
                    self.logger.error("{} 签到，数据异常...".format(job_name))
                    return

                data = as_json['data']
                sign_success = (data['status'] == '1')
                self.logger.info("{} {}".format(job_name, str(data)))

                if sign_success:
                    bean_count = data['continuityAward']['beanAward']['beanCount']
                    message = '获得京豆 {} 个.'.format(bean_count)
                else:
                    message = data['dailyAward']['title']

                self.logger.info('{} 签到成功: {}; Message: {}'.format(job_name, sign_success, message))
        except Exception:
            self.logger.error("{} 签到发生异常".format(job_name))
            self.logger.exception(sys.exc_info())

    def jd_jr_sign(self):
        """京东金融签到"""
        job_name = "京东金融签到"
        index_url = "https://vip.jr.jd.com"
        info_url = 'https://vip.jr.jd.com/newSign/querySignRecord'
        sign_url = 'https://vip.jr.jd.com/newSign/doSign'

        try:
            self.session.headers.update({
                'Host': 'api.m.jd.com',
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': index_url
            })
            r = self.session.post(info_url)
            if r.ok:
                data = r.json()
                signed = data['isFlag']
                sign_days = data['signContinuity']
                self.logger.info(
                    '{} 今日已签到: {}; 签到天数: {}; 现有钢镚: {}'.format(job_name, signed, sign_days, data['accountBalance']))

                if not signed:
                    response = self.session.post(sign_url).json()
                    self.logger.info("{} {}".format(job_name, str(response)))

                    sign_success = response['signSuccess']
                    sign_data = response['signResData']

                    if sign_success and sign_data:
                        unit = ['', '京豆', '金币', '钢镚'][sign_data['rewardType']]
                        count = sign_data['thisAmount'] / 100 if sign_data['rewardType'] == 3 else sign_data[
                            'thisAmount']
                        self.logger.info('{} 签到成功, 获得 {} 个{}.'.format(job_name, count, unit))
                    else:
                        self.logger.error('{} 签到失败: Code={}'.format(job_name, response['resBusiCode']))
        except Exception:
            self.logger.error("{} 签到发生异常".format(job_name))
            self.logger.exception(sys.exc_info())

    def jd_double_sign(self):
        """双签赢奖励"""
        job_name = "双签赢奖励"
        index_url = "https://m.jr.jd.com/integrate/signin/index.html"

        try:
            self.session.headers.update({
                'Host': 'ms.jr.jd.com',
                'Origin': 'https://m.jr.jd.com',
                'Accept': 'application/json',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                'Connection': 'keep-alive',
                'Referer': index_url
            })
            info_api = "https://ms.jr.jd.com/gw/generic/jrm/h5/m/signInit?_=" + str(int(time.time() * 1000))
            data = "reqData=" + json.dumps({"source": ""})
            r = self.session.post(info_api, data=data)
            if r.ok:
                data = r.json()['resultData']
                if data['isGet']:
                    self.logger.info("{} 已完成双签".format(job_name))
                    return

                if data['isSignInJr'] and data['isSignInJd']:
                    award_api = "https://ms.jr.jd.com/gw/generic/jrm/h5/m/getAwardList?_=" + str(
                        int(time.time() * 1000))
                    data = "reqData=" + json.dumps({})
                    response = self.session.post(award_api, data=data).json()
                    self.logger.info("{} {}".format(job_name, str(response)))
        except Exception:
            self.logger.error("{} 签到发生异常".format(job_name))
            self.logger.exception(sys.exc_info())

    def jd_vip_sign(self):
        """京东会员签到"""
        index_url = "https://vip.jd.com/"
        job_name = "京东会员签到"

        try:
            self.session.headers.update({
                'Host': 'api.m.jd.com',
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': index_url
            })
            api = "https://api.m.jd.com/client.action?functionId=aries_m_scoreHome" \
                  "&body=%7B%22isAjax%22%3A%221%22%2C%22apiType%22%3A%22h5%22%2C%22v%22%3A%22%22%2C%22paramData%22%3A%7B%7D%2C%22bodyData%22%3A%7B%7D%7D" \
                  "&appid=aries_m_h5&t=" + str(int(time.time() * 1000)) + "&jsonp=jsonp"

            r = self.session.get(api).text
            if r is None or ('jsonp' not in r):
                self.logger.error("京东会员签到 网络请求失败...")
                return
            as_json = json.loads(r[6:-2])
            self.logger.info("{} {}".format(job_name, str(as_json)))
            result = as_json['result']
            if not result['isLogin']:
                self.logger.error("京东会员签到 未登录...")
                return

            floorInfoList = result['floorInfoList']
            for floor in floorInfoList:
                if floor['code'] == "M_USER_INFO":
                    signType = floor['dataDetail']['signType']
                    self.logger.info("京东会员签到 " + signType['message'])
                    if signType and signType['code'] == 100:
                        api = "https://vip.m.jd.com/page/signin"
                        headers = {
                            'Host': 'vip.m.jd.com',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                            'Accept-Encoding': 'gzip, deflate, br',
                            'upgrade-insecure-requests': '1'
                        }
                        r = self.session.get(api, headers=headers).text
                        # self.logger.info("京东会员签到 " + r)
                        bean_num = PyQuery(r)('div.dayGet span.beanNum').text()
                        self.logger.info("京东会员签到 已领取 {} 京豆".format(bean_num))
                    elif signType and signType['code'] == 101:
                        return

        except Exception:
            self.logger.error("{} 签到发生异常".format(job_name))
            self.logger.exception(sys.exc_info())

    def jr_gb_sign_zq(self):
        """京东金融领钢镚-赚钱签到"""
        job_name = "京东金融-赚钱签到"
        index_url = "https://m.jr.jd.com/spe/qyy/hzq/index.html?usertype=1176&sid=#/"
        test_api = "https://ms.jr.jd.com/gw/generic/base/h5/m/baseGetMessByGroupTypeEncryptNew"
        sign_api = "https://ms.jr.jd.com/gw/generic/base/h5/m/baseSignInEncryptNew"
        try:
            self.session.headers.update({
                'Host': 'ms.jr.jd.com',
                'Origin': 'https://m.jr.jd.com',
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Connection': 'keep-alive',
                'Referer': index_url
            })
            payload = {
                'reqData': '{"clientType":"outH5","userType":1176,"groupType":166}',
                'source': 'jrm'
            }
            sign_data = {}
            # 参见 daka_app_min.js -> h.getSign, 第 1825 行开始
            r = self.session.post(test_api, data=payload)
            as_json = r.json()
            self.logger.info("{} {}".format(job_name, str(as_json)))

            if 'resultData' in as_json:
                sign_data = r.json()['resultData']['53']
            else:
                error_msg = as_json.get('resultMsg') or as_json.get('resultMessage')
                self.logger.error('获取打卡数据失败: {}'.format(error_msg))
                return

            signed = sign_data['signInStatus'] == 1
            self.logger.info('{}今日已打卡: {}'.format(job_name, signed))
            if signed:
                return

            payload = {
                'reqData': '{}',
                'source': 'jrm'
            }
            r = self.session.post(sign_api, data=payload)
            as_json = r.json()

            if 'resultData' in as_json:
                result_data = as_json['resultData']
                # statusCode 14 似乎是表示延期到帐的意思, 如: 签到成功，钢镚将于15个工作日内发放到账
                sign_success = result_data['isSuccess'] or result_data['statusCode'] == 14
                message = result_data['showMsg']

                # 参见 daka_app_min.js, 第 1893 行
                continuity_days = result_data['continuityDays']

                if continuity_days > 1:
                    message += '; 签到天数: {}'.format(continuity_days)

            else:
                sign_success = False
                message = as_json.get('resultMsg') or as_json.get('resultMessage')

            self.logger.info('京东金融领钢镚-赚钱签到: {}; Message: {}'.format(sign_success, message))


        except Exception:
            self.logger.error("{} 签到发生异常".format(job_name))
            self.logger.exception(sys.exc_info())

    def jr_gb_sign_fall_line(self):
        """京东钢镚-割吊绳"""
        job_name = "京东钢镚-割吊绳"
        index_url = "https://coin.jd.com/m/gb/index.html"
        test_api = "https://coin.jd.com/m/sign/isSign.do"
        sign_api = "https://ms.jr.jd.com/gw/generic/base/h5/m/baseSignInEncryptNew"
        try:
            self.session.headers.update({
                'Host': 'coin.jd.com',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Connection': 'keep-alive',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': index_url
            })

            r = self.session.get(test_api)
            as_json = r.json()
            self.logger.info("{} {}".format(job_name, str(as_json)))

            if as_json['success'] and 'data' in as_json:
                sign_data = as_json['data']
            else:
                error_msg = as_json['success'] or as_json.get('resultMessage')
                self.logger.error('京东钢镚-割吊绳 获取数据失败: {}'.format(error_msg))
                return

            signed = sign_data['signFlag']
            self.logger.info('{} 今日已打卡: {}'.format(job_name, signed))
            if signed:
                return

            # 割吊绳 api 未完成；
            self.logger.info('京东金融领钢镚-赚钱签到:未完成')

        except Exception:
            self.logger.error("{} 签到发生异常".format(job_name))
            self.logger.exception(sys.exc_info())

    def jr_gb_sign_flip_draw(self):
        """京东钢镚-翻牌"""
        job_name = "京东钢镚-翻牌"
        index_url = "https://active.jd.com/forever/flipDraw/html/index.html"
        try:
            self.session.headers.update({
                'Host': 'gpm.jd.com',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': index_url
            })
            # https://gpm.jd.com/signin_new/home?sid=ed611e91ca782e6d7728be5cdf12f848&uaType=4&_=1553736292174&callback=Zepto1553736292127
            test_api = "https://gpm.jd.com/signin_new/home?sid=" + self.session.cookies.get(
                'sid') + "&uaType=4&_=" + str(int(time.time() * 1000)) + "&callback=Zepto"
            r = self.session.get(test_api).text
            # Zepto([{"code":1,"data":{"result":0,"isAllowSignin":1,"todayCount":0,"totalCount":6},"errcode":1,"flushTime":null,"msg":"成功","success":true,"systime":1553736292217,"trade":false,"usIsTrade":false}])
            if r is None or (not "Zepto" in r):
                self.logger.error("{} 获取数据失败...".format(job_name))
                return

            as_json = json.loads(r[7:-2])
            self.logger.info("{} {}".format(job_name, str(as_json)))

            if as_json['data']:
                sign_data = as_json['data']
            else:
                self.logger.error('{} 获取数据失败'.format(job_name))
                return

            allow_sign = sign_data['isAllowSignin']
            self.logger.info('{} 今日已打卡: {}'.format(job_name, not allow_sign))
            if not allow_sign:
                return

            choise_api = "https://gpm.jd.com/signin_new/choice?sid=" + self.session.cookies.get(
                'sid') + "&position=" + str(random.randint(1, 6)) + "&uaType=4&_=" + str(
                int(time.time() * 1000)) + "&callback=Zepto"
            self.session.get(choise_api)

            self.logger.info(job_name + ' 已完成')

        except Exception:
            self.logger.error("{} 签到发生异常".format(job_name))
            self.logger.exception(sys.exc_info())

    def jr_sign_mrbyb(self):
        """京东钢镚-每日蹦一蹦"""
        job_name = "京东钢镚-每日蹦一蹦"
        index_url = "https://red-e.jd.com/resources/pineapple/index.html?merchantCode=4B2CE697A1AEE055"
        try:
            merchantCode = splitquery(index_url)[1]
            merchantCode = parse_qs(merchantCode).get('merchantCode')[0]

            self.session.headers.update({
                'Host': 'coin.jd.com',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': index_url
            })
            # https://coin.jd.com/mlgnActivity/coins/checkLottery.html?merchantCode=4B2CE697A1AEE055&callback=jQuery33109727842609730113_1553737619367&_=1553737619368
            test_api = "https://coin.jd.com/mlgnActivity/coins/checkLottery.html?merchantCode=" + merchantCode + "&_=" + str(
                int(time.time() * 1000)) + "&callback=jQuery"
            r = self.session.get(test_api).text
            # jQuery({"data":3,"success":true})
            if r is None or (not "jQuery" in r):
                self.logger.error("{} 获取数据失败...".format(job_name))
                return

            as_json = json.loads(r[7:-1])
            self.logger.info("{} {}".format(job_name, str(as_json)))

            if as_json['data']:
                sign_data = as_json['data']
            else:
                self.logger.error('{} 获取数据失败'.format(job_name))
                return

            if sign_data <= 0:
                self.logger.info("{} 抽奖次数已用完...")
                return

            # 割吊绳 api 未完成；
            for i in range(0, sign_data):
                award_api = "https://coin.jd.com/mlgnActivity/coins/awardNeedLogin.html?merchantCode=" + merchantCode + "&_=" + str(
                    int(time.time() * 1000)) + "&callback=jQuery"
                self.session.get(award_api)

            self.logger.info(job_name + ' 已完成')

        except Exception:
            self.logger.error("{} 签到发生异常".format(job_name))
            self.logger.exception(sys.exc_info())

    def jr_sign_mxhb(self):
        """京东金融-免息红包"""
        job_name = "京东金融-免息红包"
        index_url = "https://m.jr.jd.com/btyingxiao/marketing/html/index.html"
        try:

            self.session.headers.update({
                'Host': 'ms.jr.jd.com',
                'Origin': 'https://m.jr.jd.com',
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': index_url
            })
            data = "reqData={\"clientType\":\"sms\",\"actKey\":\"181299\"}"
            # https://ms.jr.jd.com/gw/generic/syh_yxmx/h5/m/canJoin
            test_api = "https://ms.jr.jd.com/gw/generic/syh_yxmx/h5/m/canJoin"
            r = self.session.post(test_api, data=data).text
            # {"resultCode":0,"resultMsg":"操作成功","resultData":{"data":true,"code":"107","issuccess":"1","msg":"可以抽奖","actKey":181299},"channelEncrypt":0}

            if r is None or (not "resultData" in r):
                self.logger.error("{} 获取数据错误...".format(job_name))
                return

            as_json = json.loads(r)
            self.logger.info("{} {}".format(job_name, str(as_json)))

            if as_json['resultData']:
                sign_data = as_json['resultData']
            else:
                self.logger.error('{} 获取数据失败'.format(job_name))
                return

            if not (sign_data['msg'] is u'可以抽奖'):
                self.logger.info("{} 抽奖次数已用完...")
                return

            award_api = "https://ms.jr.jd.com/gw/generic/syh_yxmx/h5/m/lottery"
            reqData = {"clientType": "sms", "actKey": "181299", "deviceInfo": {
                "eid": self.session.cookies.get('eid'),
                "fp": self.session.cookies.get('fp'),
                "token": "DQ5J77QEMQHCXSJSHGF47G7O5LFYPP7TJWZAIY6SQ24CT3AFPL7ZWQYBYLVJR4LJHJQ6OEXOWG2JU"}}
            data = "reqData=" + json.dumps(reqData)
            self.session.post(award_api, data=data)

            self.logger.info(job_name + ' 已完成')
        except Exception:
            self.logger.error("{} 签到发生异常".format(job_name))
            self.logger.exception(sys.exc_info())

    def jr_view_ad(self, url):
        """看广告赢京豆"""
        job_name = "看广告赢京豆"
        try:
            url_path, url_query = splitquery(url)
            adId = parse_qs(url_query).get('adId')[0]

            self.session.headers.update({
                'Host': 'ms.jr.jd.com',
                'Origin': 'https://m.jr.jd.com',
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                'Connection': 'keep-alive',
                'Referer': url
            })

            reqData = {"clientType": "sms", "actKey": "176696", "userDeviceInfo": {"adId": adId}}
            data = "reqData=" + json.dumps(reqData)
            test_api = "https://ms.jr.jd.com/gw/generic/jrm/h5/m/canGetGb"
            r = self.session.post(test_api, data=data).text
            # {"resultCode":0,"resultMsg":"操作成功","resultData":{"data":{"volumn":"0","gbAmount":"137"},"canGetGb":true,"code":"1000","issuccess":"1","actKey":"176696","msg":"查询成功"},"channelEncrypt":0}
            # {"resultCode":0,"resultMsg":"操作成功","resultData":{"msg":"您今天领取的京豆已经超过3次啦，明天再来看看！","actKey":"176696","code":2002,"issuccess":"1","data":{"volumn":"0","gbAmount":"145"},"canGetGb":false},"channelEncrypt":0}

            if r is None or (not "resultData" in r):
                self.logger.error("{} canGetGb 获取数据错误...".format(job_name))
                return

            as_json = json.loads(r)
            self.logger.info("{} {}".format(job_name, str(as_json)))

            if as_json['resultData']:
                sign_data = as_json['resultData']
            else:
                self.logger.error('{} canGetGb 获取数据失败'.format(job_name))
                return

            if not (sign_data['canGetGb']):
                self.logger.info("{} canGetGb {}".format(job_name, sign_data['msg']))
                return

            award_api = "https://ms.jr.jd.com/gw/generic/jrm/h5/m/sendAdGb"
            reqData = {"clientType": "sms", "actKey": "176696", "userDeviceInfo": {"adId": adId},
                       "deviceInfoParam": {}, "bussource": ""}
            data = "reqData=" + json.dumps(reqData)
            award_r = self.session.post(award_api, data=data).text

            if award_r is None or (not "resultData" in award_r):
                self.logger.error("{} sendAdGb 获取数据错误...".format(job_name))
                return

            award_json = json.loads(award_r)
            self.logger.info("{} sendAdGb {}".format(job_name, str(award_json)))

            if award_json['resultData']:
                sign_data = award_json['resultData']
                self.logger.info("{} 获得 {} 京豆".format(job_name, award_json['resultData']['data']['volumn']))
            else:
                self.logger.error('{} sendAdGb 获取数据失败'.format(job_name))
                return

            self.logger.info(job_name + ' 已完成')
        except Exception:
            self.logger.error("{} 签到发生异常".format(job_name))
            self.logger.exception(sys.exc_info())

    def mall_sign_up(self, name, url):
        try:
            # self.logger.info(name + " 签到 " + url)
            bs = BeautifulSoup(requests.get(url).text, 'html.parser')
            dataHub = bs.find(id=re.compile("^dataHub"))
            data = dataHub.string.strip() if dataHub else None

            if data:
                data = data[data.find('{') + 1:data.rfind('}')]
                data = data[data.find('{'): data.rfind('}') + 1]
                data_json = json.loads(data)
                params = None

                for value in data_json.values():
                    if "feData" in str(value) and "signInfos" in str(value):
                        params = value['feData']['signInfos']['params']

                if params is None:
                    return

                body = {
                    "params": params,
                    "riskParam": {
                        "platform": "3",
                        "orgType": "2",
                        "openId": "-1",
                        "pageClickKey": "Babel_Sign",
                        "eid": self.session.cookies.get('3AB9D23F7A4B3C9B'),
                        "fp": "aa8693e158d7a8b3524b2d4b19037cf0",
                        "shshshfp": self.session.cookies.get("shshshfp"),
                        "shshshfpa": self.session.cookies.get("shshshfpa"),
                        "shshshfpb": self.session.cookies.get("shshshfpb"),
                        "childActivityUrl": url
                    },
                    "mitemAddrId": "",
                    "geo": {
                        "lng": "",
                        "lat": ""
                    },
                    "addressId": "",
                    "posLng": "",
                    "posLat": "",
                    "focus": "",
                    "innerAnchor": ""
                }

                api = "https://api.m.jd.com/client.action?functionId=userSign&body=" + json.dumps(body) \
                      + "&screen=362*913&client=wh5&clientVersion=1.0.0&sid=" + self.session.cookies.get('sid') \
                      + "&uuid=" + self.session.cookies.get('mba_muid') + "&area=&_=" \
                      + str(int(time.time() * 1000)) + "&callback=jsonp1"

                self.logger.info("{} 签到api:{}".format(name, api))

                self.session.headers.update({
                    'Host': 'api.m.jd.com',
                    'Accept': '*/*',
                    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Referer': url
                })

                jsonp1 = self.session.get(api).text
                ret_json = json.loads(jsonp1[7:-1])
                self.logger.info(name + " 签到 " + str(ret_json))

        except Exception as e:
            self.logger.error(name + " 签到失败:" + str(e))
            self.logger.exception(sys.exc_info())

    def vender_sign_up(self, name, url):
        try:
            url_path, url_query = splitquery(url)
            activityId = parse_qs(url_query).get('activityId')[0]
            vender_id = parse_qs(url_query).get('venderId')[0]

            bs = BeautifulSoup(requests.get(url).text, 'html.parser')
            if bs.title.string is u'活动已结束':
                self.logger.info("{} 活动已结束".format(name))
                return

            headers = {
                'Host': 'lzkj-isv.isvjcloud.com',
                'Origin': 'https://lzkj-isv.isvjcloud.com',
                'Accept': 'application/json',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': url
            }

            if url_path.startswith("https://lzkj-isv.isvjcloud.com/sign/signActivity"):
                self.session.headers.update(headers)
                api = "https://lzkj-isv.isvjcloud.com/sign/wx/signUp"
                data = "actId=" + activityId + "&pin=" + self.session.cookies.get('pin')
                ret_json = json.loads(self.session.post(api, data=data).text)
                self.logger.info("{} 签到：{}".format(name, str(ret_json)))

            elif url_path.startswith("https://lzkj-isv.isvjcloud.com/sign/sevenDay/signActivity"):
                self.session.headers.update(headers)

                ping_api = "https://lzkj-isv.isvjcloud.com/wxDrawActivity/getMyPing"
                user_id = bs.find(id='userId').get('value')
                data = "userId=" + user_id + "&token=" + self.session.cookies.get('wq_auth_token') + "&fromType=WeChat"
                my_ping = json.loads(self.session.post(ping_api, data=data).text)
                self.logger.info("{} getMyPing {}".format(name, str(my_ping)))

                sign_info_api = "https://lzkj-isv.isvjcloud.com/sign/sevenDay/wx/getSignInfo"
                data = "actId=" + activityId + "&venderId=" + vender_id + "&pin=" + self.session.cookies.get('pin')
                sign_info = self.session.post(sign_info_api, data=data).json()
                self.logger.info("{} getSignInfo {}".format(name, str(sign_info)))
                # {"giftConditions":[{"dayNum":"1","imgUrl":"","showType":"1","gift":{"id":"491019","giftType":"6","giftName":"1京豆","giftNum":"1","priceInfo":"0.01","shortLink":"","orginLink":null}},{"dayNum":"2","imgUrl":"","showType":"1","gift":{"id":"491019","giftType":"6","giftName":"1京豆","giftNum":"1","priceInfo":"0.01","shortLink":"","orginLink":null}},{"dayNum":"3","imgUrl":"","showType":"1","gift":{"id":"125347125","giftType":"1","giftName":"30元优惠券","giftNum":"30","priceInfo":"30.00","shortLink":"3.cn/AbmlJKg","orginLink":null}},{"dayNum":"4","imgUrl":"","showType":"1","gift":{"id":"491019","giftType":"6","giftName":"1京豆","giftNum":"1","priceInfo":"0.01","shortLink":"","orginLink":null}},{"dayNum":"5","imgUrl":"","showType":"1","gift":{"id":"491019","giftType":"6","giftName":"1京豆","giftNum":"1","priceInfo":"0.01","shortLink":"","orginLink":null}},{"dayNum":"6","imgUrl":"","showType":"1","gift":{"id":"125346736","giftType":"1","giftName":"50元优惠券","giftNum":"50","priceInfo":"50.00","shortLink":"3.cn/549ZDEh","orginLink":null}},{"dayNum":"7","imgUrl":"","showType":"1","gift":{"id":"491019","giftType":"6","giftName":"2京豆","giftNum":"2","priceInfo":"0.02","shortLink":"","orginLink":null}}],"msg":"","isOk":true,"isOver":"n","contiSignDays":1,"actRule":"1、活动时间：2019-03-18 22:12 - 2019-04-17 22:12（奖品发完，活动将会提前结束）；\n2、符合连续签到赠送条件，则赠送连续签到奖品；\n3、签到7天后不能再参加；\n4、第1天签到，赠送1京豆；\n5、第2天签到，赠送1京豆；\n6、第3天签到，赠送30元优惠券；\n7、第4天签到，赠送1京豆；\n8、第5天签到，赠送1京豆；\n9、第6天签到，赠送50元优惠券；\n10、第7天签到，赠送2京豆；\n11、本次活动如果中了任何奖品。如优惠券需要您手动领取；实物类奖品需要您主动联系卖家进行兑换；\n12、奖品数量有限，先到先得；\n","followDays":0,"isSign":"n"}

                if sign_info and sign_info['isSign'] is 'n':
                    sign_up_api = "https://lzkj-isv.isvjcloud.com/sign/sevenDay/wx/signUp"
                    data = "actId=" + activityId + "&pin=" + self.session.cookies.get('pin')
                    r = self.session.post(sign_up_api, data=data).json()
                    self.logger.info("{} 已完成签到：{}".format(name, str(r)))
                else:
                    self.logger.info("{} 今天已签到".format(name))

            else:
                self.logger.error("{} 不支持：{}".format(name, url))

        except Exception:
            self.logger.error("{} 签到发生异常".format(name))
            self.logger.exception(sys.exc_info())

    # 京东闪购签到  未完成
    def flash_sales(self):
        url = "https://red.m.jd.com/app/index.html"
        api = "https://api.m.jd.com/client.action?functionId=userSign&body=%7B%22params%22%3A%22%7B%5C%22signId%5C%22%3A%5C%2210005117%5C%22%2C%5C%22ruleSrv%5C%22%3A%5C%2200319240_14465884_t1%5C%22%2C%5C%22enActK%5C%22%3A%5C%22iI3ftbiBJ6aPULcWcVYxhZRGR9zZg%2Fp7czvUb%2BtCAWIaZs%2Fn4coLNw%3D%3D%5C%22%2C%5C%22isFloatLayer%5C%22%3Afalse%7D%22%2C%22riskParam%22%3A%7B%22platform%22%3A%223%22%2C%22orgType%22%3A%222%22%2C%22openId%22%3A%22-1%22%2C%22pageClickKey%22%3A%22Babel_Sign%22%2C%22eid%22%3A%22PJPWNCQCWCESEL4GLYPM3MVWDL2ORDOICM624REPQMJKCDD4F4V7FDVTJ72LSSY5LY37ZW5QSIHJQV5VWIAZLQ4TL4%22%2C%22fp%22%3A%2250b12fd2ee3c7061ac22f86925407557%22%2C%22shshshfp%22%3A%221292ccc50e9d288e9972ff076111a305%22%2C%22shshshfpa%22%3A%22288109af-d1fe-341d-0d01-3564fb4876e5-1530957652%22%2C%22shshshfpb%22%3A%22002d3062c344650cb83545281ef744eb8810c15f351d83a085b10edd54%22%2C%22childActivityUrl%22%3A%22https%253A%252F%252Fpro.m.jd.com%252Fmall%252Factive%252F3TTD7JhDnRxEUzepCHeGPbTxJcpF%252Findex.html%22%7D%2C%22mitemAddrId%22%3A%22%22%2C%22geo%22%3A%7B%22lng%22%3A%22%22%2C%22lat%22%3A%22%22%7D%2C%22addressId%22%3A%22%22%2C%22posLng%22%3A%22%22%2C%22posLat%22%3A%22%22%2C%22focus%22%3A%22%22%2C%22innerAnchor%22%3A%22%22%7D&screen=485*913&client=wh5&clientVersion=1.0.0&sid=b2edc6c3be1a8716568494d343b01218&uuid=1514269586558942628573&area=&_" + str(
            int(time.time() * 1000)) + "&callback=jsonp1"

        self.session.headers.update({
            'Host': 'api.m.jd.com',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': url
        })

        try:
            jsonp1 = self.session.get(api).text
            ret_json = json.loads(jsonp1[7:-1])
            self.logger.info("京东租房节签到: " + str(ret_json))
        except Exception as e:
            self.logger.error("京东租房节签到: 失败:" + str(e))

    # 京东礼品卡抽奖 未完成
    def gift_card(self):
        url = "https://pro.m.jd.com/mall/active/2nTmRwG2r7d83rQNumvf5stQzB1h/index.html"
        api = "https://api.m.jd.com/client.action?functionId=userSign&body=%7B%22params%22%3A%22%7B%5C%22signId%5C%22%3A%5C%2210005117%5C%22%2C%5C%22ruleSrv%5C%22%3A%5C%2200319240_14465884_t1%5C%22%2C%5C%22enActK%5C%22%3A%5C%22iI3ftbiBJ6aPULcWcVYxhZRGR9zZg%2Fp7czvUb%2BtCAWIaZs%2Fn4coLNw%3D%3D%5C%22%2C%5C%22isFloatLayer%5C%22%3Afalse%7D%22%2C%22riskParam%22%3A%7B%22platform%22%3A%223%22%2C%22orgType%22%3A%222%22%2C%22openId%22%3A%22-1%22%2C%22pageClickKey%22%3A%22Babel_Sign%22%2C%22eid%22%3A%22PJPWNCQCWCESEL4GLYPM3MVWDL2ORDOICM624REPQMJKCDD4F4V7FDVTJ72LSSY5LY37ZW5QSIHJQV5VWIAZLQ4TL4%22%2C%22fp%22%3A%2250b12fd2ee3c7061ac22f86925407557%22%2C%22shshshfp%22%3A%221292ccc50e9d288e9972ff076111a305%22%2C%22shshshfpa%22%3A%22288109af-d1fe-341d-0d01-3564fb4876e5-1530957652%22%2C%22shshshfpb%22%3A%22002d3062c344650cb83545281ef744eb8810c15f351d83a085b10edd54%22%2C%22childActivityUrl%22%3A%22https%253A%252F%252Fpro.m.jd.com%252Fmall%252Factive%252F3TTD7JhDnRxEUzepCHeGPbTxJcpF%252Findex.html%22%7D%2C%22mitemAddrId%22%3A%22%22%2C%22geo%22%3A%7B%22lng%22%3A%22%22%2C%22lat%22%3A%22%22%7D%2C%22addressId%22%3A%22%22%2C%22posLng%22%3A%22%22%2C%22posLat%22%3A%22%22%2C%22focus%22%3A%22%22%2C%22innerAnchor%22%3A%22%22%7D&screen=485*913&client=wh5&clientVersion=1.0.0&sid=b2edc6c3be1a8716568494d343b01218&uuid=1514269586558942628573&area=&_" + str(
            int(time.time() * 1000)) + "&callback=jsonp1"

        self.session.headers.update({
            'Host': 'api.m.jd.com',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': url
        })

        try:
            jsonp1 = self.session.get(api).text
            ret_json = json.loads(jsonp1[7:-1])
            self.logger.info("京东礼品卡抽奖: " + str(ret_json))
        except Exception as e:
            self.logger.error("京东礼品卡抽奖: 失败:" + str(e))

    # 每日抽奖签到
    def daily_draw_sign(self):
        url = "https://sale.jd.com/m/act/MD5aBJg4vL.html"
        # https://l-activity.jd.com/mobile/lottery_start.action?authType=2&lotteryCode=e1a61383-a5da-4482-9748-7d62e5f6842b&cookieValue=1728B43C20D0FD740E6590B197335294FBDE10782948A8395D42839EFFC58085&_=1552696812546&callback=Zepto1552696713687
        api = "https://l-activity.jd.com/mobile/lottery_start.action?authType=2&lotteryCode=e1a61383-a5da-4482-9748-7d62e5f6842b&cookieValue=1728B43C20D0FD740E6590B197335294FBDE10782948A8395D42839EFFC58085&_=" + str(
            int(time.time() * 1000)) + "&callback=jsonp1"

        self.session.headers.update({
            'Host': 'l-activity.jd.com',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': url
        })

        try:
            jsonp1 = self.session.get(api).text
            # jsonp1({"data":{"chances":0,"downgradeCanNotWin":false,"pass":true,"promptMsg":"很可惜没抽到","userPin":"chenbenqing530905787","winner":false},"responseCode":"0000","responseMessage":"request_success"})
            ret_json = json.loads(jsonp1[7:-1])
            self.logger.info("每日抽奖签到: " + str(ret_json))

        except Exception as e:
            self.logger.error("每日抽奖签到: 失败:" + str(e))

    # 拍拍抽奖签到
    def paipai_draw_sign(self):
        url = "https://paipai.m.jd.com/c2c/mine/coin-luck"
        # https://pp-promotion.jd.com/lottery/exchange_draw?callback=jQuery33107111196095755592_1552697080818&appBusinessId=1006&activityInfoId=10061812170267&lotteryChanceChannel=0&mpSource=4&optSource=3&_=1552697080822
        api = "https://pp-promotion.jd.com/lottery/exchange_draw?appBusinessId=1006&activityInfoId=10061812170267&lotteryChanceChannel=0&mpSource=4&optSource=3&_=" + str(
            int(time.time() * 1000)) + "&callback=jsonp1"

        self.session.headers.update({
            'Host': 'pp-promotion.jd.com',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': url
        })

        try:
            jsonp1 = self.session.get(api).text
            # /**/jsonp1({"code":1025,"message":"很抱歉，你没有中奖","result":null,"serverTime":1552697148965,"success":false});
            self.logger.info("拍拍抽奖签到: " + str(jsonp1))

        except Exception as e:
            self.logger.error("拍拍抽奖签到: 失败:" + str(e))

    # 京东企业购抽奖
    def enterprise_purchase(self):
        url = "https://pro.m.jd.com/mall/active/2XeyGsMLCH3kUs14fXFCKF1aVN5V/index.html"
        api = "https://api.m.jd.com/client.action?functionId=babelGetLottery&body=%7B%22lotteryCode%22%3A%220ff2d706-8723-42dc-8e14-68cf3aa749ed%22%2C%22authType%22%3A%222%22%2C%22riskParam%22%3A%7B%22platform%22%3A%223%22%2C%22orgType%22%3A%222%22%2C%22openId%22%3A%22-1%22%2C%22pageClickKey%22%3A%22Babel_WheelSurf%22%2C%22eid%22%3A%22PJPWNCQCWCESEL4GLYPM3MVWDL2ORDOICM624REPQMJKCDD4F4V7FDVTJ72LSSY5LY37ZW5QSIHJQV5VWIAZLQ4TL4%22%2C%22fp%22%3A%2264c1c8822353dcd4404fa61d5bd03572%22%2C%22shshshfp%22%3A%22038027b48a11ae8dd24e15b7d7575cdf%22%2C%22shshshfpa%22%3A%22288109af-d1fe-341d-0d01-3564fb4876e5-1530957652%22%2C%22shshshfpb%22%3A%22002d3062c344650cb83545281ef744eb8810c15f351d83a085b10edd54%22%2C%22childActivityUrl%22%3A%22https%253A%252F%252Fpro.m.jd.com%252Fmall%252Factive%252F2XeyGsMLCH3kUs14fXFCKF1aVN5V%252Findex.html%22%7D%2C%22mitemAddrId%22%3A%22%22%2C%22geo%22%3A%7B%22lng%22%3A%22%22%2C%22lat%22%3A%22%22%7D%2C%22addressId%22%3A%22%22%2C%22posLng%22%3A%22%22%2C%22posLat%22%3A%22%22%2C%22focus%22%3A%22%22%2C%22innerAnchor%22%3A%22%22%7D&screen=1920*540&client=wh5&clientVersion=1.0.0&sid=b2edc6c3be1a8716568494d343b01218&uuid=1514269586558942628573&area=&_=" + str(
            int(time.time() * 1000)) + "&callback=jsonp1"

        self.session.headers.update({
            'Host': 'api.m.jd.com',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': url
        })

        try:
            jsonp1 = self.session.get(api).text
            ret_json = json.loads(jsonp1[7:-1])
            self.logger.info("京东企业购抽奖: " + str(ret_json))
        except Exception as e:
            self.logger.error("京东企业购抽奖: 失败:" + str(e))


if __name__ == '__main__':
    log_format = '%(asctime)s %(name)s[%(module)s] %(levelname)s: %(message)s'
    # logging.basicConfig(filename=log_path, format=log_format, level=logging.INFO)
    logging.basicConfig(format=log_format, level=logging.INFO)
    UserSign().start()
