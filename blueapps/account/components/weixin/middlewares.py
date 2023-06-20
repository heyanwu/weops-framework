import logging
import random
import time
import traceback

from django.conf import settings
from django.contrib import auth
from django.core.cache import caches
from django.db import IntegrityError
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

from blueapps.account import get_user_model
from blueapps.account.components.weixin.forms import WeixinAuthenticationForm
from blueapps.account.conf import ConfFixture
from blueapps.account.handlers.response import ResponseHandler
from blueapps.account.utils.http import send
from blueapps.utils import client
from utils.token import generate_bk_token, set_bk_token_to_open_pass_db

logger = logging.getLogger("component")

ROLE_TYPE_ADMIN = "1"

cache = caches["login_db"]


class WeixinLoginRequiredMiddleware(MiddlewareMixin):
    def process_view(self, request, view, args, kwargs):
        """
        可通过登录认证的方式，仅有两种
        1. 带有 login_exemp 标识的 view 函数
        2. 用户已成功 auth.login
        """
        # 框架前置中间件，已将识别的客户端信息填充进 request
        if not request.is_wechat():
            return None

        login_exempt = getattr(view, "login_exempt", False)
        if not (login_exempt or request.user.is_authenticated):
            bk_token = request.COOKIES.get("bk_token", "")
            if bk_token:
                is_authenticate = self.authenticate_user(bk_token, request)
                if is_authenticate:
                    return None

            form = WeixinAuthenticationForm(request.GET)

            if form.is_valid():
                code = form.cleaned_data["code"]
                state = form.cleaned_data["state"]

                if self.valid_state(request, state):
                    user = auth.authenticate(request=request, code=code, is_wechat=True)
                    if user == 0:
                        return JsonResponse({"result": False, "message": "用户验证失败!"})
                    if user and user.username != request.user.username:
                        auth.login(request, user)
                    if request.user.is_authenticated:
                        # 登录成功，确认登陆正常后退出
                        return None
            else:
                logger.error("微信请求链接，未检测到微信验证码，url：{}，params：{}".format(request.path_info, request.GET))

            self.set_state(request)
            handler = ResponseHandler(ConfFixture, settings)
            # return handler.build_weixin_401_response(request)
            return handler.redirect_weixin_login(request)
        return None

    def process_response(self, request, response):
        if not request.is_wechat():
            return response
        if not request.user.username:
            return response
        if request.COOKIES.get("bk_token"):
            return response
        bk_token, expire_time = generate_bk_token(request.user.username)
        set_bk_token_to_open_pass_db(bk_token, expire_time)
        response.set_cookie("bk_token", bk_token, max_age=60 * 60 * 12, domain=settings.BK_DOMAIN, httponly=True)
        return response

    @staticmethod
    def set_state(request, length=32):
        """
        生成随机数 state，表示客户端的当前状态，根据 oauth2.0 标准，在请求授权码时需要
        附带上的参数，认证服务器的回应必须一模一样包含这个参数，此处将 state 设置在
        session
        """
        allowed_chars = "abcdefghijkmnpqrstuvwxyz" "ABCDEFGHIJKLMNPQRSTUVWXYZ" "0123456789"
        state = "".join(random.choice(allowed_chars) for _ in range(length))
        request.session["WEIXIN_OAUTH_STATE"] = state
        request.session["WEIXIN_OAUTH_STATE_TIMESTAMP"] = time.time()
        return True

    @staticmethod
    def valid_state(request, state, expires_in=60):
        """
        验证微信认证服务器返回的 code & state 是否合法
        """
        raw_state = request.session.get("WEIXIN_OAUTH_STATE")
        raw_timestamp = request.session.get("WEIXIN_OAUTH_STATE_TIMESTAMP")

        if not raw_state or raw_state != state:
            logger.error("验证 WEIXIN 服务器返回信息，state 不一致，" "WEIXIN_OAUTH_STATE=%s，state=%s" % (raw_state, state))
            return False

        if not raw_timestamp or time.time() - raw_timestamp > expires_in:
            logger.error("验证 WEIXIN 服务器返回信息，state 过期，" "WEIXIN_OAUTH_STATE_TIMESTAMP=%s" % (raw_timestamp))
            return False

        request.session["WEIXIN_OAUTH_STATE"] = None
        request.session["WEIXIN_OAUTH_STATE_TIMESTAMP"] = None
        return True

    def get_user(self, bk_token):
        api_params = {"bk_token": bk_token}
        try:
            response = send(ConfFixture.VERIFY_URL, "GET", api_params, verify=False)
        except Exception:
            logger.exception(u"Abnormal error in verify_bk_token...")
            return None
        if not response.get("result"):
            error_msg = response.get("message", "")
            error_data = response.get("data", "")
            logger.error(u"Fail to verify bk_token, error={}, ret={}".format(error_msg, error_data))
            return
        data = response.get("data")
        username = data.get("username")
        user_model = get_user_model()
        try:
            user, _ = user_model.objects.get_or_create(username=username)
            get_user_info_result, user_info = self.get_user_info(bk_token)
            # 判断是否获取到用户信息,获取不到则返回None
            if not get_user_info_result:
                return None
            user.set_property(key="qq", value=user_info.get("qq", ""))
            user.set_property(key="language", value=user_info.get("language", ""))
            user.set_property(key="time_zone", value=user_info.get("time_zone", ""))
            user.set_property(key="role", value=user_info.get("role", ""))
            user.set_property(key="phone", value=user_info.get("phone", ""))
            user.set_property(key="email", value=user_info.get("email", ""))
            user.set_property(key="wx_userid", value=user_info.get("wx_userid", ""))
            user.set_property(key="chname", value=user_info.get("chname", ""))

            # 用户如果不是管理员，则需要判断是否存在平台权限，如果有则需要加上
            if not user.is_superuser and not user.is_staff:
                role = user_info.get("role", "")
                is_admin = True if str(role) == ROLE_TYPE_ADMIN else False
                user.is_superuser = is_admin
                user.is_staff = is_admin
                user.save()
            return user
        except IntegrityError:
            logger.exception(traceback.format_exc())
            logger.exception(u"get_or_create UserModel fail or update_or_create UserProperty")
            return None
        except Exception:
            logger.exception(traceback.format_exc())
            logger.exception(u"Auto create & update UserModel fail")
            return None

    @staticmethod
    def get_user_info(bk_token):
        api_params = {"bk_token": bk_token}
        try:
            response = client.bk_login.get_user(api_params)
        except Exception as e:
            logger.exception(u"Abnormal error in get_user_info...:%s" % e)
            return False, {}

        if response.get("result") is True:
            # 由于v1,v2的get_user存在差异,在这里屏蔽字段的差异,返回字段相同的字典
            origin_user_info = response.get("data", "")
            user_info = dict()
            # v1,v2字段相同的部分
            user_info["wx_userid"] = origin_user_info.get("wx_userid", "")
            user_info["language"] = origin_user_info.get("language", "")
            user_info["time_zone"] = origin_user_info.get("time_zone", "")
            user_info["phone"] = origin_user_info.get("phone", "")
            user_info["chname"] = origin_user_info.get("chname", "")
            user_info["email"] = origin_user_info.get("email", "")
            user_info["qq"] = origin_user_info.get("qq", "")
            # v2版本特有的字段
            if settings.DEFAULT_BK_API_VER == "v2":
                user_info["username"] = origin_user_info.get("bk_username", "")
                user_info["role"] = origin_user_info.get("bk_role", "")
            # v1版本特有的字段
            elif settings.DEFAULT_BK_API_VER == "":
                user_info["username"] = origin_user_info.get("username", "")
                user_info["role"] = origin_user_info.get("role", "")
            return True, user_info
        else:
            error_msg = response.get("message", "")
            error_data = response.get("data", "")
            logger.error(u"Failed to Get User Info: error={err}, ret={ret}".format(err=error_msg, ret=error_data,))
            return False, {}

    def authenticate_user(self, bk_token, request):
        session_key = request.session.session_key
        if session_key:
            # 确认 cookie 中的 ticket 和 cache 中的是否一致
            cache_session = cache.get(session_key)
            is_match = cache_session and bk_token == cache_session.get("bk_token")
            if is_match and request.user.is_authenticated:
                return True
        user = self.get_user(bk_token)
        if user:
            auth.login(request, user)
            session_key = request.session.session_key
            if not session_key:
                logger.info("删除了session_session_key")
                request.session.cycle_key()
            session_key = request.session.session_key
            cache.set(session_key, {"bk_token": bk_token}, settings.LOGIN_CACHE_EXPIRED)
            return True
        return False
