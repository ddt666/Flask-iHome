# -*- coding:utf-8 -*-

"""
@author:ML
@file:task_sms.py
@time:2020/08/28
"""

from celery import Celery

# from ihome.utils.sms import SMS

# 定义celery对象
celery_app = Celery("ihome", broker="redis://127.0.0.1:6379/1")


@celery_app.task
def send_sms(tid, mobile, data):
    """发送短信的异步任务"""
    # sms = SMS()
    # sms.send_message(tid, mobile, data)


if __name__ == '__main__':
    print(dir(send_sms))