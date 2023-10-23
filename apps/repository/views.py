# -*- coding: utf-8 -*-

# @File    : dashboard_views.py
# @Date    : 2022-04-02
# @Author  : windyzhao
from django.db import transaction
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.repository.controller import RepositoryController, RepositoryTemplateController
from apps.repository.filters import RepositoryFilter, RepositoryLabelsFilter, RepositoryTemplateFilter
from apps.repository.models import Repository, RepositoryLabels, RepositoryTemplate
from apps.repository.permissions import RepositoryInstPermission
from apps.repository.search_indexes import RepositoryIndex
from apps.repository.serializers import (
    RepositoryDraftsSerializer,
    RepositoryLabelsModelSerializer,
    RepositoryModelSerializer,
    RepositoryRetrieveModelSerializer,
    RepositoryTemplateModelSerializer,
)
from apps.system_mgmt.casbin_package.permissions import (
    RepositoryItServerTagPermission,
    RepositoryRoleOperatePermission,
    UserSuperPermission,
)
from apps.system_mgmt.models import OperationLog, SysRole
from apps.system_mgmt.pages import LargePageNumberPagination
from common.casbin_inst_service import CasBinInstService
from packages.drf.viewsets import ModelViewSet
from utils.app_log import logger
from utils.decorators import ApiLog


