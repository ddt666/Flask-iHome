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
from ihome.models import Area, House, Facility, HouseImage
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


@api.route("/houses/info", methods=["POST"])
@login_require
def save_house_info():
    """
    保存房屋的基本信息
    前端发送过来的json数据
    {
        "title":"",
        "price":"",
        "area_id":"1",
        "address":"",
        "room_count":"",
        "acreage":"",
        "unit":"",
        "beds":"",
        "capacity":"",
        "deposit":"",
        "min_days":"",
        "max_days":"",
        "facility":["7","8"]
    }
    """
    resp = BaseResponse()

    # 获取数据
    user_id = g.user_id
    house_data = request.get_json()

    title = house_data.get("title")  # 房屋名称标题
    price = house_data.get("price")  # 房屋单价
    area_id = house_data.get("area_id")  # 房屋所属城区的编号
    address = house_data.get("address")  # 房屋地址
    room_count = house_data.get("room_count")  # 房屋包含的房间数目
    acreage = house_data.get("acreage")  # 房屋面积
    unit = house_data.get("unit")  # 房屋布局（几室几厅)
    capacity = house_data.get("capacity")  # 房屋容纳人数
    beds = house_data.get("beds")  # 房屋卧床数目
    deposit = house_data.get("deposit")  # 押金
    min_days = house_data.get("min_days")  # 最小入住天数
    max_days = house_data.get("max_days")  # 最大入住天数

    # 检验参数
    if not all(
            [title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
        resp.errno = RET.PARAMERR
        resp.errmsg = "参数不完整"
        return jsonify(resp.dict)

    try:
        price = int(float(price) * 100)
        deposit = int(float(deposit) * 100)
    except Exception as e:
        current_app.logger.error(e)
        resp.errno = RET.PARAMERR
        resp.errmsg = "参数错误"
        return jsonify(resp.dict)

    # 判断城区id是否存在
    try:
        area = Area.query.get(area_id)
    except Exception as e:
        current_app.logger.error(e)
        resp.errno = RET.DBERR
        resp.errmsg = "数据库异常"
        return jsonify(resp.dict)
    if area is None:
        resp.errno = RET.NODATA
        resp.errmsg = "城区信息有误"
        return jsonify(resp.dict)

    # 保存房屋信息
    house = House(
        user_id=user_id,
        area_id=area_id,
        title=title,
        price=price,
        address=address,
        room_count=room_count,
        acreage=acreage,
        unit=unit,
        capacity=capacity,
        beds=beds,
        deposit=deposit,
        min_days=min_days,
        max_days=max_days
    )

    # db.session.add(house)

    # 房屋信息与设施属于同一个事务，在添加设施后再统一进行提交
    # try:
    #     db.session.add(house)
    #     db.session.commit()
    # except Exception as e:
    #     current_app.logger.error(e)
    #     db.session.rollback()
    #     resp.errno = RET.DBERR
    #     resp.errmsg = "保存数据异常"
    #     return jsonify(resp.dict)

    # 处理房屋的设施信息
    facility_ids = house_data.get("facility")

    if facility_ids:
        try:
            facilities = Facility.query.filter(Facility.id.in_(facility_ids)).all()
        except Exception as e:
            current_app.logger.error(e)
            resp.errno = RET.DBERR
            resp.errmsg = "数据库异常"
            return jsonify(resp.dict)

        if facilities:
            # 有合法的设施数据
            # 保存设施数据
            house.facilities = facilities
    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        resp.errno = RET.DBERR
        resp.errmsg = "保存数据失败"
        return jsonify(resp.dict)

    resp.errno = RET.OK
    resp.errmsg = "OK"
    resp.data = {"house_id": house.id}

    return jsonify(resp.dict)


@api.route("/houses/image", methods=["POST"])
@login_require
def save_house_image():
    """
    保存房屋的图片
    参数 图片，房屋的id
    """
    resp = BaseResponse()
    image_file = request.files.get("house_image")
    house_id = request.form.get("house_id")

    if not all([image_file, house_id]):
        resp.errno = RET.PARAMERR
        resp.errmsg = "参数错误"
        return jsonify(resp.dict)

    # 判断house_id的正确性
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        resp.errno = RET.DBERR
        resp.errmsg = "数据库异常"
        return jsonify(resp.dict)

    if house is None:
        resp.errno = RET.NODATA
        resp.errmsg = "房屋不存在"
        return jsonify(resp.dict)
    image_data = image_file.read()

    # 保存图片到七牛中
    try:
        file_name = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        resp.errno = RET.THIRDERR
        resp.errmsg = "保存图片失败"
        return jsonify(resp.dict)

    # 保存图片信息到数据库中
    house_image = HouseImage(house_id=house_id, url=file_name)

    db.session.add(house_image)

    if not house.index_image_url:
        house.index_image_url = house_image
        db.session.add(house)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        resp.errno = RET.DBERR
        resp.errmsg = "保存图片数据异常"
        return jsonify(resp.dict)

    image_url = constants.QINIU_URL_DOMAIN + file_name

    resp.errno = RET.OK
    resp.errmsg = "OK"
    resp.data = {
        "image_url": image_url
    }

    return jsonify(resp.dict)
