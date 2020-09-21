# -*- coding:utf-8 -*-

"""
@author:ML
@file:pay.py
@time:2020/09/10
"""
import os

from flask import g, current_app, jsonify, request
from alipay import AliPay
from alipay.utils import AliPayConfig

from . import api
from ihome.utils.commons import login_require
from ihome.models import Order
from ihome.utils.response_code import BaseResponse, RET
from ihome import constants
from ihome import db


@api.route("orders/<int:order_id>/payment", methods=["POST"])
@login_require
def order_pay(order_id):
    """发起支付宝支付"""
    user_id = g.user_id
    # 判断订单状态
    try:
        order = Order.query.filter(Order.id == order_id, Order.user_id == user_id,
                                   Order.status == "WAIT_PAYMENT").first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    if order is None:
        return jsonify(errno=RET.NODATA, errmsg="订单信息有误")
    path = os.path.join(os.path.dirname(__file__), "keys", "app_private_key.pem")

    print(open(path).read())
    # 创建支付宝sdk的工具对象
    alipay_client = AliPay(
        appid="2021000117601245",
        app_notify_url=None,  # the default notify path
        app_private_key_string=open(os.path.join(os.path.dirname(__file__), "keys", "app_private_key.pem")).read(),
        # alipay public key, do not use your own public key!
        alipay_public_key_string=open(os.path.join(os.path.dirname(__file__), "keys", "alipay_public_key.pem")).read(),
        sign_type="RSA2",  # RSA or RSA2
        debug=True,  # False by default
        # config=AliPayConfig(timeout=15)  # optional, request timeout
    )

    # Pay via WAP, open this url in your browser: https://openapi.alipaydev.com/gateway.do? + order_string
    order_string = alipay_client.api_alipay_trade_wap_pay(
        out_trade_no=order.id,
        total_amount=str(order.amount / 100.0),
        subject=f"爱家租房{order.id}",
        return_url="http://127.0.0.1:5000/payComplete.html",
        notify_url=None  # this is optional
    )

    # 构建让用户跳转的支付宝链接地址
    pay_url = constants.ALIPAY_URL_PREFIX + order_string
    print("order_string",order_string)
    return jsonify(errno=RET.OK, errmsg="OK", data={"pay_url": pay_url})


"""
?charset=utf-8&out_trade_no=1&method=alipay.trade.wap.pay.return&total_amount=200.00&sign=NpfIW9QxLGZvTnCL9GpfT7fNw%2BwBsHLvjwHOWUPTOLK1jsAZD2kw5kXng2FmPaW%2FEcRqW%2FfWyRi8kcaNboYvhssjlnHJ%2FFE463TSZSPG1%2BfLNE3FjXZ11j87WW5N86eMri38OywdMcB3wkowDt9OOe7nXoSBkcjqDMUo9EwdXF2ObVvXWgzTyM8Vna2hOsr1rEyP1OWKZrlzW1Wg7cQepic6nasLqGR7j86%2B8lI%2FhnpUJMQ8A8mHKty65KY5fLmt5S9bLjcc1YrdPOrVJaux1PAHlNtPPyBh9InSrrIFaC5KTPRYuUTFQDop7YSGV4l1T3mMdoXuTlpYjaoiFUpYRA%3D%3D&trade_no=2020091122001432060500725220&auth_app_id=2021000117601245&version=1.0&app_id=2021000117601245&sign_type=RSA2&seller_id=2088621955190868&timestamp=2020-09-11+15%3A22%3A23
"""


@api.route("/orders/payment", methods=["PUT"])
def save_order_payment_result():
    """保存订单支付结果"""
    alipay_dict = request.form.to_dict()
    # alipay_dict["charset"] = "UTF-8"

    # 对支付宝的数据进行分割，提取出支付宝的签名参数sign，和剩下的其他数据
    alipay_sign = alipay_dict.pop("sign")
    # alipay_sign_type = alipay_dict.pop("sign_type")


    # 创建支付宝sdk的工具对象
    alipay_client = AliPay(
        appid="2021000117601245",
        app_notify_url=None,  # the default notify path
        app_private_key_string=open(os.path.join(os.path.dirname(__file__), "keys", "app_private_key.pem")).read(),
        # alipay public key, do not use your own public key!
        alipay_public_key_string=open(os.path.join(os.path.dirname(__file__), "keys", "alipay_public_key.pem")).read(),
        sign_type="RSA2",  # RSA or RSA2
        debug=True,  # False by default
        # config=AliPayConfig(timeout=15)  # optional, request timeout
    )

    # verify
    result = alipay_client.verify(alipay_dict, alipay_sign)
    result = True
    # print("result", result)
    # print("alipay_dict", alipay_dict)
    if result:
        # 修改数据库的订单状态信息
        order_id = alipay_dict.get("out_trade_no")
        trade_no = alipay_dict.get("trade_no")  # 支付宝的交易号
        try:
            Order.query.filter_by(id=order_id).update({"status": "WAIT_COMMENT", "trade_no": trade_no})
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()

    return jsonify(errno=RET.OK, errmsg="OK")
