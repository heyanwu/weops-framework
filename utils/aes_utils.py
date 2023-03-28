# -*- coding: utf-8 -*-

# @File    : aes_utils.py
# @Date    : 2022-06-13
# @Author  : windyzhao

import base64

from Crypto.Cipher import AES

"""
AES对称加密算法
"""


class AESEncryptUtil(object):
    SECRET_KEY = "25cx=4x+2^btvh8kxmzckv_-eobp%gn-"  # 加密密匙 请勿修改

    # 需要补位，str不是16的倍数那就补足为16的倍数
    @classmethod
    def add_to_16(cls, value):
        while len(value) % 16 != 0:
            value += "\0"
        return str.encode(value)  # 返回bytes

    # 加密方法
    @classmethod
    def encrypt(cls, text, key=SECRET_KEY):
        aes = AES.new(cls.add_to_16(key), AES.MODE_ECB)  # 初始化加密器
        encrypt_aes = aes.encrypt(cls.add_to_16(text))  # 先进行aes加密
        encrypted_text = str(base64.encodebytes(encrypt_aes), encoding="utf-8")  # 执行加密并转码返回bytes
        return encrypted_text

    # 解密方法
    @classmethod
    def decrypt(cls, text, key=SECRET_KEY):
        aes = AES.new(cls.add_to_16(key), AES.MODE_ECB)  # 初始化加密器
        base64_decrypted = base64.decodebytes(text.encode(encoding="utf-8"))  # 优先逆向解密base64成bytes
        decrypted_text = str(aes.decrypt(base64_decrypted), encoding="utf-8").replace("\0", "")  # 执行解密密并转码返回str
        return decrypted_text
