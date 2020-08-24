# -*- coding:utf-8 -*-

"""
@author:ML
@file:sms.py
@time:2020/08/20
"""
from ronglian_sms_sdk import SmsSDK
import json

accId = '8***6'
accToken = 'd***8'
appId = '8***d'


class SMS(object):
    instance = None

    def __new__(cls, *args, **kwargs):

        # 单例模式
        # 1. 判断类属性是否已经被赋值
        if cls.instance is None:
            obj = super(SMS, cls).__new__(cls)
            obj.sdk = SmsSDK(accId, accToken, appId)
            cls.instance = obj

        # 2. 返回类属性的单例引用
        return cls.instance

    def send_message(self, tid, mobile, data):
        """
        :param tid: '容联云通讯创建的模板ID'
        :param mobile: '手机号1,手机号2'
        :param data: ('变量1', '变量2')
        :return:
        """

        resp = self.sdk.sendMessage(tid, mobile, data)
        resp = json.loads(resp)
        status_code = resp.get("statusCode")
        if status_code == "000000":
            # 发送成功
            return 0
        else:
            return -1


if __name__ == '__main__':
    sms = SMS()
    ret = sms.send_message(mobile="186******8", data=("1234", "5"), tid=1)

    print(ret)
