# -*- coding: utf-8 -*-

# @File    : user_manages.py
# @Date    : 2022-02-09
# @Author  : windyzhao
import copy
import json

import requests
from django.conf import settings

from utils.app_log import logger

"""
用户管理第三方接口类
由于用户管理未开放esb接口，所以所有的接口路由需要进行拼接
参数也是固定只有内置的字段，若有新的字段，请在平台的用户管理的设置处设置此字段未非必填

"""


class UserManageApi(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        try:
            self.apps_host = settings.BK_PAAS_INNER_HOST
        except AttributeError:
            self.apps_host = "http://paas.weops.com"

        self.version = "o"
        # 用户操作 删除/禁用 用户等
        self.add_user_url = r"{}/{}/bk_user_manage/api/v1/web/profiles/".format(self.apps_host, self.version)
        self.delete_user_url = r"{}/{}/bk_user_manage/api/v1/web/profiles/batch/".format(self.apps_host, self.version)

        # 创建用户目录
        self.categories_url = r"{}/{}/bk_user_manage/api/v2/categories/".format(self.apps_host, self.version)
        # 创建用户目录下的根组织
        self.departments_url = r"{}/{}/bk_user_manage/api/v2/departments/".format(self.apps_host, self.version)

        self.header = {"Cookie": "", "AUTH-APP": "WEOPS", "Content-Type": "application/json"}
        self.update_user_template = {"display_name": "", "email": "", "telephone": ""}
        self.add_user_template = {
            "category_id": 1,
            "password_valid_days": -1,  # 密码有效期
            "username": "",  # 用户名称
            "display_name": "",  # 全名
            "email": "",  # 邮箱
            "telephone": "",  # 电话
            "iso_code": "cn",
            "status": "NORMAL",  # 账户状态
            "staff_status": "IN",
            "departments": [1],  # 所在组织
            "leader": [],  # 上级 [{display_name: "赵金盟", id: 2, username: "windyzhao"}]
            "position": 0,
            "qq": "",
            "wx_userid": "",
            "account_expiration_date": "",
        }

    def set_header(self, cookies):
        """
        初始化cookie为制定格式
        cookies：request.COOKIES
        """

        if isinstance(cookies, dict):
            cookie = ";".join("{n}={v}".format(n=n, v=v) for n, v in cookies.items())
        else:
            cookie = cookies
        self.header["Cookie"] = cookie

    def request_method(self, url, data, method):
        """
        request请求 根据请求方式获取对应的方法
        url: 请求地址
        data：请求体数据
        method：请求方式
        """
        logger.info(f"UserManageApi  request_method method={method},headers={self.header}, url={url},data={data}")

        func = getattr(requests, method)
        req = func(url=url, data=json.dumps(data), headers=self.header, verify=False)
        res = req.json()

        logger.info(f"UserManageApi  request_method res={res}")
        return res

    # def get_departments(self):
    #     """
    #     获取部门，分清楚哪些是本地local可改，和不可以修改的目录
    #     """
    #     url = r"http://paas.weops.com/{}/bk_user_manage/api/v2/departments/?only_enabled=true".format(self.version)
    #     res = requests.get(url=url, headers=self.header)
    #     return res.json()

    def add_bk_user_manage(self, data):
        """
        新增用户 POST
        data: 新增用户的数据 dict
        """
        copy_add_user_template = copy.deepcopy(self.add_user_template)
        copy_add_user_template.update(data)  # 把数据加到模版里
        req = self.request_method(url=self.add_user_url, data=copy_add_user_template, method="post")
        return req

    def update_bk_user_manage(self, data, id):
        """
        修改用户信息
        method: PATCH
        data: 修改用户的数据 dict
        id: bk_user_id (用户管理处的id)
        """
        url = f"{self.add_user_url}{id}/"
        req = self.request_method(url=url, data=data, method="patch")
        return req

    def reset_passwords(self, id, data):
        """
        重制密码
        method: PATCH
        id: bk_user_id (用户管理处的id)
        data: 密码 dict
        """
        url = f"{self.add_user_url}{id}/"
        req = self.request_method(url=url, data=data, method="patch")
        return req

    def delete_bk_user_manage(self, data):
        """
        删除用户
        method: DELETE
        data: 用户id [{"id":10}]
        """
        header = copy.deepcopy(self.header)
        header.update({"Content-Type": "application/json"})
        req = requests.delete(url=self.delete_user_url, headers=header, json=data, verify=False)

        return json.loads(req.text)

    def create_categories(self, data):
        """
        创建组织
        data:
        {
            "type":"local",
            "display_name":"测试公司11",
            "domain":"default.local11",
            "activated":true
        }
        """
        header = copy.deepcopy(self.header)
        header.update({"Content-Type": "application/json"})
        req = self.request_method(url=self.categories_url, data=data, method="post")
        return req

    def create_departments(self, data):
        """
        创建组织下的根组织
        data:
        {"name":"鞍山市1","category_id":6}
        """
        header = copy.deepcopy(self.header)
        header.update({"Content-Type": "application/json"})
        req = self.request_method(url=self.departments_url, data=data, method="post")
        return req

    def update_user_status(self, data):
        """
        禁用/开启用户
        data:
        开启：{status: "NORMAL"}
                禁用：{status: "DISABLED"}
        """

        user_id = data.pop("user_id")
        path = f"{self.add_user_url}{user_id}/"

        header = copy.deepcopy(self.header)
        header.update({"Content-Type": "application/json"})
        req = self.request_method(url=path, data=data, method="patch")
        return req
