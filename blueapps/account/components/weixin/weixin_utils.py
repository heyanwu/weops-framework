import hashlib
import logging

from django.core.cache import cache

from blueapps.account.conf import ConfFixture
from blueapps.account.utils.http import send

logger = logging.getLogger("component")


class WechatUtils(object):
    get_jsapi_ticket = "https://qyapi.weixin.qq.com/cgi-bin/get_jsapi_ticket"

    @staticmethod
    def check_login_code(code):
        """
        校验登录回调code
        """

        # query_param = {
        #     "appid": ConfFixture.WEIXIN_APP_ID,
        #     "secret": ConfFixture.WEIXIN_APP_SECRET,
        #     "code": code,
        #     "grant_type": "authorization_code",
        # }

        query_param = {
            "corpid": ConfFixture.WEIXIN_APP_ID,
            "corpsecret": ConfFixture.WEIXIN_APP_SECRET,
        }
        data = send(ConfFixture.WEIXIN_URL, "GET", query_param)
        access_token = data.get("access_token")
        if access_token is None:
            logger.exception(f"登录票据CODE接口返回无access_token, {data}")
            return False, {}
        # return True, {"access_token": access_token, "openid": openid}
        return True, {"access_token": access_token, "code": code}

    @staticmethod
    def generate_signature(data):
        query_string = "&".join([f"{key}={data[key]}" for key in data])
        sha1_hash = hashlib.sha1()
        # 将字符串传递给哈希对象
        sha1_hash.update(query_string.encode("utf-8"))
        # 获取加密后的结果
        hashed_text = sha1_hash.hexdigest()
        # 打印结果
        return hashed_text

    @staticmethod
    def jsapi_ticket():
        cache_jsapi_ticket = cache.get("WX_JSAPI_TICKET")
        if cache_jsapi_ticket:
            return cache_jsapi_ticket

        access_token = cache.get("WX_ACCESS_TOKEN")
        if not access_token:
            success, data = WechatUtils.check_login_code(code="")
            if not success:
                raise SystemError("获取微信/企业微信APP_ID失败")
            access_token = data.get("access_token")
            cache.set("WX_ACCESS_TOKEN", access_token, 7000)

        ticket_data = send(WechatUtils.get_jsapi_ticket, "GET", {"access_token": access_token})

        if ticket_data["errcode"]:
            logger.exception("获取微信/企业微信JSAPI_TICKET失败！,error={}".format(ticket_data["errmsg"]))
            raise SystemError("获取微信/企业微信JSAPI_TICKET失败")

        cache.set("WX_JSAPI_TICKET", ticket_data["ticket"], 7000)

        return ticket_data["ticket"]
