# coding: utf-8 

"""
@author:ML
@file:demo.py
@time:2020/08/18
"""

from flask import current_app
from . import api
from ihome import db,models


@api.route("/index")
def index():
    current_app.logger.debug("debug msg")
    return "index page"
