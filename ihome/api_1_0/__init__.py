# coding: utf-8 

"""
@author:ML
@file:__init__.py.py
@time:2020/08/18
"""

from flask import Blueprint

# 创建蓝图对象
api = Blueprint("api_1_0", __name__)

# 导入蓝图的视图
from . import demo, verify_code, passport
