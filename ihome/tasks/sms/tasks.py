# -*- coding:utf-8 -*-

"""
@author:ML
@file:tasks.py
@time:2020/08/28
"""
from ihome.tasks.main import celery_app

from ihome.utils.sms import SMS


@celery_app.task
def send_sms(tid, mobile, data):
    """发送短信的异步任务"""
    # sms = SMS()
    # sms.send_message(tid, mobile, data)
    pass