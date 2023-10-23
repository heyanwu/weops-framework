# -- coding: utf-8 --

# @File : minio_client.py
# @Time : 2023/3/13 15:05
# @Author : windyzhao

from django.conf import settings
from django_minio_backend import MinioBackend

from common.minio_utils import MinIoClient

if settings.DEBUG:
    minio_client = MinIoClient()
    fake_minio_client = minio_client
else:
    minio_backend = MinioBackend()
    minio_client = MinIoClient(minio_client=minio_backend.client)

    if minio_backend.same_endpoints:
        fake_minio_client = minio_client  # 内部
    else:
        fake_minio_client = MinIoClient(minio_client=minio_backend.client_fake)  # 外部
