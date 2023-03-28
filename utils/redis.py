# -- coding: utf-8 --

# @File : redis.py
# @Time : 2022/10/15 15:13
# @Author : windyzhao
import redis
from django.conf import settings

"""
此redis连接只提供给自动采集任务连接到auto-mate服务，查询task的执行状态
"""
pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    db=int(settings.AUTO_MATE_REDIS_DB),
    max_connections=50,
    decode_responses=True,
    encoding="utf8",
)  # db需要和auto-mate的redis的db一致
redis_client = redis.Redis(connection_pool=pool)
