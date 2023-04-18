# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging

from django.contrib.auth.backends import ModelBackend

from blueapps.account import get_user_model
from blueapps.account.components.weixin.weixin_utils import WechatUtils
from blueapps.account.conf import ConfFixture
from blueapps.account.utils.http import send
from blueapps.core.exceptions import BlueException
from blueking.component.shortcuts import get_client_by_user

logger = logging.getLogger("component")


class WeixinBackend(ModelBackend):
    def authenticate(self, request=None, code=None, is_wechat=True):
        """
        is_wechat 参数是为了使得 WeixinBackend 与其他 Backend 参数个数不同，在框架选择
        认证 backend 时，快速定位
        """
        logger.debug("进入 WEIXIN 认证 Backend")
        if not code:
            return None

        # result, user_info = self.verify_weixin_code(code)
        result, user_info = self.get_weixin_user(code)

        if not result:
            return 0

        user_model = get_user_model()
        try:
            user, _ = user_model.objects.get_or_create(username=user_info["username"])
            user.nickname = user_info["display_name"]
            user.save()
            # user.avatar_url = user_info["avatar"]
        except Exception:
            logger.exception("自动创建 & 更新 User Model 失败")
        else:
            return user

    def get_user(self, user_id):
        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None

    def get_weixin_user(self, code):
        result, query_param = WechatUtils.check_login_code(code)
        if not result:
            return False, None
        try:
            data = send(ConfFixture.WEIXIN_INFO_URL, "GET", query_param)
            if data.get("errcode") and data.get("errcode") != 0:
                logger.error("通过微信授权码，获取用户信息失败，errcode={}，errmsg={}".format(data["errcode"], data["errmsg"]))
                return False, None
            weixin_user_id = data["UserId"]
            user = self.get_bk_user(weixin_user_id)
            logger.error(user)
            return True, user
        except BlueException:
            logger.exception("通过微信授权码，获取用户信息异常")
            return False, None

    def get_bk_user(self, weixin_user_id):
        client = get_client_by_user("admin")
        result = client.usermanage.retrieve_user(
            {"id": weixin_user_id, "lookup_field": "wx_userid", "fields": "username,display_name"}
        )
        if not result["result"]:
            logger.exception(result["message"])
            raise BlueException()
        return result["data"]
