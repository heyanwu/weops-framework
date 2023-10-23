# -*- coding: utf-8 -*-

# @File    : controller.py
# @Date    : 2022-04-08
# @Author  : windyzhao
import json
import time

from django.db import transaction
from django.db.models import Q

from apps.repository.celery_task import async_delete_minio_images
from apps.repository.constants import BLANK_TEMPLATE_NAME, REPOSITORY_UPLOAD_TO, SEARCH_TYPE_ALL, TEMPLATE_UPLOAD_TO
from apps.repository.dao import RepositoryModels
from apps.repository.models import Repository, RepositoryLabels
from apps.repository.search_indexes import RepositoryIndex
from apps.repository.serializers import RepositoryIndexHaystackSerializer
from apps.repository.utils import IndexesUtils, RepositoryUtils
from apps.repository.utils_package.pandoc_utils import DocxChangeMarkdownUtils
from apps.system_mgmt.models import OperationLog, SysRole
from blueapps.core.exceptions import ParamValidationError
from common.casbin_inst_service import CasBinInstService
from utils.app_log import logger

"""
知识库和模版

涉及到图片组件
再删除图片时(修改/删除文件/模版时)
获取到模版和文章的图片，
判断删除的图片，是否被模版或者其余模版关联的文章引用了
若引用了 不删除
未引用 删除
"""


