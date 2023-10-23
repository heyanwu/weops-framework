# -- coding: utf-8 --

# @File : config.py
# @Time : 2023/3/9 14:00
# @Author : windyzhao

import distutils.util
import os
from datetime import timedelta
from typing import List, Tuple

from django.conf import settings

# app注册
app_name = "apps.repository"

# CELERY 配置，申明任务的文件路径，即包含有 @task 装饰器的函数文件
CELERY_IMPORTS = ("apps.repository.celery_task",)

HAYSTACK_CONNECTIONS = {
    "default": {
        # 使用whoosh引擎
        # 'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        "ENGINE": "apps.repository.whoosh_cn_backend.WhooshEngine",
        # 索引文件路径
        "PATH": os.path.join(settings.BASE_DIR, "USERRES", "whoosh_index"),  # noqa
    }
}

# 当添加、修改、删除数据时，自动生成索引
# HAYSTACK_SIGNAL_PROCESSOR = "haystack.signals.RealtimeSignalProcessor"


# 以下是minio的配置

DEFAULT_BK_PAAS_HOST = os.getenv("BK_PAAS_HOST", "http://paas.weops.com")

MINIO_ENDPOINT = os.getenv("BKAPP_GH_MINIO_ENDPOINT", DEFAULT_BK_PAAS_HOST)  # 内部节点
MINIO_EXTERNAL_ENDPOINT = os.getenv(
    "BKAPP_MINIO_EXTERNAL_ENDPOINT", DEFAULT_BK_PAAS_HOST
)  # 外部节点 Default is same as MINIO_ENDPOINT
# MINIO_EXTERNAL_ENDPOINT_USE_HTTPS = False
MINIO_EXTERNAL_ENDPOINT_USE_HTTPS = bool(
    distutils.util.strtobool(os.getenv("BKAPP_GH_MINIO_EXTERNAL_ENDPOINT_USE_HTTPS", "false"))
)  # Default is same as MINIO_USE_HTTPS
MINIO_ACCESS_KEY = os.getenv("BKAPP_GH_MINIO_ACCESS_KEY", "6WVIL8GRLF0RU6Z0G3GP")
MINIO_SECRET_KEY = os.getenv("BKAPP_GH_MINIO_SECRET_KEY", "qm02lZjy2lZVFPwMnfN++Hp4dq+NtO2d548K77U4")
MINIO_USE_HTTPS = bool(distutils.util.strtobool(os.getenv("BKAPP_GH_MINIO_USE_HTTPS", "false")))
# MINIO_USE_HTTPS = False
MINIO_URL_EXPIRY_HOURS = timedelta(days=1)  # Default is 7 days (longest) if not defined
MINIO_CONSISTENCY_CHECK_ON_START = True  # minio 一致性检查 开发模式建议关闭

REPOSITORY_BUCKET = "weops-repository-private"  # 知识库桶

MINIO_PRIVATE_BUCKETS = getattr(settings, "MINIO_PRIVATE_BUCKETS", [])
# MINIO_PUBLIC_BUCKETS = getattr(settings, "MINIO_PRIVATE_BUCKETS", [])

MINIO_PRIVATE_BUCKETS.append(REPOSITORY_BUCKET)

MINIO_POLICY_HOOKS: List[Tuple[str, dict]] = [
    # (PROFILE_BUCKET, dummy_policy)
]  # 策略钩子

# MINIO_MEDIA_FILES_BUCKET = 'my-media-files-bucket'  # replacement for MEDIA_ROOT
# MINIO_STATIC_FILES_BUCKET = 'my-static-files-bucket'  # replacement for STATIC_ROOT
MINIO_BUCKET_CHECK_ON_SAVE = True  # Default: True // Creates bucket if missing, then save

DEFAULT_FILE_STORAGE = "django_minio_backend.models.MinioBackend"

# 以上是minio的配置

if settings.DEBUG:
    MINIO_ENDPOINT = "127.0.0.1:9001"
    MINIO_EXTERNAL_ENDPOINT = "127.0.0.1:9001"
    MINIO_USE_HTTPS = False
    MINIO_EXTERNAL_ENDPOINT_USE_HTTPS = False
    MINIO_ACCESS_KEY = "admin"
    MINIO_SECRET_KEY = "1234567890"
