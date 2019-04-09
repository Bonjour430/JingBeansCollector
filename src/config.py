#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import argparse
import json
import logging
import sys
import time
from pathlib import Path

data_path = Path(__file__).parent.parent.joinpath('data')
log_path = Path(__file__).parent.parent.joinpath('log')

log_file = log_path / ('{}.log'.format(time.strftime('%Y-%m-%d')))
log_format = '%(asctime)s %(name)s[%(module)s] %(levelname)s: %(message)s'
# logging.basicConfig(filename=log_file, format=log_format, level=logging.INFO)
logging.basicConfig(format=log_format, level=logging.INFO)


jd_first_page = 'https://jd.com/'
jd_home_page = 'https://home.jd.com/'
jd_login_page = 'https://passport.jd.com/new/login.aspx'

m_jd_first_page = 'https://m.jd.com'
m_jd_home_page = 'https://home.m.jd.com'
m_jd_login_page = 'https://plogin.m.jd.com/user/login.action'

ua_hwv9_wechat = "Mozilla/5.0 (Linux; Android 8.0; DUK-AL20 Build/HUAWEIDUK-AL20; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/6.2 TBS/044353 Mobile Safari/537.36 MicroMessenger/6.7.3.1360(0x26070333) NetType/WIFI Language/zh_CN Process/tools"
ua_hwry8_wechat = "Mozilla/5.0 (Linux; Android 7.0; FRD-AL10 Build/HUAWEIFRD-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/6.2 TBS/044304 Mobile Safari/537.36 MicroMessenger/6.7.2.1340(0x2607023A) NetType/WIFI Language/zh_CN"
ua_hw_mate9 = "Mozilla/5.0 (Linux; Android 8.0; MHA-AL00 Build/HUAWEIMHA-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/6.2 TBS/044304 Mobile Safari/537.36 MicroMessenger/6.7.3.1360(0x26070333) NetType/WIFI Language/zh_CN Process/tools"
ua_android_wechat = "Mozilla/5.0 (Linux; Android 5.0; SM-N9100 Build/LRX21V) > AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 > Chrome/37.0.0.0 Mobile Safari/537.36 > MicroMessenger/6.0.2.56_r958800.520 NetType/WIFI"
ua_android_qq = "Mozilla/5.0 (Linux; Android 5.0; SM-N9100 Build/LRX21V) > AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 > Chrome/37.0.0.0 Mobile Safari/537.36 V1_AND_SQ_5.3.1_196_YYB_D > QQ/5.3.1.2335 NetType/WIFI"
ua_ios_qq = "Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) > AppleWebKit/537.51.2 (KHTML, like Gecko) Mobile/11D257 > QQ/5.2.1.302 NetType/WIFI Mem/28"
ua_ios_wechat = "Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) > AppleWebKit/537.51.2 (KHTML, like Gecko) Mobile/11D257 > MicroMessenger/6.0.1 NetType/WIFI"
ua_win10_chrome = "(Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
ua_qqbrowser = "Mozilla/5.0 (Linux; U; Android 8.1.0; zh-cn; BLA-AL00 Build/HUAWEIBLA-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/8.9 Mobile Safari/537.36"
ua_baidu = "Mozilla/5.0 (Linux; Android 8.1.0; CLT-AL00 Build/HUAWEICLT-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/63.0.3239.83 Mobile Safari/537.36 T7/10.13 baiduboxapp/10.13.0.10 (Baidu; P1 8.1.0)"


class Config:
    def __init__(self):
        self.debug = False
        self.log_format = log_format
        self.jd = {
            'username': '',
            'password': ''
        }

        self.jobs_skip = []

    @classmethod
    def load(cls, d):
        the_config = Config()

        the_config.debug = d.get('debug', False)

        try:
            the_config.jd = {
                # 'username': b85decode(d['jd']['username']).decode(),
                # 'password': b85decode(d['jd']['password']).decode()
                'username': d['jd']['username'],
                'password': d['jd']['password']
            }
        except Exception as e:
            logging.error('load JD account error: ' + repr(e))

        if not (the_config.jd['username'] and the_config.jd['password']):
            # 有些页面操作还是有用的, 比如移动焦点到输入框... 滚动页面到登录表单位置等
            # 所以不禁止 browser 的 auto_login 动作了, 但两项都有才自动提交, 否则只进行自动填充动作
            the_config.jd['auto_submit'] = 0  # used in js
            logging.info('userName and PWD not config, can not auto_submit.')

        else:
            the_config.jd['auto_submit'] = 1
        return the_config


def load_config():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='config file name')
    args = parser.parse_args()

    config_name = args.config or 'config.json'
    logging.info('parse the config file: "{}".'.format(config_name))

    config_file = Path(__file__).parent.joinpath('../conf/', config_name)

    if not config_file.exists():
        config_name = 'config.default.json'
        logging.warning('config file not provided, load from the default: "{}".'.format(config_name))
        config_file = config_file.parent.joinpath(config_name)

    try:
        # 略坑, Path.resolve() 在 3.5 和 3.6 上表现不一致... 若文件不存在 3.5 直接抛异常, 而 3.6
        # 只有 Path.resolve(strict=True) 才抛, 但 strict 默认为 False.
        # 感觉 3.6 的更合理些...
        config_file = config_file.resolve()
        config_dict = json.loads(config_file.read_text())
    except Exception as e:
        sys.exit('# error as load config file failed: {}'.format(e))

    the_config = Config.load(config_dict)
    return the_config


config = load_config()

