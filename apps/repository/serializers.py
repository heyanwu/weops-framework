# -*- coding: utf-8 -*-

# @File    : serializers.py
# @Date    : 2022-04-02
# @Author  : windyzhao
import json

from drf_haystack import serializers as drf_haystack_serializers
from drf_haystack.serializers import HaystackSerializer
from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework.serializers import ModelSerializer

from apps.repository.constants import SEARCH_TYPE_COLLECT, SEARCH_TYPE_USER
from apps.repository.models import Repository, RepositoryLabels, RepositoryTemplate
from apps.repository.search_indexes import RepositoryIndex
from apps.system_mgmt.models import SysUser
from common.sys_user_utils import user_cache


class RepositoryIndexHaystackSerializer(HaystackSerializer):
    """
    全文检索的序列化器
    """

    id = drf_haystack_serializers.serializers.SerializerMethodField()
    labels = drf_haystack_serializers.serializers.SerializerMethodField()
    update_time = drf_haystack_serializers.serializers.SerializerMethodField()
    content = drf_haystack_serializers.serializers.SerializerMethodField()
    collect = drf_haystack_serializers.serializers.SerializerMethodField()
    created_by = drf_haystack_serializers.serializers.SerializerMethodField()
    username = drf_haystack_serializers.serializers.SerializerMethodField()

    def __init__(self, instance=None, data=empty, **kwargs):
        super(RepositoryIndexHaystackSerializer, self).__init__(instance, data, **kwargs)
        request = kwargs["context"]["request"]
        user = SysUser.objects.get(bk_username=request.user.username)
        user_collect_repository_list = list(user.collect_users.all().values_list("id", flat=True))
        self.user_collect_repository_list = user_collect_repository_list

        # 获取当前分页的用户的用户名称
        username_qs = SysUser.objects.filter(bk_username__in=[i.created_by for i in instance]).values_list(
            "bk_username", "chname"
        )
        self.username_mapping = dict(username_qs)

    class Meta:
        index_classes = [RepositoryIndex]
        search_fields = ["text"]
        fields = ["id", "title", "content", "created_by", "labels", "collect", "updated_at", "username"]

    @staticmethod
    def _object(obj):
        return getattr(obj, "object")

    def get_username(self, obj):
        _object = self._object(obj)
        if _object is None:
            return ""
        return obj.object.created_by

    def get_created_by(self, obj):
        return self.username_mapping.get(obj.created_by, obj.created_by)

    @staticmethod
    def get_id(obj):
        return obj.repository_id

    def get_labels(self, obj):
        _object = self._object(obj)
        if _object is None:
            return []
        else:
            return [i.label_name for i in _object.labels.all()]

    def get_update_time(self, obj):
        _object = self._object(obj)
        if _object is None:
            return "--"
        return obj.object.updated_at.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def get_content(obj):
        content = obj.content[:100]
        return f"{content}..." if len(content) == 100 else content

    def get_collect(self, obj):
        # 是否是我的收藏
        return obj.repository_id in self.user_collect_repository_list


class RepositoryInstPermissionsSerializer(ModelSerializer):
    class Meta:
        model = Repository
        fields = ["id", "title", "created_at", "created_by"]


class RepositoryModelSerializer(ModelSerializer):
    update_time = serializers.SerializerMethodField()
    labels = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    collect = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

    def __init__(self, instance=None, data=empty, **kwargs):
        super(RepositoryModelSerializer, self).__init__(instance=instance, data=data, **kwargs)
        request = kwargs["context"]["request"]
        user = SysUser.objects.get(bk_username=request.user.username)
        user_collect_repository_list = list(user.collect_users.all().values_list("id", flat=True))
        self.user_collect_repository_list = user_collect_repository_list
        # 获取当前分页的用户的用户名称
        self.username_mapping = user_cache()

    class Meta:
        model = Repository
        fields = [
            "id",
            "created_at",
            "title",
            "content",
            "created_by",
            "labels",
            "collect",
            "update_time",
            "username",
            "is_it_service",
        ]

    @staticmethod
    def get_username(obj):
        return obj.created_by

    def get_created_by(self, obj):
        return self.username_mapping.get(obj.created_by, obj.created_by)

    @staticmethod
    def get_content(obj):
        content = obj.content[:100]
        return f"{content}..." if len(content) == 100 else content

    @staticmethod
    def get_update_time(obj):
        return obj.updated_at.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def get_labels(obj):
        return [i.label_name for i in obj.labels.all()]

    def get_collect(self, obj):
        # 是否是我的收藏
        return obj.id in self.user_collect_repository_list


