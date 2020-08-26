# -*- coding:utf-8 -*-

"""
@author:ML
@file:houses.py
@time:2020/08/26
"""
import json
from flask import g, current_app, jsonify, request

from . import api
from ihome.utils.commons import login_require
from ihome.utils.response_code import BaseResponse, RET
from ihome.utils.image_storage import storage
from ihome.models import Area
from ihome import db, constants
from ihome import redis_store


@api.route("/areas", methods=["GET"])
def get_area_info():
    """获取城区信息"""
    # 尝试从redis中读取数据

    try:
        resp_json = redis_store.get("area_info")
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json is not None:
            # redis有缓存数据
            current_app.logger.error("hit redis area_info")
            return resp_json, 200, {"Content-Type": "application/json"}

    # 查询数据库，读取城区信息
    resp = BaseResponse()
    try:
        area_li = Area.query.all()
    except Exception as e:
        resp.errno = RET.DBERR
        resp.errmsg = "获取城区信息错误"
        current_app.logger.error(e)
        return jsonify(resp.dict)

    area_dict_li = []
    for area in area_li:
        area_dict_li.append(area.to_dict())

    resp.errno = RET.OK
    resp.errmsg = "OK"
    resp.data = area_dict_li

    # 将数据转换为json字符串
    resp_json = json.dumps(resp.dict)
    # 将area_dict_li保存到redis中
    try:
        redis_store.setex("area_info", constants.AREA_INFO_REDIS_CACHE_EXPIRES, resp_json)
    except Exception as e:
        current_app.logger.error(e)

    return resp_json, 200, {"Content-Type": "application/json"}
