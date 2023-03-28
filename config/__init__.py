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

from __future__ import absolute_import

import os
from urllib.parse import urlparse

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from blueapps.core.celery import celery_app

__all__ = ["celery_app", "RUN_VER", "APP_CODE", "SECRET_KEY", "BK_URL", "BASE_DIR"]


# app 基本信息


def get_env_or_raise(key):
    """Get an environment variable, if it does not exist, raise an exception"""
    value = os.environ.get(key)
    if not value:
        raise RuntimeError(
            'Environment variable "{}" not found, you must set this variable to run this application.'.format(key)
        )
    return value


# 应用 ID
APP_ID = APP_CODE = os.getenv("APP_ID", "weops_saas")

# APP_ID = APP_CODE = "open-app-check"
# 应用用于调用云 API 的 Secret
APP_TOKEN = SECRET_KEY = os.getenv("APP_TOKEN", "166e8c8b-41ba-4e35-85ea-d4bb4864cf82")
# APP_TOKEN = SECRET_KEY = "42ba1f8b-7485-497b-8469-8dcc750539ad"
# SaaS运行版本，如非必要请勿修改
RUN_VER = "open"
# 蓝鲸SaaS平台URL，例如 http://paas.bking.com
BK_PAAS_HOST = os.getenv("BK_PAAS_HOST", "http://paas.weops.com")
# BK_PAAS_HOST = "https://paas.cwbk.com"
BK_URL = os.getenv("BK_URL", BK_PAAS_HOST)
# BK_URL = "https://paas.cwbk.com"
BK_PAAS_DOMAIN = urlparse(BK_PAAS_HOST).hostname
BK_DOMAIN = os.getenv("BKAPP_DOMAIN", "." + BK_PAAS_DOMAIN.split(".", 1)[-1])
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MONITOR = "{}/t/{}".format(BK_URL, "monitor-center")
VAULT_URL = os.getenv("BKAPP_VAULT_URL", "http://vault.weops.com")
VAULT_TOKEN = os.getenv("BKAPP_VAULT_TOKEN", "hvs.iw0mQExGLhcr81Ik1fqalyJA")
DECODE_TOKEN = b"D4eqLDQjsQvDDSldYtcd3SmeUhoyQym2"

# 是否展示3D大屏
IS_3D_SCREEN = os.getenv("BKAPP_IS_3D_SCREEN", "1")

# datacenter root目录
DATACENTER_ROOT = os.getenv("BKAPP_DATACENTER_ROOT", "Datacenter")
