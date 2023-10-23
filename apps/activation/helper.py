# -- coding: utf-8 --

# @File : helper.py
# @Time : 2022/9/19 11:38
# @Author : windyzhao

import base64
import random
import string

from Crypto.Cipher import AES

"""
采用AES对称加密算法
"""


# str不是32的倍数那就补足为16的倍数
def add_to_32(value):
    while len(value) % 32 != 0:
        value += "\0"
    return str.encode(value)  # 返回bytes


# 加密方法
def aes_encrypt(text):
    # 秘钥
    key = "can_way_msp_cloud_2020"
    # 待加密文本
    # 初始化加密器
    aes = AES.new(add_to_32(key), AES.MODE_ECB)
    # 先进行aes加密
    encrypt_aes = aes.encrypt(add_to_32(text))
    # 用base64转成字符串形式
    encrypted_text = str(base64.encodebytes(encrypt_aes), encoding="utf-8")  # 执行加密并转码返回bytes
    return encrypted_text


# 解密方法
def aes_decrypt(text):
    # 秘钥
    key = "can_way_msp_cloud_2020"
    # 密文
    # 初始化加密器
    try:
        aes = AES.new(add_to_32(key), AES.MODE_ECB)
        # 优先逆向解密base64成bytes
        base64_decrypted = base64.decodebytes(text.encode(encoding="utf-8"))
        # 执行解密密并转码返回str
        decrypted_text = str(aes.decrypt(base64_decrypted), encoding="utf-8").replace("\0", "")
        return True, decrypted_text
    except Exception:
        return False, ""


# 生成注册码
def create_registration_code():
    str_list = ["".join(random.sample(string.ascii_uppercase + string.digits, 5)) for i in range(5)]
    registration_code = "-".join(str_list)
    return registration_code
