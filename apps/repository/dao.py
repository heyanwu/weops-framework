# -*- coding: utf-8 -*-

# @File    : dao.py
# @Date    : 2022-04-08
# @Author  : windyzhao
from apps.repository.constants import BLANK_TEMPLATE_DATA
from apps.repository.models import RepositoryTemplate
from apps.system_mgmt.utils_package.dao import ModelOperate


class RepositoryModels(ModelOperate):
    @classmethod
    def get_blank_template(cls):
        """
        获取空白模版
        """
        instance = RepositoryTemplate.objects.get(template_name=BLANK_TEMPLATE_DATA["template_name"])

        return instance.id
