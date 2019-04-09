#!/usr/bin/env python 
# -*- coding:utf-8 -*-
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
from src.login import JD_Auto_Login
from src.utils.utils import update_session_cookies

"""萌犬庄园"""


class PetDog(threading.Thread):

    def __init__(self):
        super(PetDog, self).__init__(name="Pet-Dog")
        self.index_url = 'https://wqs.jd.com/pet-dog/index.html'
        self.logger = logging
        self.session = requests.session()
        self.job_success = False
        self.id = None
        self.manorId = None
        self.data = {}

        self.session.headers.update({
            'Host': 'wq.jd.com',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': self.index_url
        })

    def run(self):
        self.logger.info("Job Start :" + self.name)

        update_session_cookies(self.session, data_path / "cookies.json")

        self.get_curr_tuan_info()
        time.sleep(0.5)

        self.get_manor_info()
        time.sleep(1)

        self.get_task()

        self.logger.info("Job End :" + self.name)

    def get_curr_tuan_info(self):
        try:
            api = "https://wq.jd.com/petmanor/petquerytuan/GetCurrTuanInfo?channel=3&_=" + str(
                int(time.time() * 1000)) + "&g_login_type=0&callback=jsonpCBKA&g_ty=ls"

            r = self.session.get(api).text
            # jsonpCBKA({"data":{"confirmStatus":1,"currCount":0,"endTime":1552155687,"fullCount":10,"id":"XVcViy4xuqsTDFrOGUv-YmqNrt2JIUyfnJF3lw5YTLw","manorId":"XVcViy4xuqsTDFrOGUv-YvAYGA_bc2akYiassINF4BPBr3BzScraLPcXITBhxeJo","maxSuccessCount":10,"members":[],"remainSeconds":0,"startTime":1552069287,"status":1,"successCount":0},"errcode":0,"errmsg":"success"})
            if (r is None) or (not 'jsonpCBKA' in r):
                self.logger.error("{} get_curr_tuan_info response fail...".format(self.name))
                return
            as_json = json.loads(r[10:-1])
            self.logger.error("{} get_curr_tuan_info:{}".format(self.name, str(as_json)))

            if as_json['errcode'] != 0 or as_json['data'] is None:
                self.logger.error("{} get_curr_tuan_info data error...".format(self.name))
                return

            self.id = as_json['data']['id']
            self.manorId = as_json['data']['manorId']
        except Exception:
            self.logger.exception(sys.exc_info())

    def get_manor_info(self):
        # channel = 3 # 已知：微信 1，chrome 为 3，
        try:
            # https://wq.jd.com/petmanor/petdog/GetManorInfo?channel=3&_=1553130152101&g_login_type=0&callback=jsonpCBKC&g_tk=452613068&g_ty=ls
            api = "https://wq.jd.com/petmanor/petdog/GetManorInfo?channel=3&_=" + str(
                int(time.time() * 1000)) + "&g_login_type=0&callback=jsonpCBKC&g_ty=ls"

            r = self.session.get(api).text
            # jsonpCBKC({
            # 	"data": {
            # 		"appetite": 120,
            # 		"avatar": "http://thirdqq.qlogo.cn/g?b=oidb&k=7wf6gyRUn1dt9t7U8Mcszw&s=40",
            # 		"dogId": 1156115,
            # 		"eatCnt": 480,
            # 		"grade": 7,
            # 		"isHungry": 1,
            # 		"lastEatTime": 1553125246,
            # 		"leapRewards": [],
            # 		"manorId": "XVcViy4xuqsTDFrOGUv-YvAYGA_bc2akYiassINF4BPBr3BzScraLPcXITBhxeJo",
            # 		"neadEatCnt": 1400,
            # 		"nickname": "雄鹰的飞翔",
            # 		"otherRewards": [],
            # 		"perEatTime": 14400,
            # 		"remainEatTime": 0,
            # 		"remainFood": 0,
            # 		"stage": 2,
            # 		"type": 2,
            # 		"upRewards": [],
            # 		"validFood": 5996
            # 	},
            # 	"errcode": 0,
            # 	"msg": "success"
            # })
            if (r is None) or (not 'jsonpCBKC' in r):
                self.logger.error("{} get_manor_info response fail...".format(self.name))
                return
            as_json = json.loads(r[10:-1])
            self.logger.error("{} get_manor_info:{}".format(self.name, str(as_json)))
            if as_json['errcode'] == 5000:  # and as_json['errmsg'] is u'未登录':
                self.logger.error("{} {} please re-login...".format(self.name, as_json['msg']))
                JD_Auto_Login().auto_login()
                time.sleep(2)
                self.run()
                return

            if as_json['errcode'] != 0 or as_json['data'] is None:
                self.logger.error("{} get_manor_info data error...".format(self.name))
                return

            self.data = as_json['data']
            self.logger.info("{} : grade {},appetite {},perEatTime {},remainEatTime {}:{},neadEatCnt {} to upgrade...".format(self.name, str(
                self.data['grade']), str(self.data['appetite']), str(self.data['perEatTime'] // 3600), str(
                self.data['remainEatTime'] // 3600), str(int(self.data['remainEatTime']) % 60), str(
                self.data['neadEatCnt'] - self.data['eatCnt'])))

            if self.data['isHungry'] == 1:
                self.logger.info("{} pet dog hungry...".format(self.name))
                self.feed_dog()

            if self.data['remainFood'] > 0:
                self.gain_dog_food()

        except Exception:
            self.logger.exception(sys.exc_info())

    def feed_dog(self):
        try:
            # https://wq.jd.com/petmanor/petopr/FeedDog?manorId=&channel=3&_=1553691624147&g_login_type=0&callback=jsonpCBKM&g_tk=1657396594&g_ty=ls
            api = "https://wq.jd.com/petmanor/petopr/FeedDog?manorId=&channel=3&_=" + str(
                int(time.time() * 1000)) + "&g_login_type=0&callback=jsonpCBKE&g_ty=ls"

            r = self.session.get(api).text
            # jsonpCBKE({
            # 	"data": {
            # 		"foodCnt": 120,
            # 		"validFood": 5876
            # 	},
            # 	"errcode": 0,
            # 	"errmsg": "success"
            # })
            if (r is None) or (not 'jsonpCBKE' in r):
                self.logger.error("{} feed_dog response fail...".format(self.name))
                return

            as_json = json.loads(r[10:-1])
            if as_json['errcode'] != 0 or as_json['data'] is None:
                self.logger.error("{} feed_dog data error...".format(self.name))
                return

            self.logger.info("{} feed food:{},remind food:{}".format(self.name, str(as_json['data']['foodCnt']),
                                                     str(as_json['data']['validFood'])))
        except Exception:
            self.logger.exception(sys.exc_info())

    def take_dog_food(self, type):
        try:
            # https://wq.jd.com/petmanor/petmodule/TakeDogFood?type=2&channel=3&_=1553133563270&g_login_type=0&callback=jsonpCBKF&g_tk=452613068&g_ty=ls
            api = "https://wq.jd.com/petmanor/petmodule/TakeDogFood?type=" + type + "&channel=3&_=" + str(
                int(time.time() * 1000)) + "&g_login_type=0&callback=jsonpCBKF&g_ty=ls"

            r = self.session.get(api).text
            # jsonpCBKF({
            # 	"data": {
            # 		"foodCnt": 30
            # 	},
            # 	"errcode": 0,
            # 	"msg": "success"
            # })
            if (r is None) or (not 'jsonpCBKF' in r):
                self.logger.error("{} take_dog_food reponse error...".format(self.name))
                return

            as_json = json.loads(r[10:-1])
            if as_json['errcode'] != 0 or as_json['data'] is None:
                self.logger.error("{} take_dog_food data error...".format(self.name))
                return

            self.logger.info("{} take_dog_food {}".format(self.name, str(as_json['data']['foodCnt'])))
        except Exception:
            self.logger.exception(sys.exc_info())

    def gain_dog_food(self):
        try:
            # https://wq.jd.com/petmanor/petopr/GainDogFood?manorId=&channel=3&_=1553691043132&g_login_type=0&callback=jsonpCBKJ&g_tk=1657396594&g_ty=ls
            api = "https://wq.jd.com/petmanor/petopr/GainDogFood?manorId=&channel=3&_=" + str(
                int(time.time() * 1000)) + "&g_login_type=0&callback=jsonpCBKF&g_ty=ls"

            r = self.session.get(api).text
            # jsonpCBKF({
            # 	"data": {
            # 		"foodCnt": 180,
            # 		"oversteallimit": 0,
            # 		"validFood": 7258
            # 	},
            # 	"errcode": 0,
            # 	"errmsg": "success"
            # }
            if (r is None) or (not 'jsonpCBKF' in r):
                self.logger.error("{} gain_dog_food response fail...".format(self.name))
                return

            as_json = json.loads(r[10:-1])
            if as_json['errcode'] != 0 or as_json['data'] is None:
                self.logger.error("{} gain_dog_food data error...".format(self.name))
                return

            self.logger.info("{} gain_dog_food {}，remaind food: {}".format(self.name, str(as_json['data']['foodCnt']),
                                                            str(as_json['data']['validFood'])))
        except Exception:
            self.logger.exception(sys.exc_info())

    def get_task(self):
        try:
            # https://wq.jd.com/petmanor/petmodule/GetTask?channel=3&_=1553130153584&g_login_type=0&callback=jsonpCBKE&g_tk=452613068&g_ty=ls
            api = "https://wq.jd.com/petmanor/petmodule/GetTask?channel=3&_=" + str(
                int(time.time() * 1000)) + "&g_login_type=0&callback=jsonpCBKD&g_ty=ls"

            r = self.session.get(api).text
            # jsonpCBKD({
            # 	"data": {
            # 		"curShareCnt": 0,
            # 		"curShopCnt": 0,
            # 		"curViewCnt": 2,
            # 		"shareFood": 0,
            # 		"shareRewardMax": 80,
            # 		"shareRewardMin": 50,
            # 		"shopFood": 0,
            # 		"shopReward": 288,
            # 		"totalShareCnt": 5,
            # 		"totalShopCnt": 3,
            # 		"totalViewCnt": 3,
            # 		"viewFood": 30,
            # 		"viewReward": 30
            # 	},
            # 	"errcode": 0,
            # 	"msg": "success"
            # })
            if (r is None) or (not 'jsonpCBKD' in r):
                self.logger.error("{} get_task response fail...".format(self.name))
                return

            as_json = json.loads(r[10:-1])
            self.logger.info("{} get_task: {}".format(self.name, str(as_json)))
            if as_json['errcode'] != 0 or as_json['data'] is None:
                self.logger.error("{} get_task data error...".format(self.name))
                return

            data = as_json['data']
            remindShareTask = data['totalShareCnt'] - data['curShareCnt']
            remindViewTask = data['totalViewCnt'] - data['curViewCnt']
            remindShopTask = data['totalShopCnt'] - data['curShopCnt']

            self.logger.info(
                "{} get_task：share: {} ，shopping: {}，view: {}".format(self.name, str(remindShareTask), str(remindShopTask),
                                                    str(remindViewTask)))
            if remindViewTask == 3:
                self.session.get("https://wq.jd.com/sqportal/index_v7?ptag=138488.4.7")
            elif remindViewTask == 2:
                self.session.get("https://wqs.jd.com/portal/wx/tuan/pingou_list.shtml?ptag=138488.4.8")
            elif remindViewTask == 1:
                self.session.get("https://wqs.jd.com/pingou/superior_goods.shtml?ptag=138488.4.9")

            time.sleep(2)
            self.get_manor_info()

        except Exception:
            self.logger.exception(sys.exc_info())


if __name__ == '__main__':
    log_format = '%(asctime)s %(name)s[%(module)s] %(levelname)s: %(message)s'
    # logging.basicConfig(filename=log_path, format=log_format, level=logging.INFO)
    logging.basicConfig(format=log_format, level=logging.INFO)

    PetDog().start()
