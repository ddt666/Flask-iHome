# -*- coding:utf-8 -*-

"""
@author:ML
@file:commons.py
@time:2020/08/19
"""

from werkzeug.routing import BaseConverter


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
