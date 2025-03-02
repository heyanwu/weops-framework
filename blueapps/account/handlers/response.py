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
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse
from django.utils.translation import ugettext_lazy as _

from blueapps.account.utils.http import build_redirect_url
from blueapps.core.exceptions import BkJwtVerifyError, RioVerifyError

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse

logger = logging.getLogger("component")


class ResponseHandler(object):
    def __init__(self, _conf_fixture, _settings):
        """
        @param {object} confFixture Account Package Settings
        @param {object} settings Django User Settings
        """
        self._conf = _conf_fixture
        self._settings = _settings

    def build_401_response(self, request):

        # 强制要求进行跳转的方式
        if getattr(settings, "IS_AJAX_PLAIN_MODE", False) and request.is_ajax():
            return self._build_ajax_401_response(request)

        # Just redirect to PAAS-LOGIN-PLATRORM no matter whether request.is_ajax
        if self._conf.HAS_PLAIN:
            if request.is_ajax():
                return self._build_ajax_401_response(request)
            else:
                return self._build_page_401_response(request)
        else:
            if request.is_ajax():
                context = {"has_plain": False}
                return JsonResponse(context, status=401)
            else:
                return self._build_page_401_response_to_platform(request)

    def _build_ajax_401_response(self, request):
        """
        Return 401 info, inlclude login_url to PAAS-LOGIN-PLATFORM,
        width & height for adjusting iframe window, login_url as
        http://xxx/login/?c_url=http%3A//xxx/t/data/&app_id=data
        """
        _next = request.build_absolute_uri(reverse("account:login_success"))

        if self._conf.ADD_CROSS_PREFIX:
            _next = self._conf.CROSS_PREFIX + _next

        _login_url = build_redirect_url(
            _next, self._conf.LOGIN_PLAIN_URL, self._conf.C_URL, extra_args=self._build_extra_args()
        )

        context = {
            "login_url": _login_url,
            "width": self._conf.IFRAME_WIDTH,
            "height": self._conf.IFRAME_HEIGHT,
            "has_plain": True,
        }
        return JsonResponse(context, status=401)

    def _build_page_401_response(self, request):
        """
        Redirect to login page in self app, redirect url format as
        http://xxx:8000/account/login_page/?refer_url=http%3A//xxx%3A8000/
        """
        _login_url = request.build_absolute_uri(reverse("account:login_page"))

        _next = request.build_absolute_uri()
        _redirect = build_redirect_url(_next, _login_url, "refer_url")
        return HttpResponseRedirect(_redirect)

    def _build_page_401_response_to_platform(self, request):
        """
        Directly redirect to PAAS-LOGIN-PLATFORM
        """
        _next = request.build_absolute_uri()
        if self._conf.ADD_CROSS_PREFIX:
            _next = self._conf.CROSS_PREFIX + _next

        _login_url = build_redirect_url(
            _next, self._conf.LOGIN_URL, self._conf.C_URL, extra_args=self._build_extra_args()
        )
        return HttpResponseRedirect(_login_url)

    def _build_extra_args(self):
        extra_args = None
        if self._conf.ADD_APP_CODE:
            extra_args = {self._conf.APP_KEY: getattr(self._settings, self._conf.SETTINGS_APP_KEY)}
        return extra_args

    def get_oauth_redirect_url(self, callback_url, state="authenticated"):
        """
        获取oauth访问链接
        """
        params = {
            "appid": self._conf.WEIXIN_APP_ID,
            "redirect_uri": callback_url,
            "response_type": "code",
            "scope": "snsapi_userinfo",
            "state": state,
        }
        params = urllib.parse.urlencode(params)
        redirect_uri = "{}?{}#wechat_redirect".format(self._conf.WEIXIN_OAUTH_URL, params)
        return redirect_uri

    def redirect_weixin_login(self, request):
        """
        跳转到微信登录
        """
        url = urllib.parse.urlparse(request.build_absolute_uri())
        callback_url = url.scheme + r"://" + self._conf.WEIXIN_APP_EXTERNAL_HOST + request.get_full_path()
        state = request.session["WEIXIN_OAUTH_STATE"]
        redirect_uri = self.get_oauth_redirect_url(callback_url, state)
        return HttpResponseRedirect(redirect_uri)

    def build_weixin_401_response(self, request):
        """
        todo，说明 url 格式
        """
        _login_url = self._conf.WEIXIN_OAUTH_URL
        _next = request.build_absolute_uri()

        extra_args = {
            "appid": self._conf.WEIXIN_APP_ID,
            "response_type": "code",
            "scope": "snsapi_base",
            "state": request.session["WEIXIN_OAUTH_STATE"],
        }
        logger.error(f"回调参数：{extra_args}, login_url: {_login_url}; _next: {_next}")
        _redirect = build_redirect_url(_next, _login_url, "redirect_uri", extra_args=extra_args)
        logger.error(f"_redirect: {_redirect}")
        return HttpResponseRedirect(_redirect)

    def build_rio_401_response(self, request):
        context = {"result": False, "code": RioVerifyError.ERROR_CODE, "message": _("您的登陆请求无法经智能网关正常检测，请与管理人员联系")}
        return JsonResponse(context, status=401)

    def build_bk_jwt_401_response(self, request):
        """
        BK_JWT鉴权异常
        """
        context = {"result": False, "code": BkJwtVerifyError.ERROR_CODE, "message": _("您的登陆请求无法经BK JWT检测，请与管理人员联系")}
        return JsonResponse(context, status=401)