class RepositoryRetrieveModelSerializer(ModelSerializer):
    update_time = serializers.SerializerMethodField()
    create_time = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()

    labels = serializers.SerializerMethodField()
    collect = serializers.SerializerMethodField()
    body = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    drafts = serializers.SerializerMethodField()

    class Meta:
        model = Repository
        fields = [
            "id",
            "title",
            "labels",
            "created_by",
            "updated_by",
            "update_time",
            "create_time",
            "collect",
            "body",
            "username",
            "images",
            "drafts",
        ]

    @staticmethod
    def get_username(obj):
        return obj.created_by

    @staticmethod
    def get_updated_by(obj):
        user = SysUser.objects.filter(bk_username=obj.updated_by).first()
        if user is None:
            return obj.updated_by
        return user.chname

    @staticmethod
    def get_created_by(obj):
        user = SysUser.objects.filter(bk_username=obj.created_by).first()
        if user is None:
            return obj.created_by
        return user.chname

    @staticmethod
    def get_body(obj):
        if isinstance(obj.body, str):
            return json.loads(obj.body)
        return obj.body

    @staticmethod
    def get_update_time(obj):
        return obj.updated_at.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def get_create_time(obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def get_labels(obj):
        return [{"id": i.id, "label_name": i.label_name} for i in obj.labels.all()]

    def get_collect(self, obj):
        # 是否是我的收藏
        request = self.context.get("request")
        user_collect_bool = obj.collect_users.filter(bk_username=request.user.username).exists()
        return user_collect_bool

    @staticmethod
    def get_images(obj):
        if isinstance(obj.images, str):
            return json.loads(obj.images)
        return obj.images

    @staticmethod
    def get_drafts(obj):
        # 此文章是否存在草稿
        drafts = Repository.objects.filter(drafts=True, base_id=obj.id).first()
        if drafts is None:
            return 0
        return drafts.id


class RepositoryLabelsModelSerializer(ModelSerializer):
    use_count = serializers.SerializerMethodField()

    class Meta:
        model = RepositoryLabels
        fields = ["id", "label_name", "use_count"]

    def get_use_count(self, obj):
        request = self.context.get("request")
        search_type = request.GET.get("search_type")
        is_it_service = request.GET.get("is_it_service") == "true"
        query_set = obj.repository_labels.filter(drafts=False)
        if is_it_service:
            query_set = obj.repository_labels.filter(is_it_service=is_it_service)

        if search_type == SEARCH_TYPE_USER:
            count = query_set.filter(created_by=request.user.username).count()
        elif search_type == SEARCH_TYPE_COLLECT:
            count = query_set.filter(collect_users__bk_username=request.user.username).count()
        else:
            count = query_set.count()
        return count


class RepositoryTemplateModelSerializer(ModelSerializer):
    class Meta:
        model = RepositoryTemplate
        fields = ["id", "template_name", "title", "template_img", "body", "images"]
        extra_kwargs = {"body": {"write_only": True}}


class RepositoryDraftsSerializer(ModelSerializer):
    """
    草稿箱查询
    """

    updated_at = serializers.DateTimeField()
    username = serializers.CharField(source="created_by")

    class Meta:
        model = Repository
        fields = ["id", "title", "updated_at", "base_id", "username"]
