#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import json
import logging
import sys
import time
from urllib.parse import splitquery, parse_qs

import requests
from bs4 import BeautifulSoup
from requests import Session


def query_shop_gift(session: Session, vender_id):
    """查询店铺活动-新人礼包"""
    if session is None or vender_id is None or vender_id is '':
        logging.error("query_shop_gift: params error...")
        return

    try:
        api = "http://wq.jd.com/mjgj/column/QueryShopGiftList?sceneval=2&g_login_type=1&callback=jsonpCBKG&g_ty=ls&channel=7&venderId=" \
              + str(vender_id) + "&_=" + str(int(time.time() * 1000))

        headers = {
            'Host': 'wq.jd.com',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': "https://wqshop.jd.com/mshop/gethomepage?venderid=" + vender_id
        }

        session.headers.update(headers)

        jsonpCBKG = session.get(api).text

        if jsonpCBKG is None or 'jsonpCBKG' not in jsonpCBKG:
            logging.error("query_shop_gift: get response error...")
            return

        gift_json = json.loads(jsonpCBKG[10:-2])
        logging.info("query_shop_gift:{}".format(str(gift_json)))

        errcode = gift_json["errcode"]  # errcode : 0 表示成功，其他异常码，例 13 表示未登录
        gift_list = gift_json["shopgift"]  # shopgift 店铺礼物列表
        isvOrofficial = gift_json["isvOrofficial"]  # 礼物弹窗形式，默认为0，1表示使用内置官方的弹窗形式，2表示活动链接形式
        isvActivityLink = gift_json["isvActivityLink"]

        if errcode == 0 and gift_list and len(gift_list) > 0:
            if isvActivityLink and isvOrofficial == 2:
                shop_gift_from_activity_link(session, vender_id, isvActivityLink)
            else:
                for gift in gift_list:
                    if gift["prizeType"] == "4":  # 4 为京豆,1 为店铺东券,6 为店铺积分
                        logging.info("query_shop_gift: get beans {}".format(gift["discount"]))
                        shop_gift_from_official(session, vender_id, gift["activityId"])
                        # gift_content = "{}: 获得京豆 {}".format(gift_content, json_str["discount"])
                    # elif json_str["prizeType"] == "6":
                    #     gift_content = "{}: 店铺积分 {}".format(gift_content, json_str["discount"])
                    # elif json_str["prizeType"] == "1":
                    #     gift_content = "{}: 店铺东券: 满{}减{}".format(gift_content, json_str["quota"],
                    #                                              json_str["discount"])

        elif errcode == 201:
            # shop gift have been draw
            logging.info("query_shop_gift:{} ".format(str(gift_json['msg'])))
        elif errcode == 13:
            logging.info("query_shop_gift:{} please re-login...".format(str(gift_json['msg'])))
            # # no login
            # JD_Auto_Login().auto_login()
            # time.sleep(2)
            #
            # update_session_cookies(self.session, data_path / "cookies.json")
            #
            # self.run()
        elif errcode == 402:
            # no prize
            logging.info("query_shop_gift:{} ".format(str(gift_json['msg'])))
        elif errcode == 100:
            # sys error
            logging.info("query_shop_gift:{} ".format(str(gift_json['msg'])))

    except Exception:
        logging.exception(sys.exc_info())


