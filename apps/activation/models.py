# -- coding: utf-8 --

# @File : models.py
# @Time : 2022/9/19 11:38
# @Author : windyzhao

from django.db import models
from django_mysql.models import JSONField


class Activation(models.Model):
    """激活许可"""

    registration_code = models.CharField(u"注册码", max_length=100, null=False)
    activation_code = models.CharField(u"激活码", max_length=1024, null=False)
    start_date = models.CharField(u"起始时间", max_length=100, null=False)
    expiration_date = models.CharField(u"结束时间", max_length=100, null=False)
    activation_status = models.CharField(u"激活状态", max_length=100, null=False)
    agent_num = models.IntegerField("节点数", default=0)
    applications = JSONField("功能模块", default=list)
    notify_day = models.IntegerField("到期提醒", default=30)


class Log(models.Model):
    """错误日志"""

    create_time = models.DateTimeField("创建时间", auto_now_add=True, blank=True, null=True)
    desc = models.TextField("描述", blank=True, null=True)
