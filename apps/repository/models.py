# -*- coding: utf-8 -*-

# @File    : models.py
# @Date    : 2022-04-02
# @Author  : windyzhao

import json

from django.db import models
from django_mysql.models import JSONField

from apps.repository.constants import REPOSITORY_UPLOAD_TO
from apps.system_mgmt.models import SysUser
from utils.common_models import MaintainerInfo, TimeInfo


class RepositoryTemplate(TimeInfo, MaintainerInfo):
    """
    文章模版 和文章一对多
    """

    template_name = models.CharField(max_length=64, unique=True, help_text="模版名称")
    title = models.CharField(max_length=255, default="", null=True, blank=True, help_text="模版文章名称")
    template_img = models.CharField(max_length=100, null=True, blank=True, help_text="模版图片")
    body = JSONField(help_text="模版内容")
    labels = models.ManyToManyField("RepositoryLabels", help_text="标签")
    images = JSONField(help_text="文件名称列表", default=json.dumps({}))  # {"uuid_": "图片1.jpg, "uuid2": 图片2.jpg"}

    class Meta:
        verbose_name = "模版"


class RepositoryLabels(TimeInfo, MaintainerInfo):
    """
    标签 和文章多对多
    """

    label_name = models.CharField(max_length=255, unique=True, help_text="标签名称")

    def __str__(self):
        return self.label_name

    class Meta:
        verbose_name = "标签"


class Repository(TimeInfo, MaintainerInfo):
    """
    文章
    """

    upload_to = REPOSITORY_UPLOAD_TO

    title = models.CharField(max_length=255, help_text="文章标题")
    content = models.TextField(help_text="文章内容")
    body = models.TextField(default=json.dumps([]), help_text="文章完整内容")
    template = models.ForeignKey(RepositoryTemplate, on_delete=models.CASCADE)
    collect_users = models.ManyToManyField(
        SysUser, through="RepositoryCollectUser", related_name="collect_users", help_text="收藏用户"
    )
    labels = models.ManyToManyField(
        RepositoryLabels, through="Labels", related_name="repository_labels", help_text="标签"
    )
    images = JSONField(help_text="文件名称列表", default=json.dumps({}))  # {"uuid": "123.jpeg"}
    is_it_service = models.BooleanField(default=False, help_text="是否为IT服务台文章")
    drafts = models.BooleanField(default=False, help_text="是否为草稿")
    base_id = models.IntegerField(default=0, help_text="草稿原文id")

    class Meta:
        verbose_name = "文章"

    @property
    def get_labels_names(self):
        return ",".join(self.labels.all().values_list("label_name", flat=True))


class RepositoryCollectUser(models.Model):
    repository = models.ForeignKey("Repository", on_delete=models.CASCADE)
    user = models.ForeignKey(SysUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(help_text="收藏时间", auto_now_add=True, db_index=True)
    deleted_at = models.DateTimeField(help_text="取消收藏时间", auto_now=True)


class Labels(models.Model):
    repository = models.ForeignKey("Repository", related_name="repository_labels", on_delete=models.CASCADE)
    repository_labels = models.ForeignKey(RepositoryLabels, on_delete=models.CASCADE)
    created_at = models.DateTimeField(help_text="使用时间", auto_now_add=True, db_index=True)
    deleted_at = models.DateTimeField(help_text="取消时间", auto_now=True)