def shop_gift_from_activity_link(session: Session, vender_id, activity_link):
    """收取新人礼-活动链接"""
    if session is None or vender_id is None or activity_link is None:
        logging.error("shop_gift_from_activity_link:params error...")
        return False
    # https://lzkj-isv.isvjcloud.com/wxShopGift/activity?activityId=2bbae234626742069a604ae1de043da5

    logging.info("shop_gift_from_activity_link:{}".format(activity_link))
    path_part, query_part = splitquery(activity_link)
    logging.info("shop_gift_from_activity_link:{}".format(path_part))

    if path_part == "https://lzkj-isv.isvjcloud.com/wxShopGift/activity":
        # https://lzkj-isv.isvjcloud.com/wxShopGift/activity?activityId=623eb7fbbca541d7ad967411bfd68ad1
        try:
            bs = BeautifulSoup(requests.get(activity_link).text, 'html.parser')
            user_id = bs.find(id='userId').get('value')

            headers = {
                'Host': 'lzkj-isv.isvjcloud.com',
                'Origin': 'https://lzkj-isv.isvjcloud.com',
                'Accept': 'application/json',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': activity_link
            }
            session.headers.update(headers)

            api = "https://lzkj-isv.isvjcloud.com/wxDrawActivity/getMyPing"
            data = "userId=" + user_id + "&token=" + session.cookies.get('wq_auth_token') + "&fromType=WeChat"
            my_ping = session.post(api, data=data).text
            # {"result":true,"data":"chenbenqing530905787","count":0,"errorMessage":""}
            # {"result":false,"data":"pin get error","count":0,"errorMessage":"获取账户转换信息出错，请重新进入一次"}
            logging.info("shop_gift_from_activity_link getMyPing {}".format(str(my_ping)))

            api = "https://lzkj-isv.isvjcloud.com/wxShopGift/activityContent"
            activity_id = parse_qs(query_part).get('activityId')[0]
            data = "activityId=" + activity_id + "&buyerPin=" + session.cookies.get('pin')

            content = json.loads(session.post(api, data=data).text)
            logging.info("shop_gift_from_activity_link activityContent:{}".format(str(content)))
            hasFollow = False
            if content['result']:
                data = content['data']
                hasFollow = data['hasFollow']
                gift_list = data['list']
                gift_content = ' 获取到'
                for gift in gift_list:
                    if gift['type'] is 'jd':
                        logging.info("shop_gift_from_activity_link get beans:{}".format(str(gift['takeNum'])))

            # {"result":true,"data":{"id":"d405589a5e1549ef9021cc181e0850a3","userId":1000001996,"venderType":1,"endTime":1554047940000,"list":[{"type":"jd","takeNum":10,"discount":"","quota":""},{"type":"jf","takeNum":20,"discount":"","quota":""}],"hasFollow":false},"count":0,"errorMessage":""}
            # {"result":true,"data":{"id":"8aee90f2ea194a23922af9fb8bb70a4b","userId":1000013741,"venderType":1,"endTime":1553824800000,"list":[{"type":"jd","takeNum":2,"discount":"","quota":""}],"hasFollow":false},"count":0,"errorMessage":""}
            # {"result":true,"data":{"id":"b32b18a1407e493cb2f21154bbb749a7","userId":1000008142,"venderType":1,"endTime":1553563140000,"list":[{"type":"jd","takeNum":2,"discount":"","quota":""}],"hasFollow":false},"count":0,"errorMessage":""}

            api = "https://lzkj-isv.isvjcloud.com/wxShopGift/draw"
            data = "activityId=" + activity_id + "&buyerPin=" + session.cookies.get('pin') + "&hasFollow=" + str(
                hasFollow) + "&accessType="
            # {"result":true,"data":"000000","count":0,"errorMessage":"通用成功代码"}
            # {"result":false,"data":"000015","count":0,"errorMessage":"您的店铺礼包奖品已经发放，请您不要重复领取！"}
            draw = json.loads(session.post(api, data=data).text)
            logging.info("shop_gift_from_activity_link draw: {}".format(draw))

            return True
        except Exception:
            logging.exception(sys.exc_info())
            return False

    elif path_part == "https://gzsl-isv.isvjcloud.com/wuxian/mobileForApp/dist/views/pages/shopGiftBag.html":
        # https://gzsl-isv.isvjcloud.com/wuxian/mobileForApp/dist/views/pages/shopGiftBag.html?activityType=DPHB_1&activityId=1000075981
        try:
            activityType = parse_qs(query_part).get('activityType')[0]
            activityId = parse_qs(query_part).get('activityId')[0]
            activityType = activityType + "_" + activityId
            token = session.cookies.get('wq_auth_token')

            api = "https://gzsl-isv.isvjcloud.com/wuxian/user/getShopGiftActivity/" + activityId
            refer_link = "https://gzsl-isv.isvjcloud.com/wuxian/mobileForApp/dist/views/pages/shopGiftBag.html?" \
                         "activityType=" + activityType + "&token=" + token
            headers = {
                'Host': 'gzsl-isv.isvjcloud.com',
                'Origin': 'https://gzsl-isv.isvjcloud.com',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Content-Type': 'application/json;charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': refer_link
            }
            session.headers.update(headers)

            payload = {'venderId': activityId}
            ret_json = json.loads(session.post(api, json=payload).text)
            logging.info("shop_gift_from_activity_link getShopGiftActivity: {}".format(str(ret_json)))
            if ret_json['isTake']:
                logging.info("shop_gift_from_activity_link gift isTake...")
                return True

            api = "https://gzsl-isv.isvjcloud.com/wuxian/user/getShopGiftPrize/" + str(
                ret_json['activity']['id']) + "?wxToken=" + token
            data = {'activityId': ret_json['activity']['id'], 'wxToken': token}

            gift_json = json.loads(session.post(api, json=data).text)
            logging.debug("shop_gift_from_activity_link getShopGiftPrize: {}".format(str(gift_json)))
            logging.info("shop_gift_from_activity_link getShopGiftPrize: {}".format(str(gift_json['data'])))
            return True
        except Exception:
            logging.exception(sys.exc_info())
            return False

    else:
        logging.error("shop_gift_from_activity_link unsupport link....")
        return False


