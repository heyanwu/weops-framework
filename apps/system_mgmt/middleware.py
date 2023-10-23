# -*- coding: utf-8 -*-

# @File    : middleware.py
# @Date    : 2022-06-08
# @Author  : windyzhao
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

from apps.system_mgmt.constants import MENUS_CHOOSE_MAPPING
from apps.system_mgmt.sys_setting import sys_setting
from utils.app_log import logger


class ApplicationMenusPermission(MiddlewareMixin):
    """
    权限控制 控制所有的接口是否有访问权限
    默认有权限 拿到有权限的接口
    取反 获取没有
    重新激活weops后，获取新的数据，重新加载新的权限
    """

    _init_permission = False
    _not_application_paths = set()  # 没有权限的功能的url
    _has_activation_data = []  # 有权限

    def init_menus(self):
        """
        初始化weops的功能模块
        """

        activation_data_cache = cache.get("activation_data")
        if activation_data_cache:
            # 更改最新的apps
            self._init_permission = False
            activation_data = activation_data_cache
        else:
            activation_data = sys_setting.activation_data or {}

        if self._init_permission:
            return

        try:
            self._init_permission = True
            logger.info("==activation_data==", activation_data)
            has_activation_data = activation_data.get("applications", [])
            self._has_activation_data = has_activation_data

            not_permission_set = set()
            for application, urls in MENUS_CHOOSE_MAPPING.items():
                if application in has_activation_data:
                    continue

                for url in urls:
                    if not url.startswith("/"):
                        url = "/{}".format(url)
                    if not url.endswith("/"):
                        url = "{}/".format(url)
                    not_permission_set.add(url)

            self._not_application_paths = not_permission_set

            if activation_data_cache:
                cache.delete("activation_data")

            logger.info("==初始化了weops功能模块的权限==")
            logger.info("==_not_application_paths=={}".format(self._not_application_paths))
            logger.info("==_has_activation_data=={}".format(self._has_activation_data))
        except Exception as err:
            # 若初始化失败，那么重新恢复，重新再新的请求中初始化
            logger.exception("初始化weops功能模块的权限失败: error={}".format(err))
            self._init_permission = False
            self._not_application_paths = set()
            self._has_activation_data = []

            if activation_data_cache:
                cache.set("activation_data", activation_data_cache)

    def process_request(self, request):

        if settings.DEBUG:
            return None

        self.init_menus()

        # 默认没有权限的可以全部访问
        if not self._has_activation_data:
            return None

        response = None

        for url in self._not_application_paths:
            if request.path.startswith(url):
                logger.info("未通过url={}".format(request.path))
                response = JsonResponse({"result": False, "code": "40300", "message": "您没有访问此功能的权限! ", "data": None})
                response.status_code = 403
                break

        return response