class RepositoryController(object):
    @classmethod
    def rebuild(cls, *args, **kwargs):
        """
        手动更新索引接口
        """
        logger.info("开始手动更新索引接口")
        RepositoryIndex().reindex()
        logger.info("手动更新索引接口结束")

    @classmethod
    def get_repository_controller(cls, *args, **kwargs):
        """
        查询文章 走全文检索 排序按照id倒叙
        """
        self = kwargs["self"]
        id_list = kwargs.get("id_list", [])
        search = self.request.GET.get("text")
        label_id = self.request.GET.get("label_id")
        search_type = self.request.GET.get("search_type")
        is_it_service = self.request.GET.get("is_it_service")

        if (label_id or is_it_service or search_type != SEARCH_TYPE_ALL) or (not self.request.user.is_super):
            # 通过标签查询/或者查询方式不是全部的 走过滤器 拿id
            id_list = list(self.filter_queryset(self.get_queryset()).values_list("id", flat=True))

        model_serializer = RepositoryIndexHaystackSerializer
        index_queryset = IndexesUtils.get_indexes_data(search=search, id_list=id_list)
        if not index_queryset.count():
            index_queryset = (
                self.filter_queryset(self.get_queryset())
                .filter(drafts=False)
                .filter(
                    Q(title__contains=search) | Q(content__contains=search) | Q(labels__label_name__contains=search)
                )
                .order_by("-id")
                .distinct()
            )
            model_serializer = self.serializer_class

        response = RepositoryUtils.get_serializer(
            self=self, instances=index_queryset, model_serializer=model_serializer
        )
        return response

    @classmethod
    def create_or_update_drafts(cls, *args, **kwargs):
        """
        创建/修改草稿箱
        """
        request = kwargs["request"]
        labels, instance_data = RepositoryUtils.get_create_repository_data(data=request.data)

        # 草稿箱逻辑
        instance_data = cls.add_drafts_data(instance_data)

        # 复制模版图片，并补全(图片组件，非md)
        instance_data, _copy_images = RepositoryUtils.add_repository_use_template_img(instance_data=instance_data)
        # 复制body里content的图片
        _copy_md_images = RepositoryUtils.copy_repository_image(instance_data=instance_data)
        # 创建失败，需要删除的图片
        _copy_images.extend(_copy_md_images)

        instance_data["created_by"] = request.user.username
        instance_data["body"] = json.dumps(instance_data["body"])
        repository_id = instance_data.get("base_id", 0)

        with transaction.atomic():
            try:

                if repository_id > 0:
                    Repository.objects.filter(drafts=True, base_id=repository_id).delete()  # 删除旧的草稿

                instance = RepositoryModels.model_create(model_objects=Repository, data=instance_data)

                if labels:
                    labels_instances = RepositoryLabels.objects.filter(id__in=labels)
                    RepositoryModels.add_many_to_many_field(
                        instance=instance, add_attr="labels", add_data=labels_instances
                    )

                OperationLog.objects.create(
                    operator=request.user.username,
                    operate_type=OperationLog.ADD,
                    operate_obj=instance.title,
                    operate_summary="创建草稿，草稿名称为：[{}]".format(instance.title),
                    current_ip=request.current_ip,
                    app_module="知识库",
                    obj_type="知识文章",
                )

                role_names = SysRole.get_user_roles(request.user.username)
                policies = [[role_name, "知识库", "manage", str(instance.id), "0"] for role_name in role_names]
                result = CasBinInstService.create_policies(policies=policies, sec="p", ptype="p")
                if not result:
                    raise Exception("权限同步到casbin失败!")

                return {"data": instance.id}

            except Exception as err:
                logger.exception("创建草稿失败! error={}".format(err))
                if _copy_images:
                    transaction.on_commit(lambda: async_delete_minio_images.delay(REPOSITORY_UPLOAD_TO, _copy_images))
                return {"data": {"detail": "创建草稿失败！"}, "status": 500}

    @classmethod
    def create_repository_controller(cls, *args, **kwargs):
        """
        创建文章
        """
        request = kwargs["request"]
        labels, instance_data = RepositoryUtils.get_create_repository_data(data=request.data)

        # 复制模版图片，并补全(图片组件，非md)
        instance_data, _copy_images = RepositoryUtils.add_repository_use_template_img(instance_data=instance_data)
        # 复制body里content的图片
        _copy_md_images = RepositoryUtils.copy_repository_image(instance_data=instance_data)
        # 创建失败，需要删除的图片
        _copy_images.extend(_copy_md_images)

        instance_data["created_by"] = request.user.username
        instance_data["body"] = json.dumps(instance_data["body"])

        with transaction.atomic():
            try:
                instance = RepositoryModels.model_create(model_objects=Repository, data=instance_data)

                if labels:
                    labels_instances = RepositoryLabels.objects.filter(id__in=labels)
                    RepositoryModels.add_many_to_many_field(
                        instance=instance, add_attr="labels", add_data=labels_instances
                    )
                OperationLog.objects.create(
                    operator=request.user.username,
                    operate_type=OperationLog.ADD,
                    operate_obj=instance.title,
                    operate_summary="创建文章，文章名称为：[{}]".format(instance.title),
                    current_ip=request.current_ip,
                    app_module="知识库",
                    obj_type="知识文章",
                )
                role_names = SysRole.get_user_roles(request.user.username)
                policies = [[role_name, "知识库", "manage", str(instance.id), "0"] for role_name in role_names]
                result = CasBinInstService.create_policies(policies=policies, sec="p", ptype="p")
                if not result:
                    raise Exception("权限同步到casbin失败!")
                return {"data": instance.id}
            except Exception as err:
                logger.exception("创建文章失败! error={}".format(err))
                if _copy_images:
                    transaction.on_commit(lambda: async_delete_minio_images.delay(REPOSITORY_UPLOAD_TO, _copy_images))
                return {"data": {"detail": "创建文章失败！"}, "status": 500}

    @classmethod
    def update_repository_controller(cls, *args, **kwargs):
        """
        修改文章
        若修改的对象是草稿时，存在base_id，
        且不是草稿箱，那么删除此文章的草稿
        """
        self = kwargs["self"]
        request = kwargs["request"]
        instance = self.get_object()

        labels, instance_data = RepositoryUtils.get_create_repository_data(data=request.data)

        instance_data.pop("base_id", 0)
        instance_data.pop("template_id", False)
        instance_data["updated_by"] = request.user.username
        instance_data["body"] = json.dumps(instance_data["body"])

        with transaction.atomic():
            if instance.drafts and not instance_data["drafts"]:
                # 旧文章为草稿，新文章不为草稿，需要把草稿内容修改到base_id的文章里，删除此草稿
                base_repository = Repository.objects.filter(id=instance.base_id).first()
                if base_repository is not None:
                    # 只需要把原文章的id指向草稿id即可
                    instance.id = base_repository.id
                    instance.save()
                    base_repository.delete()
                    # template_delete_images = RepositoryUtils.repository_delete_image(instance)
                    # RepositoryUtils.minio_delete_objects(delete_images=template_delete_images)
                    # instance = base_repository

            RepositoryModels.model_update(data=instance_data, instance=instance)
            labels_instances = RepositoryLabels.objects.filter(id__in=labels)
            RepositoryModels.update_many_to_many_field(instance=instance, add_attr="labels", add_data=labels_instances)

            OperationLog.objects.create(
                operator=request.user.username,
                operate_type=OperationLog.MODIFY,
                operate_obj=instance.title,
                operate_summary="修改{}，名称为：[{}]".format("草稿" if instance.drafts else "文章", instance.title),
                current_ip=request.current_ip,
                app_module="知识库",
                obj_type="知识文章",
            )

        logger.info("修改文章结束，创建操作日志结束, 开始更新索引--")
        RepositoryIndex().update_object(instance=instance)
        logger.info("修改文章结束，更新索引结束--")

        return {"data": instance.id}

    @classmethod
    def delete_repository_controller(cls, *args, **kwargs):
        """
        删除文章
        """
        self = kwargs["self"]
        request = kwargs["request"]
        instance = self.get_object()
        res = {"data": instance.id}

        RepositoryIndex().remove_object(instance=instance)
        logger.info("删除文章删除索引结束，开始删除数据库数据--")
        Repository.objects.filter(drafts=True, base_id=instance.id).delete()
        self.perform_destroy(instance)
        logger.info("删除数据库数据结束--")

        template_delete_images = RepositoryUtils.repository_delete_image(instance)

        RepositoryUtils.minio_delete_objects(delete_images=template_delete_images)

        OperationLog.objects.create(
            operator=request.user.username,
            operate_type=OperationLog.DELETE,
            operate_obj=instance.title,
            operate_summary="删除{}名称：[{}]".format("草稿，草稿" if instance.drafts else "文章，文章", instance.title),
            current_ip=request.current_ip,
            app_module="知识库",
            obj_type="知识文章",
        )

        return res

    @classmethod
    def add_repository_collect(cls, *args, **kwargs):
        """
        用户收藏文章
        """
        self = kwargs["self"]
        request = kwargs["request"]
        username = kwargs["username"]
        current_ip = getattr(request, "current_ip", "127.0.0.1")

        instance = self.get_object()
        if instance.collect_users.filter(bk_username=username).exists():
            return {"data": {"detail": "文章不能重复收藏！"}, "status": 500}

        user = RepositoryModels.get_user(username=username)
        RepositoryModels.add_many_to_many_field(instance=instance, add_attr="collect_users", add_data=user)

        OperationLog.objects.create(
            operator=request.user.username,
            operate_type=OperationLog.ADD,
            operate_obj=instance.title,
            operate_summary="文章收藏，文章名称：[{}]".format(instance.title),
            current_ip=current_ip,
            app_module="知识库",
            obj_type="知识文章",
        )

        return {"data": instance.id}

    @classmethod
    def cancel_repository_collect(cls, *args, **kwargs):
        """
        用户取消收藏文章
        """
        self = kwargs["self"]
        request = kwargs["request"]
        username = kwargs["username"]
        current_ip = getattr(request, "current_ip", "127.0.0.1")

        instance = self.get_object()
        if not instance.collect_users.filter(bk_username=username).exists():
            return {"data": {"detail": "取消失败，此文章您未收藏！"}, "status": 500}

        user = RepositoryModels.get_user(username=username)
        RepositoryModels.delete_many_to_many_field(instance=instance, delete_attr="collect_users", delete_data=user)

        OperationLog.objects.create(
            operator=request.user.username,
            operate_type=OperationLog.DELETE,
            operate_obj=instance.title,
            operate_summary="取消文章收藏，文章名称：[{}]".format(instance.title),
            current_ip=current_ip,
            app_module="知识库",
            obj_type="知识文章",
        )

        return {"data": instance.id}

    @classmethod
    def update_repository_is_it_service(cls, repository_id, judge, request):
        """修改文章是否属于IT服务台文章"""
        if judge == "true":
            is_it_service_value = True
        elif judge == "false":
            is_it_service_value = False
        else:
            raise ParamValidationError
        Repository.objects.filter(id=int(repository_id)).update(is_it_service=is_it_service_value)
        current_ip = getattr(request, "current_ip", "127.0.0.1")
        instance = Repository.objects.filter(id=int(repository_id)).first()
        operate_obj = instance.title if instance else repository_id
        OperationLog.objects.create(
            operator=request.user.username,
            operate_type=OperationLog.MODIFY,
            operate_obj=operate_obj,
            operate_summary="修改文章[{}]为{}服务台文章".format(operate_obj, "" if is_it_service_value else "非"),
            current_ip=current_ip,
            app_module="知识库",
            obj_type="知识文章",
        )

    @classmethod
    def upload_repositories_controller(cls, *args, **kwargs):
        request = kwargs["request"]
        files = request.FILES.getlist("files")
        labels = json.loads(request.data["labels"])
        current_ip = request.COOKIES.get("current_ip", "127.0.0.1")
        RepositoryUtils.create_file_logs(**{"request": request, "msg": "批量上传文件生成知识库文章"})

        if len(labels) > 5:
            raise ParamValidationError("标签设置数量超过上限！")

        success_files, error_files, instances = DocxChangeMarkdownUtils.main(
            files=files, labels=labels, username=request.user.username, model_manage=Repository
        )

        files_name = ",".join(i.name for i in files)
        OperationLog.objects.create(
            operator=request.user.username,
            operate_type=OperationLog.ADD,
            operate_obj=files_name,
            operate_summary="知识库批量上传文章：[{}]".format(files_name),
            current_ip=current_ip,
            app_module="知识库",
            obj_type="知识文章",
        )

        role_names = SysRole.get_user_roles(request.user.username)
        policies = []
        for role_name in role_names:
            for _instance in instances:
                policies.append([role_name, "知识库", "manage", str(_instance.id), "0"])
        result = CasBinInstService.create_policies(policies=policies, sec="p", ptype="p")
        logger.info("批量上传文章同步权限到casbin结果: {}".format(result))

        if not error_files:
            data = {"data": "上传成功！"}
        else:
            if len(error_files) == len(files):
                data = {"data": {"detail": "上传失败！ "}, "status": 500}
            else:
                data = {"data": {"detail": "部分上传成功，上传失败文章有:{}".format(",".join(error_files))}, "status": 500}

        return data

    @classmethod
    def get_files_url(cls, data):
        """
        从oss获取图片返回图片map
        """

        files = data.get("images", [])
        template = data.get("template", False)
        template = TEMPLATE_UPLOAD_TO if template else REPOSITORY_UPLOAD_TO
        images_dict = {}
        for file in files:
            file_key = file
            if template and file.startswith(TEMPLATE_UPLOAD_TO):
                file = file.split("/", 1)[-1]  # 兼容旧数据"template/aaa.jpg"
            object_name = RepositoryUtils.join_repository_path(file, template)
            images_dict[file_key] = RepositoryUtils.get_oss_images(object_name)

        return images_dict

    @classmethod
    def delete_files(cls, data, object_dir):
        object_dir = TEMPLATE_UPLOAD_TO if object_dir else REPOSITORY_UPLOAD_TO
        RepositoryUtils.minio_delete_objects(delete_images=data, object_dir=object_dir)

    @classmethod
    def upload_image(cls, request, image, file_name, dir_path):
        dir_path = TEMPLATE_UPLOAD_TO if dir_path else REPOSITORY_UPLOAD_TO  # 指定路径/文件夹
        RepositoryUtils.create_file_logs(**{"request": request, "msg": "知识库上传文件获取链接"})
        file_path = RepositoryUtils.oss_upload(image, file_name, dir_path)
        image_url = RepositoryUtils.get_oss_images(file_path)
        return image_url

    @classmethod
    def add_drafts_data(cls, instance_data):
        """
        判断是否创建的是草稿
        若是，补充此功能

        1. 不传base_id，创建文章，否则创建草稿
        2. 查询原文章是否存在，不存在抛出错误
        3. 删除原文章现有的草稿，写入新的草稿

        """
        title = instance_data["title"]
        repository_id = instance_data.get("base_id", 0)

        if repository_id > 0:
            repository = Repository.objects.filter(id=repository_id).first()
            if repository is None:
                template_id = instance_data.pop("template_id", RepositoryModels.get_blank_template())
            else:
                template_id = repository.template_id
        else:
            template_id = RepositoryModels.get_blank_template()

        if not title:
            instance_data["title"] = "未命名-{}".format(str(time.time()).replace(".", ""))

        instance_data["drafts"] = True
        instance_data["base_id"] = repository_id
        instance_data["template_id"] = template_id

        return instance_data


