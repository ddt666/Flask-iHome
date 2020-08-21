# coding: utf-8 
"""
@author:ML
@file:config.py
@time:2020/08/18
"""

import redis


class Config(object):
    """配置信息"""

    SECRET_KEY = "M38SFG78GS9S0D0"

    # 数据库
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@127.0.0.1:3306/ihome"

    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # redis
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = "6379"

    # flask-session配置
    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 对cookie中session_id进行隐藏处理
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = 3600 * 24  # session数据的有效期，单位秒


class DevelopmentConfig(Config):
    """开发模式的配置信息"""
    DEBUG = True


class ProductionCofig(Config):
    """生产环境配置"""
    pass


config_map = {
    "develop": DevelopmentConfig,
    "product": ProductionCofig
}
