# -- coding: utf-8 --

# @File : views.py
# @Time : 2022/9/19 11:35
# @Author : windyzhao


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

import datetime
import json
import os

from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response

from apps.activation.helper import aes_decrypt
from apps.activation.models import Activation, Log
from apps.activation.serializers import ActivationSerializer
from apps.activation.utils.constants import MENUS_DEFAULT, MENUS_MAPPING
from apps.activation.utils.view_mixin import ReModelViewSet
from blueapps.account.decorators import login_exempt
from blueapps.utils.logger import logger


def get_sys_info(request):
    try:
        return JsonResponse(
            {"result": True, "data": {"username": request.user.username, "roles": ["admin"], "logout_url": ""}}
        )
    except Exception as e:
        return JsonResponse({"result": False, "message": str(e)})


@csrf_exempt
@login_exempt
def get_applications(request):
    """
    查询weops功能模块
    """
    res = MENUS_DEFAULT
    res.update(MENUS_MAPPING)

    return JsonResponse({"result": True, "data": res})


@login_exempt
@csrf_exempt
def check_node_nums(request):
    obj = Activation.objects.first()
    if not obj:
        return JsonResponse({"result": False, "message": "未注册，激活码不存在"})
    return JsonResponse({"result": True, "data": {"agent_num": obj.agent_num}})


@login_exempt
@csrf_exempt
def set_expired_notify_day(request):
    if request.method != "POST":
        return JsonResponse({"result": False})

    params = json.loads(request.body)
    Activation.objects.update(notify_day=params["notify_day"])
    return JsonResponse({"result": True})


@login_exempt
@csrf_exempt
def check_activation(request):
    try:
        obj = Activation.objects.filter().first()
        registration_code = obj.registration_code
        activation_code = obj.activation_code
        res, activation_data = aes_decrypt(activation_code)
        activation_data = json.loads(activation_data)

        if registration_code != activation_data["registration_code"]:
            Log.objects.create(desc="注册码校验失败")
            return JsonResponse({"result": False, "message": "注册码校验失败"})

        if str(datetime.datetime.now().date()) > activation_data["expiration_date"]:
            Log.objects.create(desc="授权已到期")
            return JsonResponse({"result": False, "message": "授权已到期"})

        if activation_data["activation_status"] == "试用期":
            file_path = "USERRES/never_delete"
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    first_date = f.read()
                    first_date = aes_decrypt(first_date)[1]
                    if activation_data["start_date"] != first_date:
                        return JsonResponse({"result": False, "message": "试用信息校验失败"})
            else:
                return JsonResponse({"result": False, "message": "试用期校验文件异常"})

        return JsonResponse({"result": True})

    except Exception as e:
        logger.exception(e)
        return JsonResponse({"result": False, "message": str(e)})


class ActivationModelViewSet(ReModelViewSet):
    """
    激活码管理
    """

    serializer_class = ActivationSerializer

    def get_queryset(self):
        return Activation.objects.all()

    def list(self, request, *args, **kwargs):
        """
        查询激活码
        """
        activation_obj = Activation.objects.filter().first()
        serializer = self.get_serializer(activation_obj, many=False)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        """
        修改激活码
        """
        try:
            params = request.data
            activation_code = params["activation_code"]
            activation_obj = Activation.objects.first()
            result, activation_data = aes_decrypt(activation_code)
            activation_data = json.loads(activation_data)
            obj_data = {
                "registration_code": activation_data["registration_code"],
                "start_date": activation_data["start_date"],
                "expiration_date": activation_data["expiration_date"],
                "activation_status": activation_data["activation_status"],
                "agent_num": int(activation_data.get("agent_num", 0)),
                "applications": activation_data["applications"],
            }
            if obj_data["registration_code"] != activation_obj.registration_code:
                return JsonResponse({"result": False, "message": "注册码校验失败"})

            now_date = datetime.datetime.now()
            expiration_date = datetime.datetime.strptime(obj_data["expiration_date"], "%Y-%m-%d")
            valid_days = (expiration_date - now_date).days
            if valid_days < 0:
                return JsonResponse({"result": False, "message": "激活码无效或已过期"})

            obj_data["activation_code"] = activation_code
            Activation.objects.filter().update(**obj_data)

            # 缓存，app权限中间件使用到
            cache.set("activation_data", obj_data)

            return JsonResponse({"result": True})
        except Exception as e:
            logger.exception(e)
            return JsonResponse({"result": False, "message": "激活码无效或已过期"})
