# -*- coding:utf-8 -*-

"""
@author:ML
@file:main.py
@time:2020/08/28
"""
from celery import Celery
from ihome.tasks import config

# 定义celery对象
celery_app = Celery("ihome")

# 引入配置信息
celery_app.config_from_object(config)

# 自动搜索任务
celery_app.autodiscover_tasks(['ihome.tasks.sms'])
