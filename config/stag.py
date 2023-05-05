# -*- coding: utf-8 -*-
import os  # noqa

from config import RUN_VER

if RUN_VER == "open":
    from blueapps.patch.settings_open_saas import *  # noqa
else:
    from blueapps.patch.settings_paas_services import *  # noqa

# 预发布环境
RUN_MODE = "STAGING"

DATABASES.update(  # noqa
    {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.getenv("BKAPP_DB_NAME", ""),  # 数据库名
            "USER": os.getenv("BKAPP_DB_USERNAME", ""),  # 数据库用户
            "PASSWORD": os.getenv("BKAPP_DB_PASSWORD", ""),  # 数据库密码
            "HOST": os.getenv("BKAPP_DB_HOST", ""),  # 数据库主机
            "PORT": os.getenv("BKAPP_DB_PORT", "3306"),  # 数据库端口
        },
    }
)