def shop_gift_from_official(session: Session, vender_id, activity_id):
    """获取新人礼-official"""
    if session is None or vender_id is None or activity_id is None:
        logging.error("shop_gift_from_official:params error...")
        return False

    try:
        api = "https://wq.jd.com/mjgj/column/DrawShopGift?channel=7&sceneval=2&g_login_type=1&callback=jsonpCBKK&g_ty=ls&venderId=" \
              + vender_id + "&activityId=" + activity_id + "&_=" + str(int(time.time() * 1000))
        headers = {
            'Host': 'wq.jd.com',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': "https://wqshop.jd.com/mshop/gethomepage?venderid=" + vender_id
        }

        session.headers.update(headers)
        jsonpCBKK = session.get(api).text

        if jsonpCBKK and 'jsonpCBKK' in jsonpCBKK:
            gift_json = json.loads(str(jsonpCBKK[10:-2]))
            logging.info("shop_gift_from_official:{}".format(str(gift_json)))

            if gift_json["errcode"] == 0:
                logging.info("shop_gift_from_official: {}".format(str(gift_json['msg'])))
                return True

        return False
    except Exception:
        logging.exception(sys.exc_info())
        return False


def query_shop_active(session: Session, vender_id):
    """查询店铺活动-收藏有礼"""
    if session is None or vender_id is None or vender_id is '':
        logging.error("query_shop_active: params error...")
        return

    try:
        # https://wq.jd.com/fav_snsgift/QueryShopActive?venderId=654365&_=1551837204756&sceneval=2&g_login_type=1&callback=jsonpCBKC&g_tk=270919183&g_ty=ls
        api = "https://wq.jd.com/fav_snsgift/QueryShopActive?sceneval=2&g_login_type=1&callback=jsonpCBKC&g_ty=ls" \
              "&venderId=" + str(vender_id) + "&_=" + str(int(time.time() * 1000))

        headers = {
            'Host': 'wq.jd.com',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': 'https://wqshop.jd.com/mshop/gethomepage?venderid=' + vender_id
        }

        session.headers.update(headers)
        jsonpCBKC = session.get(api).text
        if jsonpCBKC is None or 'jsonpCBKC' not in jsonpCBKC:
            logging.error("query_shop_active: get response error...")

        gift_json = json.loads(jsonpCBKC[14:-13])
        logging.info("query_shop_active: {}".format(str(gift_json)))
        # {'errMsg': '', 'fan': 0, 'gift': None, 'helpFav': 0, 'iRet': '0'}

        if gift_json['iRet'] == '13':  # no login
            logging.info("query_shop_active：{}".format(gift_json['errMsg']))
            # JD_Auto_Login().auto_login()
            # time.sleep(2)
            #
            # update_session_cookies(self.session, data_path / "cookies.json")
            # self.run()
        elif gift_json['iRet'] == '0':
            gift_list = gift_json["gift"]
            if gift_list and len(gift_list) > 0:
                for gift in gift_list:
                    if gift['state'] == 1:  # 1 为可领取，4 为已领取
                        shop_active_add_fav(session, vender_id)
                        time.sleep(0.5)
                        shop_active_give_gift(session, vender_id, gift['activeId'], gift['giftId'])
                    elif gift['state'] == 4:
                        logging.info("query_shop_active: this gift have been draw...")
                    elif gift['state'] == 0:
                        logging.info("query_shop_active: this gift expired...")
                    else:
                        logging.info("query_shop_active：{}".format(str(gift_json)))
            else:
                logging.info("query_shop_active: no gift...")
        else:
            logging.info("query_shop_active error: {}".format(str(gift_json)))

    except Exception:
        logging.exception(sys.exc_info())


def shop_active_add_fav(session: Session, vender_id):
    """收藏有礼-收藏"""
    if session is None or vender_id is None:
        logging.error("shop_active_add_fav: params error...")
        return

    try:
        api = "https://wq.jd.com/fav_snsgift/addfavgiftshop?shareToken=&sceneval=2&g_login_type=1&callback=jsonpCBKN&g_tk=1018150000&g_ty=ls&venderId=" \
              + vender_id + "&_=" + str(int(time.time() * 1000))
        headers = {
            'Host': 'wq.jd.com',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': 'https://wqshop.jd.com/mshop/gethomepage?venderid=' + vender_id
        }
        session.headers.update(headers)

        jsonpCBKN = session.get(api).text
        # try{jsonpCBKN({"errMsg" : "success","iRet" : "0"});}catch(e){}
        if jsonpCBKN is None or 'jsonpCBKN' not in jsonpCBKN:
            logging.error("shop_active_add_fav: get response error...")
            return

        fav_json = json.loads(jsonpCBKN[14:-13])
        logging.info("shop_active_add_fav:{}".format(str(fav_json)))
    except Exception:
        logging.exception(sys.exc_info())


