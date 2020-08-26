# -*- coding:utf-8 -*-

"""
@author:ML
@file:profile.py
@time:2020/08/24
"""
from flask import g, current_app, jsonify, request

from . import api
from ihome.utils.commons import login_require
from ihome.utils.response_code import BaseResponse, RET
from ihome.utils.image_storage import storage
from ihome.models import User
from ihome import db
from ihome import constants


@api.route("/users/avatar", methods=["POST"])
@login_require
def set_user_avatar():
    """
    设置用户头像
    参数： 用户上传的图片（多媒体表单格式），用户id
    """
    # 装饰器的代码中已经将user_id 保存到g对象中，所以视图中可以直接读取
    user_id = g.user_id

    # 获取图片
    image_file = request.files.get("avatar")

    resp = BaseResponse()

    if image_file is None:
        resp.errno = RET.PARAMERR
        resp.errmsg = "未上传图片"
        return jsonify(resp.dict)

    image_data = image_file.read()

    # 调用七牛云上传图片
    try:
        file_name = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        resp.errno = RET.THIRDERR
        resp.errmsg = "上传图片失败"
        return jsonify(resp.dict)

    # 保存文件名带数据库中
    try:
        User.query.filter_by(id=user_id).update({"avatar_url": file_name})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        resp.errno = RET.DATAERR
        resp.errmsg = "保存图片信息失败"
        return jsonify(resp.dict)

    avatar_url = constants.QINIU_URL_DOMAIN + file_name

    # 保存成功返回
    resp.errno = RET.OK
    resp.errmsg = "保存成功"
    resp.data = {"avatar_url": avatar_url}
    return jsonify(resp.dict)


@api.route("/users/name", methods=["PUT"])
@login_require
def change_user_name():
    """修改用户名"""

    user_id = g.user_id

    req_dict = request.get_json()

    name = req_dict.get("name")

    resp = BaseResponse()

    if name is None:
        resp.errno = RET.PARAMERR
        resp.errmsg = "未填写用户名"
        return jsonify(resp.dict)

    try:
        User.query.filter_by(id=user_id).update({"name": name})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        resp.errno = RET.DATAERR
        resp.errmsg = "保存用户名失败"
        return jsonify(resp.dict)

    resp.errno = RET.OK
    resp.errmsg = "保存成功"

    return jsonify(resp.dict)


@api.route("/user", methods=["GET"])
@login_require
def get_user_profile():
    """获取用户信息"""
    resp = BaseResponse()

    user_id = g.user_id

    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        resp.errno = RET.DBERR
        resp.errmsg = "获取用户信息失败"
        return jsonify(resp.dict)

    if user is None:
        resp.errno = RET.DBERR
        resp.errmsg = "无效操作"
        return jsonify(resp.dict)

    print(user)
    resp.errno = RET.OK
    resp.errmsg = "OK"
    resp.data = user.to_dict()

    return jsonify(resp.dict)


@api.route("/users/auth", methods=["POST"])
@login_require
def set_user_auth():
    """保存用户实名认证"""
    resp = BaseResponse()

    user_id = g.user_id

    req_dict = request.get_json()

    real_name = req_dict.get("real_name")
    id_card = req_dict.get("id_card")

    if not all([real_name, id_card]):
        resp.errno = RET.PARAMERR
        resp.errmsg = "参数错误"
        return jsonify(resp.dict)

    try:
        User.query.filter_by(id=user_id, real_name=None, id_card=None) \
            .update({"real_name": real_name, "id_card": id_card})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)

        resp.errno = RET.DBERR
        resp.errmsg = "保存用户实名信息失败"
        return jsonify(resp.dict)

    resp.errno = RET.OK
    resp.errmsg = "OK"
    return jsonify(resp.dict)

# @api.route("users/auth", methods=["GET"])
# @login_require
# def get_user_auth():
#     """获取用户实名信息"""
#     resp = BaseResponse()
#
#     user_id = g.user_id
#
#     try:
#         user = User.query.get(id=user_id)
#     except Exception as e:
#         resp.errno = RET.DBERR
#         resp.errmsg = "查询用户失败"
#         current_app.logger.error(e)
#         return jsonify(resp.dict)
#
#     if user is None:
#         resp.errno = RET.NODATA
#         resp.errmsg = "无效操作"
#         return jsonify(resp.dict)
#
#     print(user)
#     resp.errno = RET.OK
#     resp.errmsg = "OK"
#     resp.data = user.to_dict()
#
#     return jsonify(resp.dict)
