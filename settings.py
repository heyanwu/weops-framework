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

import os
import sys

"""
请不要修改该文件
如果你需要对settings里的内容做修改，config/default.py 文件中 添加即可
如有任何疑问，请联系 【蓝鲸助手】
"""
if not hasattr(sys, "argv"):
    sys.argv = [""]

# V3判断环境的环境变量为BKPAAS_ENVIRONMENT
if "BKPAAS_ENVIRONMENT" in os.environ:
    ENVIRONMENT = os.getenv("BKPAAS_ENVIRONMENT", "dev")
# V2判断环境的环境变量为BK_ENV
else:
    PAAS_V2_ENVIRONMENT = os.environ.get("BK_ENV", "development")
    ENVIRONMENT = {"development": "dev", "testing": "stag", "production": "prod"}.get(PAAS_V2_ENVIRONMENT)
DJANGO_CONF_MODULE = "config.{env}".format(env=ENVIRONMENT)

try:
    _module = __import__(DJANGO_CONF_MODULE, globals(), locals(), ["*"])
except ImportError as e:
    raise ImportError("Could not import config '{}' (Is it on sys.path?): {}".format(DJANGO_CONF_MODULE, e))

for _setting in dir(_module):
    if _setting == _setting.upper():
        locals()[_setting] = getattr(_module, _setting)

INSTALLED_APPS = locals()["INSTALLED_APPS"]
CELERY_IMPORTS = locals()["CELERY_IMPORTS"]
MIDDLEWARE = locals()["MIDDLEWARE"]

try:
    __module = __import__("home_application.config", globals(), locals(), ["*"])
except ImportError:
    pass
else:
    for _setting in dir(__module):
        if _setting == _setting.upper():
            locals()[_setting] = getattr(__module, _setting)
        elif _setting == "app_name":
            INSTALLED_APPS += getattr(__module, _setting)
        elif _setting == "celery_tasks":
            CELERY_IMPORTS += getattr(__module, _setting)

apps = {"apps": os.listdir("apps"), "apps_other": os.listdir("apps_other")}
for key, app_list in apps.items():
    dir_list = [i for i in app_list if os.path.isdir(f"{key}/{i}") and not i.startswith("__")]

    for i in dir_list:
        try:
            __module = __import__(f"{key}.{i}.config", globals(), locals(), ["*"])
        except ImportError:
            pass
        else:
            for _setting in dir(__module):
                if _setting == _setting.upper():
                    locals()[_setting] = getattr(__module, _setting)
                elif _setting == "app_name":
                    INSTALLED_APPS += (getattr(__module, _setting),)
                elif _setting == "celery_tasks":
                    CELERY_IMPORTS += getattr(__module, _setting)
                elif _setting == "add_middleware":
                    MIDDLEWARE += getattr(__module, _setting)
