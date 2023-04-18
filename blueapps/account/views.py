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
import time

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render

from blueapps.account.components.weixin.weixin_utils import WechatUtils
from blueapps.account.decorators import login_exempt

logger = logging.getLogger("component")


@login_exempt
def login_success(request):
    """
    弹框登录成功返回页面
    """
    return render(request, "account/login_success.html")


@login_exempt
def login_page(request):
    """
    跳转至固定页面，然后弹框登录
    """
    refer_url = request.GET.get("refer_url")

    context = {"refer_url": refer_url}
    return render(request, "account/login_page.html", context)


def send_code_view(request):
    ret = request.user.send_code()
    return JsonResponse(ret)


def get_user_info(request):
    return JsonResponse(
        {
            "code": 0,
            "data": {"id": request.user.id, "username": request.user.username, "timestamp": time.time()},
            "message": "ok",
        }
    )


@login_exempt
def weixin_login(request):
    if not request.is_wechat():
        return HttpResponse("非微信访问，或应用未启动微信访问")
    # 验证回调state
    if not verify_weixin_oauth_state(request):
        return HttpResponse("State验证失败")
    # 验证code有效性
    logger.exception(f"请求参数： {request.GET.dict()}")
    is_code_valid, base_data = verify_weixin_oauth_code(request)
    if not is_code_valid:
        # TODO 改造为友好页面
        return HttpResponse("登录失败")
    # 设置登录
    callback_url = request.GET.get("c_url") or settings.SITE_URL
    logger.error(f"c_url: {callback_url}")
    return HttpResponseRedirect(callback_url)


def verify_weixin_oauth_state(request, expires_in=60):
    """
    验证state是否正确，防止csrf攻击
    """
    try:
        state = request.GET.get("state")
        raw_state = request.session.get("WEIXIN_OAUTH_STATE")
        raw_timestamp = request.session.get("WEIXIN_OAUTH_STATE_TIMESTAMP")
        # 验证state
        if not raw_state or raw_state != state:
            return False
        # 验证时间戳
        if not raw_timestamp or time.time() - raw_timestamp > expires_in:
            return False
        # 验证成功后清空session
        request.session["WEIXIN_OAUTH_STATE"] = None
        request.session["WEIXIN_OAUTH_STATE_TIMESTAMP"] = None
        return True
    except Exception as e:
        logger.exception("验证请求weixin code的 state参数出错： %s" % e)
        return False


def verify_weixin_oauth_code(request):
    """
    验证Code有效性
    """
    code = request.GET.get("code")
    is_ok, data = WechatUtils.check_login_code(code)
    return is_ok, data
