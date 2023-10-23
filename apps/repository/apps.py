# -*- coding: utf-8 -*-

# @File    : apps.py
# @Date    : 2022-04-02
# @Author  : windyzhao
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import ugettext_lazy as _


class RepositoryConfig(AppConfig):
    name = "apps.repository"
    verbose_name = _("repository")

    def ready(self):
        from apps.repository.utils import RepositoryUtils

        post_migrate.connect(RepositoryUtils.init_repository_template, sender=self)