def shop_active_give_gift(session: Session, vender_id, active_id, gift_id):
    """收藏有礼-收礼"""
    if session is None or vender_id is None or active_id is None or gift_id is None:
        logging.error("shop_active_give_gift: params error...")
        return

    try:
        api = "https://wq.jd.com/fav_snsgift/GiveShopGift?sceneval=2&g_login_type=1&callback=jsonpCBKP&g_ty=ls&venderId=" \
              + vender_id + "&activeId=" + active_id + "&giftId=" + gift_id + "&_=" + str(int(time.time() * 1000))
        headers = {
            'Host': 'wq.jd.com',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': 'https://wqshop.jd.com/mshop/gethomepage?venderid=' + vender_id
        }
        session.headers.update(headers)
        jsonpCBKP = session.get(api).text
        # try{jsonpCBKP({"errMsg" : "success","iRet" : "0"});}catch(e){}
        # try{jsonpCBKP({
        #    "errMsg" : "",
        #    "retCode" : 402
        # }
        # );}catch(e){}

        if jsonpCBKP is None or 'jsonpCBKP' not in jsonpCBKP:
            logging.error("shop_active_give_gift: get response error...")
            return

        give_gift_json = json.loads(jsonpCBKP[14: -13])
        logging.info("shop_active_give_gift:{}".format(str(give_gift_json)))
    except Exception:
        logging.exception(sys.exc_info())


