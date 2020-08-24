# -*- coding:utf-8 -*-

"""
@author:ML
@file:image_storage.py
@time:2020/08/24
"""

from qiniu import Auth, put_data, etag
import qiniu.config

# 需要填写你的 Access Key 和 Secret Key
access_key = 'v5****a6'
secret_key = '8U*****03'


def storage(file_data):
    """
    上传文件到骑牛
    :param file_data: 要上传的文件数据
    :return:
    """
    # 构建鉴权对象
    q = Auth(access_key, secret_key)

    # 要上传的空间
    bucket_name = 'ml-ihome'

    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, None, 3600)

    ret, info = put_data(token, None, file_data)
    print(info)
    print(ret)


if __name__ == '__main__':
    with open("./1.jpg", "rb") as f:
        file_data = f.read()
        storage(file_data)