class RepositoryModelViewSet(ModelViewSet):
    """
    知识库文章
    """

    permission_classes = [IsAuthenticated, UserSuperPermission, RepositoryRoleOperatePermission]
    queryset = Repository.objects.all().prefetch_related("labels")
    serializer_class = RepositoryModelSerializer
    filter_class = RepositoryFilter
    ordering_fields = ["id"]
    ordering = ["-id"]
    pagination_class = LargePageNumberPagination

    @property
    def permissions_actions(self):
        """权限校验action"""
        return ["drafts", "update", "destroy"]

    def get_permissions(self):
        if self.action in self.permissions_actions:
            _permission_classes = [permission() for permission in self.permission_classes]
            _permission_classes += [RepositoryInstPermission()]
            return _permission_classes
        return super().get_permissions()

    @action(methods=["GET"], detail=False, url_path="rebuild")
    @ApiLog("知识库文章手动更新索引")
    def rebuild(self, request, *args, **kwargs):
        RepositoryController.rebuild()
        return Response(data=[])

    @ApiLog("知识库文章获取单个文章")
    def retrieve(self, request, *args, **kwargs):
        instance = self.queryset.get(**kwargs)
        serializer = RepositoryRetrieveModelSerializer(instance, context={"request": request})
        return Response(serializer.data)

    @ApiLog("知识库文章查询")
    def list(self, request, *args, **kwargs):
        search = request.GET.get("text")

        if search:
            response = RepositoryController.get_repository_controller(self=self)
            return response

        return super().list(request, *args, **kwargs)

    @action(methods=["POST"], detail=False)
    @ApiLog("知识库文章新增草稿")
    def drafts(self, request, *args, **kwargs):
        res = RepositoryController.create_or_update_drafts(request=request)
        return Response(**res)

    @ApiLog("知识库文章新增文章")
    def create(self, request, *args, **kwargs):
        res = RepositoryController.create_repository_controller(request=request)
        return Response(**res)

    @ApiLog("知识库文章修改文章")
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        res = RepositoryController.update_repository_controller(request=request, self=self)
        return Response(**res)

    @ApiLog("知识库文章删除文章")
    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        with transaction.atomic():
            sid = transaction.savepoint()
            try:
                _instance = self.get_object()
                res = RepositoryController.delete_repository_controller(request=request, self=self)
                role_names = SysRole.get_user_roles(_instance.created_by)
                policies = [[role_name, "知识库", "manage", str(res["data"]), "0"] for role_name in role_names]
                result = CasBinInstService.remove_policies(policies=policies, sec="p", ptype="p")
                if not result:
                    raise Exception("权限同步到casbin失败!")
            except Exception as err:
                logger.exception("删除文章失败！error={}".format(err))
                transaction.savepoint_rollback(sid)
                transaction.savepoint_commit(sid)
                return Response({"detail": "删除运维工具失败！"}, status=500)

        return Response(**res)

    @action(methods=["POST"], detail=True, url_path="repository_collect")
    @ApiLog("知识库文章收藏文章")
    def repository_collect(self, request, *args, **kwargs):
        """
        收藏文章
        '/repository/25/repository_collect/'
        """
        res = RepositoryController.add_repository_collect(self=self, username=request.user.username, request=request)
        return Response(**res)

    @action(methods=["POST"], detail=True, url_path="repository_cancel_collect")
    @ApiLog("知识库文章取消收藏文章")
    @transaction.atomic
    def repository_cancel_collect(self, request, *args, **kwargs):
        """
        取消收藏
        """
        res = RepositoryController.cancel_repository_collect(self=self, username=request.user.username, request=request)
        return Response(**res)

    @action(
        methods=["PATCH"],
        detail=True,
        url_path=r"is_it_service/(?P<judge>.+?)",
        permission_classes=[RepositoryItServerTagPermission, RepositoryInstPermission],
    )
    @ApiLog("修改文章是否属于IT服务台文章")
    def update_repository(self, request, pk, judge):
        """修改文章是否属于IT服务台文章"""
        RepositoryController.update_repository_is_it_service(pk, judge, request=request)
        return Response()

    @action(methods=["POST"], detail=False)
    def upload_repositories(self, request, *args, **kwargs):
        """
        批量上传文件生成知识库文章
        """
        res = RepositoryController.upload_repositories_controller(request=request)
        return Response(**res)

    @action(methods=["POST"], detail=False, url_path="delete_images")
    @ApiLog("知识库文章批量删除图片")
    def delete_files(self, request, *args, **kwargs):
        """
        批量删除文件
        """

        files = request.data["images"]
        template = request.data.get("template", False)  # 区分模版和知识库的不同路径
        RepositoryController.delete_files(files, template)

        return Response()

    @action(methods=["POST"], detail=False, url_path="get_images")
    @ApiLog("知识库批量获取图片链接")
    def get_files_url(self, request, *args, **kwargs):
        """
        批量获取文件链接
        """
        res = RepositoryController.get_files_url(request.data)
        return Response(data=res)

    @action(methods=["POST"], detail=False)
    def upload_files(self, request, *args, **kwargs):
        """
        知识库上传图片后，返回图片链接
        """
        file = request.FILES.get("file")
        file_name = request.data.get("file_name")
        template = request.data.get("template", False)  # 区分模版和知识库的不同路径
        current_ip = request.COOKIES.get("current_ip", "127.0.0.1")
        file_url = RepositoryController.upload_image(request, file, file_name, template)

        OperationLog.objects.create(
            operator=request.user.username,
            operate_type=OperationLog.ADD,
            operate_obj=file_name,
            operate_summary="知识库上传图片：[{}]".format(file_name),
            current_ip=current_ip,
            app_module="知识库",
            obj_type="知识文章",
        )

        return Response(data=file_url)

    @ApiLog("知识库查询草稿")
    @action(methods=["GET"], detail=False)
    def get_drafts(self, request, *args, **kwargs):
        """
        查询草稿
        """
        username = request.user.username
        instances = Repository.objects.filter(
            Q(drafts=True) & (Q(created_by=username) | Q(updated_by=username))
        ).order_by("-updated_at")
        paginator = self.pagination_class()
        page_list = paginator.paginate_queryset(instances, self.request, view=self)
        serializer = RepositoryDraftsSerializer(page_list, many=True)
        response = paginator.get_paginated_response(serializer.data)

        return response