class RepositoryTemplateController(object):
    @classmethod
    def create_repository_template_controller(cls, *args, **kwargs):
        """
        创建模版
        """
        self = kwargs["self"]
        request = kwargs["request"]

        labels, instance_data = RepositoryUtils.get_create_repository_data(data=request.data)

        serializer = self.get_serializer(data=instance_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        if labels:
            labels_instances = RepositoryLabels.objects.filter(id__in=labels)
            RepositoryModels.add_many_to_many_field(
                instance=serializer.instance, add_attr="labels", add_data=labels_instances
            )

        OperationLog.objects.create(
            operator=request.user.username,
            operate_type=OperationLog.ADD,
            operate_obj=request.data["template_name"],
            operate_summary="新增模版，模版名称：[{}]".format(request.data["template_name"]),
            current_ip=request.current_ip,
            app_module="知识库",
            obj_type="文章模版",
        )

        return {"data": serializer.instance.id}

    @classmethod
    def update_repository_template_controller(cls, *args, **kwargs):
        """
        修改模版
        """
        self = kwargs["self"]
        request = kwargs["request"]
        instance = self.get_object()

        labels, instance_data = RepositoryUtils.get_create_repository_data(data=request.data)

        if instance.template_name == BLANK_TEMPLATE_NAME:
            return {"data": {"detail": "空白模版不允许修改! "}, "status": 500}

        instance_data["updated_by"] = request.user.username
        instance_data["body"] = json.dumps(instance_data["body"])

        RepositoryModels.model_update(data=instance_data, instance=instance)
        labels_instances = RepositoryLabels.objects.filter(id__in=labels)
        RepositoryModels.update_many_to_many_field(instance=instance, add_attr="labels", add_data=labels_instances)

        OperationLog.objects.create(
            operator=request.user.username,
            operate_type=OperationLog.MODIFY,
            operate_obj=instance.template_name,
            operate_summary="修改模版，模版名称：[{}]".format(request.data.get("template_name", instance.template_name)),
            current_ip=request.current_ip,
            app_module="知识库",
            obj_type="文章模版",
        )

        return {"data": instance.id}

    @classmethod
    def delete_repository_template_controller(cls, *args, **kwargs):
        """
        删除模版
        """
        self = kwargs["self"]
        request = kwargs["request"]
        instance = self.get_object()

        if instance.template_name == BLANK_TEMPLATE_NAME:
            return {"data": {"detail": "空白模版不允许删除! "}, "status": 500}
        if instance.repository_set.exists():
            return {"data": {"detail": "此模版已被使用，无法删除! "}, "status": 500}

        instance_id = instance.id
        template_img = instance.template_img

        with transaction.atomic():
            self.perform_destroy(instance)

            OperationLog.objects.create(
                operator=request.user.username,
                operate_type=OperationLog.DELETE,
                operate_obj=instance.template_name,
                operate_summary="删除模版，模版名称：[{}]".format(instance.template_name),
                current_ip=request.current_ip,
                app_module="知识库",
                obj_type="文章模版",
            )

        # 删除模版图片
        RepositoryUtils.minio_delete_objects(delete_images=[template_img], object_dir=TEMPLATE_UPLOAD_TO)

        # 从内容里拿出图片删除
        template_delete_images = RepositoryUtils.repository_delete_image(instance)

        # 删除知识库正文图片
        RepositoryUtils.minio_delete_objects(delete_images=template_delete_images)

        # logger.info("删除模版图片完成，delete_images_res={}".format(delete_images_res))

        return {"data": instance_id}

    @classmethod
    def retrieve_repository_template_controller(cls, *args, **kwargs):
        """
        获取单个模版
        """
        res = {}
        self = kwargs["self"]
        instance = self.get_object()
        res["id"] = instance.id
        res["title"] = instance.title
        res["images"] = instance.images
        res["template_name"] = instance.template_name
        res["template_img"] = instance.template_img or ""
        res["labels"] = [{"id": i.id, "label_name": i.label_name} for i in instance.labels.all()]
        res["body"] = json.loads(instance.body) if not isinstance(instance.body, list) else instance.body

        return res