def shop_draw_from_activity_link(session: Session, link):
    logging.info("shop_draw_from_activity_link : {}".format(link))
    path_part, query_part = splitquery(link)

    if path_part == "https://lzkj-isv.isvjcloud.com/wxShopGift/activity":
        try:
            api = "https://lzkj-isv.isvjcloud.com/wxShopGift/draw"
            headers = {
                'Host': 'lzkj-isv.isvjcloud.com',
                'Origin': 'https://lzkj-isv.isvjcloud.com',
                'Accept': 'application/json',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': link
            }
            session.headers.update(headers)

            activityId = parse_qs(query_part).get('activityId')[0]

            data = "activityId=" + activityId + "&buyerPin=" + session.cookies.get(
                'pin') + "&hasFollow=false&accessType="

            ret = session.post(api, data=data).text
            logging.info("shop_draw_from_activity_link: {}".format(str(ret)))

        except Exception:
            logging.exception(sys.exc_info())
    elif path_part == "https://lzkj-isv.isvjcloud.com/wxDrawActivity/activity":
        try:
            bs = BeautifulSoup(requests.get(link).text, 'html.parser')
            # activityId = bs.find(id='activityId').get('value')
            user_id = bs.find(id='userId').get('value')

            session.headers.update({
                'Host': 'lzkj-isv.isvjcloud.com',
                'Origin': 'https://lzkj-isv.isvjcloud.com',
                'Accept': 'application/json',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': link
            })

            api = "https://lzkj-isv.isvjcloud.com/wxDrawActivity/getMyPing"
            data = "userId=" + user_id + "&token=" + session.cookies.get('wq_auth_token') + "&fromType=WeChat"
            getMyPing = session.post(api, data=data).text
            # {"result":true,"data":"chenbenqing530905787","count":0,"errorMessage":""}
            # {"result":false,"data":"pin get error","count":0,"errorMessage":"获取账户转换信息出错，请重新进入一次"}
            logging.info("shop_draw_from_activity_link getMyPing: {}".format(getMyPing))

            api = "https://lzkj-isv.isvjcloud.com/wxDrawActivity/activityContent"

            activityId = parse_qs(query_part).get('activityId')[0]

            # activityId=77dcc42796bc414c86f952e588627dc0&pin=chenbenqing530905787
            data = "activityId=" + activityId + "&pin=" + session.cookies.get('pin')

            ret = session.post(api, data=data).text
            # {"result":true,"data":{"content":[{"id":225901,"name":"圣罗兰小金条","type":7,"position":1,"drawTime":null,"showImage":"https://img10.360buyimg.com/imgzone/jfs/t1/30990/20/5196/31315/5c8396b1E2fb462f1/8046cac67a332a13.png","realValue":null,"value":null,"addressId":null,"needWriteAddress":null,"priceInfo":"1800.00","itemId":null},{"id":225902,"name":"6元优惠券","type":10,"position":2,"drawTime":null,"showImage":"null","realValue":"6","value":null,"addressId":null,"needWriteAddress":null,"priceInfo":"0","itemId":null},{"id":225903,"name":"松鼠玩偶","type":7,"position":4,"drawTime":null,"showImage":"null","realValue":null,"value":null,"addressId":null,"needWriteAddress":null,"priceInfo":"99.00","itemId":null},{"id":225904,"name":"20元优惠券","type":10,"position":5,"drawTime":null,"showImage":"null","realValue":"20","value":null,"addressId":null,"needWriteAddress":null,"priceInfo":"0","itemId":null},{"id":225905,"name":"2京豆","type":6,"position":6,"drawTime":null,"showImage":"null","realValue":null,"value":null,"addressId":null,"needWriteAddress":null,"priceInfo":"0.02","itemId":null},{"id":225906,"name":"10店铺积分","type":9,"position":7,"drawTime":null,"showImage":"null","realValue":null,"value":null,"addressId":null,"needWriteAddress":null,"priceInfo":"0","itemId":null},{"id":225907,"name":"888元主人专享大礼包","type":7,"position":8,"drawTime":null,"showImage":"https://img10.360buyimg.com/imgzone/jfs/t1/10728/10/13656/42768/5c839a6eE58b8f4b7/126b2b43e7d057e3.png","realValue":null,"value":null,"addressId":null,"needWriteAddress":null,"priceInfo":"888.00","itemId":null},{"id":0,"name":"谢谢参与!","type":0,"position":0,"drawTime":null,"showImage":null,"realValue":null,"value":null,"addressId":null,"needWriteAddress":null,"priceInfo":null,"itemId":null}],"id":"77dcc42796bc414c86f952e588627dc0","rule":"1、抽奖时间：2019-03-10 00:00 至 2019-3-31 23:59；\r\n2、抽奖对象：全网客户；\r\n3、总体中奖概率：92%\r\n4、每人每天赠送1次抽奖机会，分享店铺增加一次抽奖机会，累计赠送不超过3次；\r\n5、实物奖品将会在活动结束20个工作日寄出，松鼠玩偶随机抽取10名发放，如无地址将会视为自动放弃奖品（实品奖品图片仅供参考，请以实物为准，主人专属大礼包，内涵产品为松鼠自行搭配，不接受制定）\r\n6、优惠券使用时间：领取后3天内有效；\r\n7、通过作弊手段抽中奖品一律取消中奖资格","canDrawTimes":1,"hasJoinMan":0,"userId":1000015268,"styleId":null,"member":null,"drawConsume":null},"count":0,"errorMessage":""}
            if ret is None or 'data' not in ret:
                logging.error("shop_draw_from_activity_link: get activityContent error...")
                return

            ret_json = json.loads(ret)
            canDrawTimes = ret_json['data']['canDrawTimes']

            while (ret_json['result'] and canDrawTimes > 0):
                logging.info(
                    "shop_draw_from_activity_link canDrawTimes = {} ".format(str(canDrawTimes)))
                start_api = "https://lzkj-isv.isvjcloud.com/wxDrawActivity/start"
                # {"result":true,"data":{"id":225902,"drawOk":true,"url":"3.cn/kT2I1j6","canDrawTimes":0,"drawInfoType":10,"denominations":"6","name":"6元优惠券","value":"4296","drawInfo":{"id":225902,"venderId":1000015268,"name":"6元优惠券","value":"4296","type":10,"beanNum":null,"priceInfo":"0","showImage":"null","productUrl":null,"memo":"备注","deleted":false,"createTime":1552128293000,"updateTime":1552128662000,"drawChance":null,"totalPrizeNum":null,"itemId":null},"recordId":0,"addressId":null,"position":2,"needWriteAddress":null,"itemId":null,"errorMessage":null},"count":0,"errorMessage":""}
                logging.info("shop_draw_from_activity_link: " + session.post(start_api, data=data).text)
                canDrawTimes = canDrawTimes - 1

            logging.info("shop_draw_from_activity_link: draw completed...")

        except Exception:
            logging.exception(sys.exc_info())
    elif path_part == "https://gzsl-isv.isvjcloud.com/wuxian/mobileForApp/dist/views/pages/gameJGG_1.html":
        # 'https: //gzsl-isv.isvjcloud.com/wuxian/mobileForApp/dist/views/pages/gameJGG_1.html?activityId=7989'
        # https://gzsl-isv.isvjcloud.com/wuxian/user/contact/1492
        try:
            activityId = parse_qs(query_part).get('activityId')[0]
            getLottery_api = "https://gzsl-isv.isvjcloud.com/wuxian/user/getLottery/" + activityId
            draw_api = 'https://gzsl-isv.isvjcloud.com/wuxian/user/draw/' + activityId

            session.headers.update({
                'Host': 'gzsl-isv.isvjcloud.com',
                'Origin': 'https://gzsl-isv.isvjcloud.com',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Content-Type': 'application/json;charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': link
            })
            payload = {"activityId": activityId}

            lottery_json = json.loads(session.post(getLottery_api, json=payload).text)
            if lottery_json and lottery_json['leftTime'] > 0:
                draw = session.post(draw_api, json=payload).text
                logging.info("shop_draw_from_activity_link draw: {}".format(str(draw)))
            else:
                logging.info("shop_draw_from_activity_link: no leftTime to draw...")
        except Exception:
            logging.exception(sys.exc_info())
    elif path_part == 'https://fjzy-isv.isvjcloud.com/index.php':
        # https://fjzy-isv.isvjcloud.com/index.php?mod=games&c=the9house&venderId=743669&yxId=1833&token=4A8E526738DF4C9C07F6DF303656C5024A468486A4A01BC56D3231843CBC2013
        try:
            token = session.cookies.get('wq_auth_token')
            link = link + "&token=" + str(token)
            api = "https://fjzy-isv.isvjcloud.com/index.php?mod=games&action=buyerTokenJson"

            session.headers.update({
                'Host': 'fjzy-isv.isvjcloud.com',
                'Origin': 'https://fjzy-isv.isvjcloud.com',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': link
            })

            venderId = parse_qs(query_part).get('venderId')[0]
            yxId = parse_qs(query_part).get('yxId')[0]

            # venderId=743669&wxtoken=4A8E526738DF4C9C07F6DF303656C5024A468486A4A01BC56D3231843CBC2013&yxId=1833&actId=1
            data = "venderId=" + venderId + "&wxtoken=" + token + "&yxId=" + yxId + "&actId=1"
            buyerTokenJson = json.loads(session.post(api, data=data).text)
            if buyerTokenJson['drawNum'] > 0:
                buyPin = buyerTokenJson['buyPin']
                logging.info("shop_draw_from_activity_link left drawNum:".format(str(buyerTokenJson['drawNum'])))
                # https://fjzy-isv.isvjcloud.com/index.php?mod=games&action=check&venderId=743669&actId=1&yxId=1833&token=45b7a585-df50-416c-b0be-e9fa5ac2bb4a_1543986226118-jd&buyPin=1553236206
                checkApi = "https://fjzy-isv.isvjcloud.com/index.php?mod=games&action=check&venderId=" + venderId \
                           + "&actId=1&yxId=" + yxId + "&token=45b7a585-df50-416c-b0be-e9fa5ac2bb4a_1543986226118-jd&buyPin=" + buyPin
                data = "code=" + yxId

                check = session.post(checkApi, data=data).text
                logging.info("shop_draw_from_activity_link: {}".format(str(check)))
            else:
                logging.info("{} shop_draw_from_activity_link no drawNum...")
        except Exception:
            logging.exception(sys.exc_info())


