# -*- coding:utf-8 -*-

"""
@author:ML
@file:commons.py
@time:2020/08/19
"""

from werkzeug.routing import BaseConverter
from flask import session, jsonify, g
from ihome.utils.response_code import BaseResponse, RET
import functools


# 定义正则转换器

class ReConverter(BaseConverter):
    def __init__(self, url_map, *args):
        super(ReConverter, self).__init__(url_map)
        self.regex = args[0]

    def to_python(self, value):  # 可以重写父类方法，对提取到参数进一步处理，value是在路径进行正则表达式匹配的时候提取的参数
        pass
        return value  # 返回值传回给视图函数中的id

    def to_url(self, value):  # 使用url_for的时候调用
        pass
        return value


def login_require(view_func):
    """验证登录状态的装饰器"""

    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        # 判断用户的登录状态
        user_id = session.get("user_id")

        # 如果用户是登录的，直接进入到视图函数
        if user_id:
            # 将user_id保存到g对象中，在视图函数中可以通过g对象获取保存数据
            g.user_id = user_id
            return view_func(*args, **kwargs)
        # 如果未登录，返回未登录的信息
        else:
            resp = BaseResponse()
            resp.errno = RET.SESSIONERR
            resp.errmsg = "用户未登录"

            return jsonify(resp.dict)

    return wrapper
