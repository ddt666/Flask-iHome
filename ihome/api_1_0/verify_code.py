# -*- coding:utf-8 -*-

"""
@author:ML
@file:verify_code.py
@time:2020/08/19
"""
import random

from flask import current_app, jsonify, make_response, request

from . import api
from ihome import redis_store, constants, db
from ihome.utils.captcha.captcha import captcha
from ihome.utils.response_code import RET
from ihome.models import User
from ihome.utils.sms import SMS


@api.route("/image_codes/<image_code_id>")
def get_image_code(image_code_id):
    """
    获取图片验证码
    :params image_code_id: 图片验证码
    :return: 验证码图片
    """

    # 业务逻辑处理
    # 生成验证码图片

    name, text, image_data = captcha.generate_captcha()

    try:
        # 将验证码真实值与编号保存到redis中，设置有效期
        redis_store.setex(f"image_code_{image_code_id}", constants.IMAGE_CODE_REDIS_EXPIRES, text)
        print("image_code_id", image_code_id)
        print("text", text)
    except Exception as e:
        # 记录日志
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存图片验证码失败")

    # 返回图片
    resp = make_response(image_data)
    resp.headers["Content-Type"] = "image/jpg"
    return resp


# GET /api/v1.0/sms_codes/13456987893?image_code=xxx&image_code_id=xxx
@api.route("/sms_codes/<re(r'1[34578]\d{9}'):mobile>")
def get_sms_code(mobile):
    """获取短信验证码"""
    # 获取参数
    image_code = request.args.get("image_code")
    image_code_id = request.args.get("image_code_id")

    # 校验参数
    if not all([image_code, image_code_id]):
        # 参数不完整
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 业务逻辑处理
    # 从redis中取出真实的图片验证码
    try:
        real_image_code = redis_store.get(f"image_code_{image_code_id}")
        print(image_code_id, real_image_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="redis数据库异常")

    # 判断图片验证码是否过期
    if real_image_code is None:
        # 表示图片验证码没有或者过期
        return jsonify(errno=RET.NODATA, errmsg="图片验证码失效")

    # 删除redis中的图片验证码，防止用户使用同一个图片验证码验证多次
    try:
        redis_store.delete(f"image_code_{image_code_id}")
    except Exception as e:
        current_app.logger.error(e)

    # 与用户填写的值进行对比
    if real_image_code.lower() != image_code.lower():
        # 填写错误
        return jsonify(errno=RET.DATAERR, errmsg="图片验证码错误")

    # 判断对于这个手机号的操作，在60秒内有没有之前的记录，如果有，则认为用户操作频繁，不接受处理
    try:
        send_flag = redis_store.get(f"send_sms_code_{mobile}")
    except Exception as e:
        current_app.logger.error(e)
    else:
        if send_flag is not None:
            return jsonify(errno=RET.REQERR, errmsg="请求过去频繁，请在60秒之后重试")

    # 判断手机号是否存在
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
    else:
        if user is not None:
            # 表示手机号存在
            return jsonify(errno=RET.DATAEXIST, errmsg="手机号已存在")

    # 如果不存在，则生成短信验证码
    sms_code = "%06d" % random.randint(0, 999999)

    # 保存真实的短信验证码
    try:
        redis_store.setex(f"sms_code_{mobile}", constants.SMS_CODE_REDIS_EXPIRES, sms_code)

        # 保存发送给这个手机号的记录，防止用户在60s内再次出发发送短信的操作
        redis_store.setex(f"send_sms_code_{mobile}", constants.SEND_SMS_CODE_INTERVAL, 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存短信验证码异常")

    # 发送短信
    try:
        ret = 0
        # sms = SMS()
        # ret = sms.send_message(1, mobile, (sms_code, int(constants.SMS_CODE_REDIS_EXPIRES / 60)))

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="发送异常")
    else:
        if ret == 0:

            # 发送成功
            return jsonify(errno=RET.OK, errmsg="发送成功")
        else:
            return jsonify(errno=RET.THIRDERR, errmsg="发送失败")


