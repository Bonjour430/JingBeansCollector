#!/usr/bin/env python 
# -*- coding:utf-8 -*-

"""种豆得豆 活动"""
import json
import logging
import os
import sys

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

import threading
import time

import requests

from src.config import data_path
from src.utils.utils import update_session_cookies

ua_wechat = "Mozilla/5.0 (Linux; Android 8.0; DUK-AL20 Build/HUAWEIDUK-AL20; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/6.2 TBS/044353 Mobile Safari/537.36 MicroMessenger/6.7.3.1360(0x26070333) NetType/WIFI Language/zh_CN Process/tools"


class PlantBean(threading.Thread):

    def __init__(self):
        super(PlantBean, self).__init__(name='Plant-Bean')
        self.index_url = 'https://bean.m.jd.com/plantBean/index.action?resourceValue=bean'
        self.logger = logging
        self.session = requests.Session()
        self.job_success = False
        self.round_id = None

    def run(self):
        self.logger.info("Job Start :" + self.name)

        update_session_cookies(self.session, data_path / "cookies.json")

        self.plant_bean_index()

    def plant_bean_index(self):
        try:
            body = {"monitor_refer": "", "wxHeadImgUrl": "", "shareUuid": "", "monitor_source": "plant_m_plant_index"}
            api = "https://api.m.jd.com/client.action?functionId=plantBeanIndex&body=" + json.dumps(
                body) + "&appid=ld&client=android&clientVersion=&networkType=&osVersion=&uuid=&jsonp=jsonp"

            self.session.headers.update({
                'Host': 'api.m.jd.com',
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            })

            ret = self.session.get(api).text
            if ret is None or 'jsonp' not in ret:
                self.logger.error("{} plant_bean_index reponse fail...".format(self.name))
                return

            ret_json = json.loads(ret[6:-2])
            self.logger.info("{} plant_bean_index: {}".format(self.name, str(ret_json)))
            code = ret_json['code']
            if code is not '0':
                self.logger.error('{} plant_bean_index data error...'.format(self.name))
                return

            data = ret_json['data']

            preRound = None  # 前一轮游戏
            curRound = None  # 当前游戏

            for round in data['roundList']:
                if round['roundState'] is '1':
                    preRound = round
                if round['roundState'] is '2':
                    curRound = round

            if not (preRound and curRound):
                self.logger.error(self.name + " plant_bean_index data error...")

            self.round_id = curRound['roundId']
            if int(curRound['nutrients']) > 0:
                # 可培养
                self.logger.info("{} have {} nutrients to culture...".format(self.name, curRound['nutrients']))
                self.culture_bean()

            if preRound['awardState'] is '4':  # 领取奖励状态，‘6’表示已经领取，‘4’奖励已产生，还未领取，‘1’还在培养中，未产生奖励
                self.received_bean(preRound['roundId'])

            elif preRound['awardState'] is '6':
                self.logger.info(
                    "{} get {} beans at the preRound game....".format(self.name, str(preRound['awardBeans'])))

            for award in data['awardList']:
                limitFlag = award['limitFlag']
                awardName = award['awardName']
                awardType = award['awardType']  # 1 每日签到,2 邀请好友, 3 浏览店铺, 4 宠物生活 逛会场

                if awardType is '1':
                    if limitFlag is '2':  # '2' 表示该项blocked, '1' 该项可继续进行
                        self.logger.info("{} {} done...".format(self.name, str(awardName)))
                    elif limitFlag is '1':
                        self.logger.info("{} {} need to do...".format(self.name, str(awardName)))

                if awardType is '3':
                    if limitFlag is '2':  # '2' 表示该项blocked, '1' 该项可继续进行
                        self.logger.info("{} {} done...".format(self.name, str(awardName)))
                    elif limitFlag is '1':
                        self.shop_task_list()

                if awardType is '4':
                    if limitFlag is '2':  # '2' 表示该项blocked, '1' 该项可继续进行
                        self.logger.info("{} view venue done...".format(self.name))
                    elif limitFlag is '1':
                        self.guang_hui_chang(award['linkUrl'])

            state = data['timeNutrientsRes']['state']  # 风车收集瓶的状态，‘1’ 为瓶中有可收集的营养液，‘3’ 正在产生中
            if state is '1':
                self.logger.info("{} 风车已产生".format(self.name))
                self.receive_nutrients()

            for i in range(1, 4):
                self.plant_friend_list(i)

            self.logger.info("Job End.")
        except Exception:
            self.logger.exception(sys.exc_info())

    def received_bean(self, round_id):
        try:
            body = {"roundId": round_id, "monitor_source": "plant_m_plant_index", "monitor_refer": "plant_index"}
            api = "https://api.m.jd.com/client.action?functionId=receivedBean&body=" + json.dumps(
                body) + "&appid=ld&client=android&clientVersion=&networkType=&osVersion=&uuid=&jsonp=jsonp"

            self.session.headers.update({
                'Host': 'api.m.jd.com',
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': "https://bean.m.jd.com/AttentionStore",
                'user-agent': "Mozilla/5.0 (Linux; Android 8.0; DUK-AL20 Build/HUAWEIDUK-AL20; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/6.2 TBS/044353 Mobile Safari/537.36 MicroMessenger/6.7.3.1360(0x26070333) NetType/WIFI Language/zh_CN Process/tools"
            })

            ret = self.session.get(api).text

            if not ret or ("jsonp" not in ret):
                self.logger.error("{} received_bean error...".format(self.name))
                return

            ret_json = json.loads(ret[6:-2])
            self.logger.info("{} received_bean {}".format(self.name, str(ret_json)))
            code = ret_json['code']
            if code is not '0':
                self.logger.error("{} received_bean fail".format(self.name))
                return

            self.logger.info("{} preRound growth: {}，awardBean: {}".format(self.name, ret_json['data']['growth'],
                                                                 ret_json['data']['awardBean']))
        except Exception:
            self.logger.exception(sys.exc_info())

    # 浏览店铺，获取待浏览的店铺列表
    def shop_task_list(self):
        try:
            body = {"monitor_source": "plant_m_plant_index", "monitor_refer": "plant_shopList"}
            api = "https://api.m.jd.com/client.action?functionId=shopTaskList&body=" + json.dumps(
                body) + "&appid=ld&client=android&clientVersion=&networkType=&osVersion=&uuid=&jsonp=jsonp"

            self.session.headers.update({
                'Host': 'api.m.jd.com',
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': "https://bean.m.jd.com/AttentionStore",
                'user-agent': ua_wechat
            })

            ret = self.session.get(api).text
            ret_json = json.loads(ret[6:-2])
            self.logger.info("{} shop_task_list {}".format(self.name, str(ret_json)))
            code = ret_json['code']
            if code is not '0':
                self.logger.error("{} shop_task_list fail".format(self.name))
                return

            data = ret_json['data']
            goodShopList = data['goodShopList']
            moreShopList = data['moreShopList']

            for shop in goodShopList:
                if shop['taskState'] is '2':  # 可领取状态，‘1’为已领取状态
                    self.shop_nutrients_task(shop['shopTaskId'], shop['shopId'])

                    time.sleep(1)
                    self.plant_bean_index()
                    return

            for shop in moreShopList:
                if shop['taskState'] is '2':  # 可领取状态，‘1’为已领取状态
                    self.shop_nutrients_task(shop['shopTaskId'], shop['shopId'])

                    time.sleep(1)
                    self.plant_bean_index()
                    return
        except Exception:
            self.logger.exception(sys.exc_info())

    def shop_nutrients_task(self, task_id, shop_id):
        try:
            body = {"shopTaskId": task_id, "shopId": shop_id, "monitor_source": "plant_m_plant_index",
                    "monitor_refer": "plant_shopNutrientsTask"}
            api = "https://api.m.jd.com/client.action?functionId=shopNutrientsTask&body=" + json.dumps(
                body) + "&appid=ld&client=android&clientVersion=&networkType=&osVersion=&uuid=&jsonp=jsonp"

            self.session.headers.update({
                'Host': 'api.m.jd.com',
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': "https://bean.m.jd.com/AttentionStore",
                'user-agent': ua_wechat
            })

            ret = self.session.get(api).text
            self.logger.info("{} shop_nutrients_task:{}".format(self.name, ret))
        except Exception:
            self.logger.exception(sys.exc_info())

    # 逛会场得营养液
    def guang_hui_chang(self, url):
        try:
            body = {"roundId": self.round_id, "monitor_source": "plant_m_plant_index",
                    "monitor_refer": "plant_purchaseRewardTask"}
            api = "https://api.m.jd.com/client.action?functionId=purchaseRewardTask&body=" + json.dumps(
                body) + "&appid=ld&client=android&clientVersion=&networkType=&osVersion=&uuid=&jsonp=jsonp"

            self.session.headers.update({
                'Host': 'api.m.jd.com',
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'referer': self.index_url,
                'user-agent': ua_wechat
            })

            ret = self.session.get(api).text
            ret_json = json.loads(ret[6:-2])
            self.logger.info("{} guang_hui_chang {}".format(self.name, str(ret_json)))

            time.sleep(1)
            self.plant_bean_index()

        except Exception:
            self.logger.exception(sys.exc_info())

    # 收集风车营养液
    def receive_nutrients(self):
        try:
            body = {"roundId": self.round_id, "monitor_source": "plant_m_plant_index",
                    "monitor_refer": "plant_receiveNutrients"}
            api = "https://api.m.jd.com/client.action?functionId=receiveNutrients&body=" + json.dumps(
                body) + "&appid=ld&client=android&clientVersion=&networkType=&osVersion=&uuid=&jsonp=jsonp"

            self.session.headers.update({
                'Host': 'api.m.jd.com',
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'referer': self.index_url,
                'user-agent': ua_wechat
            })

            ret = self.session.get(api).text
            ret_json = json.loads(ret[6:-2])
            if ret_json['code'] is '0':
                # nextReceiveTime = ret_json['data']['nextReceiveTime']
                self.logger.info("{} receive_nutrients success".format(self.name))

            time.sleep(1)
            self.plant_bean_index()

        except Exception:
            self.logger.exception(sys.exc_info())

    # 培养豆子
    def culture_bean(self):
        try:
            body = {"roundId": self.round_id, "monitor_source": "plant_m_plant_index", "monitor_refer": "plant_index"}
            api = "https://api.m.jd.com/client.action?functionId=cultureBean&body=" + json.dumps(
                body) + "&appid=ld&client=android&clientVersion=&networkType=&osVersion=&uuid=&jsonp=jsonp"

            self.session.headers.update({
                'Host': 'api.m.jd.com',
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'referer': self.index_url,
                'user-agent': ua_wechat
            })

            ret = json.loads((self.session.get(api).text)[6:-2])
            if ret and ret['code'] is '0':
                self.logger.info("{} current growth {}".format(self.name, ret['data']['growth']))
            else:
                self.logger.error("{} culture_bean fail...")

            time.sleep(1)
            self.plant_bean_index()

        except Exception:
            self.logger.exception(sys.exc_info())

    def plant_friend_list(self, page_num):
        try:
            body = {"pageNum": str(page_num), "monitor_source": "plant_m_plant_index",
                    "monitor_refer": "plantFriendList"}
            api = "https://api.m.jd.com/client.action?functionId=plantFriendList&body=" + json.dumps(
                body) + "&appid=ld&client=android&clientVersion=&networkType=&osVersion=&uuid=&jsonp=jsonp"

            self.session.headers.update({
                'Host': 'api.m.jd.com',
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'referer': self.index_url,
                'user-agent': ua_wechat
            })
            response = self.session.get(api).text
            if response is None or 'jsonp' not in response:
                self.logger.error("{} plant_friend_list: get response error...".format(self.name))
                return

            ret = json.loads(response[6:-2])
            self.logger.info("{} plant_friend_list: {}".format(self.name, str(ret)))
            if ret and ret['code'] is '0':
                if 'errorMessage' in response or 'data' not in response:
                    self.logger.error("{} plant_friend_list: {}".format(self.name, str(ret['errorMessage'])))
                    return

                friends = ret['data']['friendInfoList']
                for friend in friends:
                    if friend['userType'] is '1' and friend['nutrCount'] is '3':
                        self.collect_user_nutr(friend['paradiseUuid'])
            else:
                self.logger.error("plant_friend_list failed...")

        except Exception:
            logging.exception(sys.exc_info())

    def collect_user_nutr(self, paradise_uuid):
        try:
            body = {"paradiseUuid": paradise_uuid, "roundId": self.round_id, "monitor_source": "plant_m_plant_index",
                    "monitor_refer": "collectUserNutr"}
            api = "https://api.m.jd.com/client.action?functionId=collectUserNutr&body=" + json.dumps(
                body) + "&appid=ld&client=android&clientVersion=&networkType=&osVersion=&uuid=&jsonp=jsonp"

            refer_url = "https://bean.m.jd.com/FriendParadise?paradiseUuid=" + paradise_uuid + "&roundId=" + self.round_id

            self.session.headers.update({
                'Host': 'api.m.jd.com',
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'referer': refer_url,
                'user-agent': ua_wechat
            })

            response = self.session.get(api).text
            if response is None or 'jsonp' not in response:
                self.logger.error("{} collect_user_nutr: get response error...".format(self.name))
                return

            ret = json.loads(response[6:-2])
            self.logger.info("{} collect_user_nutr:{}".format(self.name, str(ret)))

            if ret['code'] is '0':
                if 'errorMessage' in response or 'data' not in response:
                    self.logger.error("{} collect_user_nutr: {}".format(self.name, str(ret['errorMessage'])))
                    return

                data = ret['data']
                if data['collectResult'] is '1':
                    self.logger.info("{} get {} nutrients...".format(self.name, data['collectNutrRewards']))
                elif data['collectResult'] is '3':
                    self.logger.info("{} {}".format(self.name, data['collectMsg']))
        except Exception:
            self.logger.exception(sys.exc_info())

    def get_login_pin(self):
        try:
            api = "https://api.m.jd.com/client.action?appid=JDReactToWeb&functionId=getLoginPin&body=%5Bobject%20Object%5D&t=" + str(
                int(time.time() * 1000)) + "&jsonp=jsonp"
            self.session.headers.update({
                'Host': 'api.m.jd.com',
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'referer': self.index_url,
                'user-agent': ua_wechat
            })
            response = self.session.get(api).text
            if response is None or 'jsonp' not in response:
                self.logger.error("{} get_login_pin: get response error...".format(self.name))
                return False

            ret = json.loads(response[6:-2])
            if ret['success'] and len(ret['data']) > 0:
                self.logger.info("{} get_login_pin: success")
                return True
            else:
                return False
        except Exception:
            self.logger.exception(sys.exc_info())
            return False


if __name__ == '__main__':
    log_format = '%(asctime)s %(name)s[%(module)s] %(levelname)s: %(message)s'
    # logging.basicConfig(filename=log_path, format=log_format, level=logging.INFO)
    logging.basicConfig(format=log_format, level=logging.INFO)
    PlantBean().start()