class RepositoryLabelsModelViewSet(ModelViewSet):
    """
    文章标签
    """

    permission_classes = [IsAuthenticated]
    queryset = RepositoryLabels.objects.all().prefetch_related("repository_labels")
    serializer_class = RepositoryLabelsModelSerializer
    filter_class = RepositoryLabelsFilter
    ordering_fields = ["id"]
    ordering = ["-id"]
    pagination_class = LargePageNumberPagination

    @ApiLog("知识库管理标签查询标签")
    def list(self, request, *args, **kwargs):
        page_size = request.GET.get("page_size")
        if page_size == "-1":
            # 获取全部标签 无汇总使用统计
            res = list(RepositoryLabels.objects.all().values("id", "label_name").order_by("-id"))
            return Response(data={"items": res})
        if page_size == "-2":
            # 获取全部标签的汇总使用统计，过滤掉使用为0的，按照使用大小排序
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            res = [i for i in serializer.data if i["use_count"]]
            res.sort(key=lambda x: x["use_count"], reverse=True)
            return Response(data={"items": res})

        return super().list(request, *args, **kwargs)

    @ApiLog("知识库管理标签新增标签")
    def create(self, request, *args, **kwargs):
        res = super().create(request, *args, **kwargs)
        current_ip = getattr(request, "current_ip", "127.0.0.1")
        OperationLog.objects.create(
            operator=request.user.username,
            operate_type=OperationLog.ADD,
            operate_obj=request.data["label_name"],
            operate_summary="新增标签，标签名称：[{}]".format(request.data["label_name"]),
            current_ip=current_ip,
            app_module="知识库",
            obj_type="文章标签",
        )

        return res

    @ApiLog("知识库管理标签修改标签")
    def update(self, request, *args, **kwargs):
        res = super().update(request, *args, **kwargs)
        instance = self.get_object()
        repository_list = instance.repository_labels.all()
        for repository in repository_list:
            # 更新此标签影响的文章
            RepositoryIndex().update_object(instance=repository)

        current_ip = getattr(request, "current_ip", "127.0.0.1")
        OperationLog.objects.create(
            operator=request.user.username,
            operate_type=OperationLog.MODIFY,
            operate_obj=request.data["label_name"],
            operate_summary="修改标签，标签名称：[{}]".format(request.data["label_name"]),
            current_ip=current_ip,
            app_module="知识库",
            obj_type="文章标签",
        )

        return res

    @ApiLog("知识库管理标签删除标签")
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        repository_list = instance.repository_labels.all()
        instance_id = instance.id
        self.perform_destroy(instance)

        current_ip = getattr(request, "current_ip", "127.0.0.1")
        OperationLog.objects.create(
            operator=request.user.username,
            operate_type=OperationLog.DELETE,
            operate_obj=instance.label_name,
            operate_summary="删除标签，标签名称：[{}]".format(instance.label_name),
            current_ip=current_ip,
            app_module="知识库",
            obj_type="文章标签",
        )

        for repository in repository_list:
            # 更新此标签影响的文章
            RepositoryIndex().update_object(instance=repository)
        return Response(instance_id)


class RepositoryTemplateModelViewSet(ModelViewSet):
    """
    文章模版
    """

    permission_classes = [IsAuthenticated]
    queryset = RepositoryTemplate.objects.all()
    serializer_class = RepositoryTemplateModelSerializer
    filter_class = RepositoryTemplateFilter
    ordering_fields = ["id"]
    ordering = ["id"]
    pagination_class = LargePageNumberPagination

    @ApiLog("知识库管理模版获取单个模版")
    def retrieve(self, request, *args, **kwargs):
        res = RepositoryTemplateController.retrieve_repository_template_controller(self=self)
        return Response(res)

    @ApiLog("知识库管理模版查询模版")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @ApiLog("知识库管理模版创建模版")
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        创建文章模版
        """
        res = RepositoryTemplateController.create_repository_template_controller(request=request, self=self)
        return Response(**res)

    @ApiLog("知识库管理模版修改模版")
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """
        修改文章模版
        """
        res = RepositoryTemplateController.update_repository_template_controller(request=request, self=self)
        return Response(**res)

    @ApiLog("知识库管理模版删除模版")
    def destroy(self, request, *args, **kwargs):
        """
        删除文章模版
        """
        res = RepositoryTemplateController.delete_repository_template_controller(request=request, self=self)
        return Response(**res)