def shop_draw_from_official(session: Session, vender_id):
    """店铺抽奖-official"""
    try:
        api = "https://wq.jd.com/mjgj/column/ShopSignDraw?channel=2&g_login_type=0&callback=jsonpCBKF&g_ty=ls&venderId=" \
              + vender_id + "&_=" + str(int(time.time() * 1000))
        headers = {
            'Host': 'wq.jd.com',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': 'https://wqshop.jd.com/mshop/shopdraw?' + vender_id
        }
        session.headers.update(headers)
        # jsonpCBKF({
        # 	"errcode": 0,
        # 	"msg": "success",
        # 	"data": {
        # 		"pinStatus": "1",
        # 		"pinEnterType": "0",
        # 		"type": "0",
        # 		"code": "1",
        # 		"prizeData": {
        #
        # 		}
        # 	}
        # });
        jsonpCBKF = session.get(api).text
        if jsonpCBKF is None or 'jsonpCBKF' not in jsonpCBKF:
            logging.error("shop_draw_from_official: get response error...")
            return

        draw_json = json.loads(jsonpCBKF[10: -2])
        logging.info("shop_draw_from_official: {}".format(str(draw_json)))
    except Exception:
        logging.exception(sys.exc_info())


def shop_sign_up(session: Session, link):
    logging.info("shop_sign_up : {}".format(link))
    path_part, query_part = splitquery(link)

    if path_part == "https://lzkj-isv.isvjcloud.com/sign/signActivity":
        # 例：https://lzkj-isv.isvjcloud.com/sign/signActivity?activityId=ee6bbff8a06f4a8dbaa67cd9843bc14f&venderId=681974
        try:
            api = "https://lzkj-isv.isvjcloud.com/sign/wx/signUp"

            session.headers.update({
                'Host': 'lzkj-isv.isvjcloud.com',
                'Origin': 'https://lzkj-isv.isvjcloud.com',
                'Accept': 'application/json',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': link
            })

            activity_id = parse_qs(query_part).get('activityId')[0]
            data = "actId=" + activity_id + "&pin=" + session.cookies.get('pin')

            ret_json = json.loads(session.post(api, data=data).text)
            logging.info("shop_sign_up: {}".format(str(ret_json)))
        except Exception:
            logging.exception(sys.exc_info())
    elif path_part == "https://gzsl-isv.isvjcloud.com/wuxian/mobileForApp/dist/views/pages/myIntegral.html":
        # 例：https: //gzsl-isv.isvjcloud.com/wuxian/mobileForApp/dist/views/pages/myIntegral.html?v=1000133822
        try:
            api = "https://gzsl-isv.isvjcloud.com/wuxian/user/sign/457"
            session.headers.update({
                'Host': 'gzsl-isv.isvjcloud.com',
                'Origin': 'https://gzsl-isv.isvjcloud.com',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Content-Type': 'application/json;charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': link
            })
            data = {"activityId": 457}
            ret = session.post(api, data=data).text
            logging.info("shop_sign_up: {}".format(str(ret)))
        except Exception as e:
            logging.exception(sys.exc_info())
    else:
        logging.error("shop_sign_up: not supported...")


