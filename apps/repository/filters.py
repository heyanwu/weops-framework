# -*- coding: utf-8 -*-

# @File    : filters.py
# @Date    : 2022-04-12
# @Author  : windyzhao
from django.db.models import Q
from django_filters import CharFilter, FilterSet

from apps.repository.constants import SEARCH_TYPE_COLLECT, SEARCH_TYPE_USER
from apps.repository.models import Repository, RepositoryLabels, RepositoryTemplate
from common.casbin_inst_service import CasBinInstService


class RepositoryFilter(FilterSet):
    """文章过滤器"""

    label_id = CharFilter(method="filter_label_id", label="全局模糊搜索")
    search_type = CharFilter(method="filter_type", label="类型查询")
    is_it_service = CharFilter(method="filter_is_it_service", label="类型查询")

    class Meta:
        models = Repository
        fields = ["search_type", "label_id"]

    @property
    def qs(self):
        """
        非超管时查询：
            自己的创建+有权的文章+服务台文章
        """
        parent = super().qs
        if self.request.method == "GET":
            parent = parent.filter(drafts=False)
        if not self.request.user.is_super:
            username = self.request.user.username
            instances = CasBinInstService.get_user_instances(username=username, instance_type="知识库")
            parent = parent.filter(Q(is_it_service=True) | Q(created_by=username) | Q(id__in=instances))

        return parent

    @staticmethod
    def filter_label_id(qs, field_name, value):
        """全局模糊过滤查询 查询标签下的"""
        return RepositoryLabels.objects.get(id=value).repository_labels.all()

    def filter_type(self, qs, field_name, value):
        """我的收藏文章/我的文章 查询"""
        if value == SEARCH_TYPE_USER:
            return qs.filter(created_by=self.request.user.username)
        if value == SEARCH_TYPE_COLLECT:
            return qs.filter(collect_users__bk_username=self.request.user.username)

        return qs

    @staticmethod
    def filter_is_it_service(qs, field_name, value):
        if value == "true":
            return qs.filter(is_it_service=True)
        elif value == "false":
            return qs.filter(is_it_service=False)
        return qs


class RepositoryLabelsFilter(FilterSet):
    """标签过滤器"""

    search = CharFilter(method="filter_search", label="全局模糊搜索")
    search_type = CharFilter(method="filter_type", label="类型查询")

    class Meta:
        models = RepositoryLabels
        fields = ["search", "search_type"]

    @staticmethod
    def filter_search(qs, field_name, value):
        """全局模糊过滤查询"""
        return qs.filter(label_name__icontains=value)

    def filter_type(self, qs, field_name, value):
        """我的收藏文章/我的文章 的标签查询"""
        if value == SEARCH_TYPE_USER:
            return qs.filter(repository_labels__created_by=self.request.user.username).distinct()
        if value == SEARCH_TYPE_COLLECT:
            return qs.filter(repository_labels__collect_users__bk_username=self.request.user.username).distinct()

        return qs

    @property
    def qs(self):
        parent = super().qs
        # parent = parent.filter(labels__repository__drafts=False)

        return parent


class RepositoryTemplateFilter(FilterSet):
    """模版过滤器"""

    search = CharFilter(method="filter_search", label="全局模糊搜索")

    class Meta:
        models = RepositoryTemplate
        fields = ["search"]

    @staticmethod
    def filter_search(qs, field_name, value):
        """全局模糊过滤查询"""
        return qs.filter(template_name__icontains=value)
