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
import traceback

from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.db import IntegrityError

from blueapps.account import get_user_model
from blueapps.account.conf import ConfFixture
from blueapps.account.utils.http import send
from blueapps.utils import client

logger = logging.getLogger("component")

ROLE_TYPE_ADMIN = "1"

class LoginBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        logger.debug(u"Enter in TokenBackend")
        user_model = get_user_model()
        try:
            user = user_model.objects.get(username=username)
        except Exception as e:
            return None
        if user.check_password(password):
            return user