def query_shop_sign_draw(session: Session, vender_id):
    """查询店铺活动-抽奖或签到"""
    try:
        api = "http://wq.jd.com/mjgj/column/QueryShopSignDraw?channel=2&sceneval=2&g_login_type=1&callback=jsonpCBKB&g_ty=ls&venderId=" \
              + vender_id + "&_=" + str(int(time.time() * 1000))
        headers = {
            'Host': 'wq.jd.com',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': 'https://wqshop.jd.com/mshop/gethomepage?venderid=' + vender_id
        }
        session.headers.update(headers)

        jsonpCBKB = session.get(api).text
        # jsonpCBKB({
        # 	"errcode": 0,
        # 	"msg": "succ",
        # 	"data": {
        # 		"pinStatus": "1",
        # 		"pinEnterType": "0",
        # 		"type": "1",   0 为抽奖，1 为签到
        # 		"code": "0",   0 为可抽奖，2 为已抽奖
        # 		"source": "3",
        # 		"isvurl": "https://lzkj-isv.isvjcloud.com/sign/signActivity?activityId=ee6bbff8a06f4a8dbaa67cd9843bc14f&venderId=681974",  抽奖链接
        # 		"share": "0",
        # 		"beginTime": "1552546456000",
        # 		"endTime": "1554047940000",
        # 		"day1": "0",
        # 		"day2": "0",
        # 		"history": [],
        # 		"prizeRule": [],
        # 		"skuList": [],
        # 		"signInfo": []
        # 	}
        # });
        if jsonpCBKB is None or 'jsonpCBKB' not in jsonpCBKB:
            logging.error("query_shop_sign_draw: get response error...")
            return

        gift_json = json.loads(jsonpCBKB[10:-2])
        logging.info("query_shop_sign_draw: {}".format(str(gift_json)))

        if gift_json["errcode"] != 0:  # errcode : 0 表示成功
            logging.error("query_shop_sign_draw: {}".format(str(gift_json['msg'])))
            return

        data = gift_json["data"]
        if data["code"] is "0":  # '0' 表示可进行，'2' 表示已经
            if data["type"] is "0":  # ‘0’ 抽奖，‘1’签到
                if (data['isvurl']) and (data['isvurl'] != ''):
                    shop_draw_from_activity_link(session, data['isvurl'])
                else:
                    shop_draw_from_official(session, vender_id)
            elif data["type"] is "1":
                shop_sign_up(session, data['isvurl'])

    except Exception:
        logging.exception(sys.exc_info())


def shop_add_fav(session: Session, shop_id):
    """店铺收藏"""
    try:
        # https://wq.jd.com/fav/shop/AddShopFav?shopId=1000078708&_=1553069382415&sceneval=2&g_login_type=1&callback=jsonpCBKG&g_ty=ls
        api = "https://wq.jd.com/fav/shop/AddShopFav?shopId=" + shop_id + "&_=" + str(
            int(time.time() * 1000)) + "&g_login_type=0&callback=jsonpCBKG&g_ty=ls"

        headers = {
            'Host': 'wq.jd.com',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': "https://shop.m.jd.com/?shopId=" + shop_id
        }

        session.headers.update(headers)

        fav = session.get(api).text
        logging.info("shop_add_fav: {}".format(fav))
    except Exception:
        logging.exception(sys.exc_info())


def shop_del_fav(session: Session, vender_id, shop_id):
    """取消店铺收藏"""
    try:
        api = "https://wq.jd.com/fav/shop/DelShopFav?g_login_type=0&callback=jsonpCBKK&g_ty=ls&shopId=" \
              + shop_id + "&venderId=" + vender_id + "&_=" + str(int(time.time() * 1000))
        headers = {
            'Host': 'wq.jd.com',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': 'https://wqshop.jd.com/mshop/gethomepage?venderid=' + vender_id
        }
        session.headers.update(headers)

        jsonpCBKK = session.get(api).text
        # try{jsonpCBKK({"iRet":"0","errMsg":"success"});}catch(e){}
        if jsonpCBKK is None or 'jsonpCBKK' not in jsonpCBKK:
            logging.error("shop_del_fav: get response error...")
            return

        logging.info("{} shop_del_fav:{}".format(str(jsonpCBKK)))
    except Exception:
        logging.exception(sys.exc_info())


def query_shop_fav_list(session: Session):
    """查询店铺收藏列表"""
    try:
        api = "https://wq.jd.com/fav/shop/QueryShopFavList?cp=1&pageSize=10" \
              "&lastlogintime=1552463214&_=" + str(int(time.time() * 1000)) \
              + "&g_login_type=0&callback=jsonpCBKA&g_tk=626832008&g_ty=ls"

        session.headers.update({
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': "https://wqs.jd.com/my/fav/shop_fav.shtml"
        })

        jsonpCBKA = session.get(api).text
        if (jsonpCBKA is None) or ("jsonpCBKA" not in jsonpCBKA):
            logging.error("query_shop_fav_list: get response error...")
            return

        fav_json = json.loads(jsonpCBKA[14:-13])
        logging.info("query_shop_fav_list " + str(fav_json))

        shop_id_list = []
        if fav_json["iRet"] is "0":
            for item in fav_json["data"]:
                shop_id_list.append(item["shopId"])

        elif fav_json["iRet"] is '9999':
            logging.error("query_shop_fav_list: not login...")
            # JD_Auto_Login().auto_login()
            # time.sleep(2)
            # update_session_cookies(self.session, data_path / "cookies.json")

        logging.info("query_shop_fav_list shop list:" + str(shop_id_list))
        return shop_id_list

    except Exception:
        logging.exception(sys.exc_info())
        return None


def batch_unfollow_fav(session: Session, shop_list):
    if shop_list is None or len(shop_list) <= 0:
        logging.error("batch_unfollow_fav: shop_list empty, return...")
        return

    try:
        api = "https://wq.jd.com/fav/shop/batchunfollow?" \
              "shopId=" + str(",".join(str(i) for i in shop_list)) + "&_=" + str(int(time.time() * 1000)) \
              + "&g_login_type=0&callback=jsonpCBKR&g_tk=626832008&g_ty=ls"

        session.headers.update({
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': "https://wqs.jd.com/my/fav/shop_fav.shtml"
        })

        jsonpCBKR = session.get(api).text
        if (jsonpCBKR is None) or ("jsonpCBKR" not in jsonpCBKR):
            logging.error("query_shop_fav_list: get response error...")
            return

        unfollow_json = json.loads(jsonpCBKR[14:-13])
        logging.info(
            "batch_unfollow_fav success ? " + str(unfollow_json['iRet'] == '0') + ", " + str(unfollow_json))

    except Exception:
        logging.exception(sys.exc_info())


def batch_query_shop_fav_gift(session: Session, vender_list):
    if session is None or vender_list is None or len(vender_list) == 0:
        logging.error("batch_query_shop_fav_gift: params error...")
        return

    try:
        api = "https://wq.jd.com/mjgj/column/BatchQueryShopFavGift?venderIds=" + str(
            ",".join(str(i) for i in vender_list)) \
              + "&channel=7&_=" + str(int(time.time() * 1000)) + "&g_login_type=0&callback=jsonpCBKE&g_ty=ls"
        headers = {
            'Host': 'wq.jd.com',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://wqs.jd.com/my/fav/shop_fav.shtml'
        }
        session.headers.update(headers)

        jsonpCBKE = session.get(api).text
        if jsonpCBKE is None or 'jsonpCBKE' not in jsonpCBKE:
            logging.error("batch_query_shop_fav_gift: get response error...")
            return

        fav_json = json.loads(jsonpCBKE[10:-2])
        logging.info("batch_query_shop_fav_gift:" + str(fav_json))

        if fav_json['errcode'] == 0:
            data = fav_json['data']
            for gift in data:
                vender_id = gift['venderId']
                gift_info = gift['giftInfo']
                for item in gift_info:
                    if item['prizeType'] is '4':  # '4' 表示 京豆
                        activity_id = item['activityId']
                        discount = item['discount']
                        logging.info(
                            "batch_query_shop_fav_gift: get {} beans from vender_id {}".format(discount, vender_id))
                        shop_gift_from_official(session, vender_id, activity_id)
        else:
            logging.error("batch_query_shop_fav_gift error:" + str(fav_json))
    except Exception:
        logging.exception(sys.exc_info())


def batch_get_shop_info_by_vender_id(session: Session, vender_list):
    if session is None or vender_list is None or len(vender_list) == 0:
        logging.error("batch_get_shop_info_by_vender_id: params error...")
        return

    try:
        api = "https://wq.jd.com/mshop/BatchGetShopInfoByVenderId?venderIds=" + str(
            ",".join(str(i) for i in vender_list)) \
              + "&_=" + str(int(time.time() * 1000)) + "&g_login_type=0&callback=jsonpCBKE&g_ty=ls"
        headers = {
            'Host': 'wq.jd.com',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://wqs.jd.com/my/fav/shop_fav.shtml'
        }
        session.headers.update(headers)

        jsonpCBKE = session.get(api).text
        if jsonpCBKE is None or 'jsonpCBKE' not in jsonpCBKE:
            logging.error("batch_get_shop_info_by_vender_id: get response error...")
            return

        json_obj = json.loads(jsonpCBKE[14:-13])
        shop_info_list = []
        if json_obj['errcode'] == 0:
            data = json_obj['data']
            for shop in data:
                item = {'shopId': shop['shopId'],
                        'venderId': shop['shopInfo']['venderId'],
                        'shopName': shop['shopInfo']['shopName'],
                        'shopUrl': "https://wqshop.jd.com/mshop/gethomepage?venderid=" + shop['shopInfo']['venderId']}
                shop_info_list.append(item)
        else:
            logging.error("batch_query_shop_fav_gift error:" + str(json_obj))

        return shop_info_list
    except Exception:
        logging.exception(sys.exc_info())
        return None


if __name__ == '__main__':
    log_format = '%(asctime)s %(name)s[%(module)s] %(levelname)s: %(message)s'
    # logging.basicConfig(filename=log_path, format=log_format, level=logging.INFO)
    logging.basicConfig(format=log_format, level=logging.INFO)
