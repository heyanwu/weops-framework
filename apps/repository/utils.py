# -*- coding: utf-8 -*-

# @File    : utils.py
# @Date    : 2022-04-08
# @Author  : windyzhao
import json
import os
import re
import uuid

import jieba_fast
from haystack.query import SearchQuerySet

from apps.repository.celery_task import async_delete_minio_images
from apps.repository.constants import BLANK_TEMPLATE_DATA, REPOSITORY_BUCKET_NAME, REPOSITORY_UPLOAD_TO
from apps.repository.models import RepositoryTemplate
from apps.repository.search_indexes import RepositoryIndex
from apps.repository.utils_package.minio_client import fake_minio_client, minio_client
from blueapps.core.exceptions import BlueException
from utils.app_log import logger
from utils.base_util import BaseUtils


class IndexesUtils(object):
    """
    全文检索工具类
    """

    @classmethod
    def get_search_query_set(cls, *args, **kwargs):
        return SearchQuerySet()

    @classmethod
    def get_indexes_data(cls, *args, **kwargs):
        """
        获取全文检索SearchQuerySet
        查询时，可传递如 "运维  大数据" 格式的查询词
        目前处理为 jieba 分词，and 类型查询
        python manage.py rebuild_index 生成索引
        """
        # TODO 优化搜索和权重比例
        search = kwargs["search"]
        id_list = kwargs["id_list"]
        index_queryset = cls.get_search_query_set()
        search_list = jieba_fast.cut_for_search(search)
        # search_list = [search]
        for search_name in search_list:
            if not search_name:
                continue
            index_queryset = index_queryset.filter_or(text=search_name)

        if id_list and index_queryset.count():
            index_queryset = index_queryset.filter(repository_id__in=id_list)

        return index_queryset.order_by("-repository_id")

    @classmethod
    def get_search_index_instance(cls, *args, **kwargs):
        """
        从索引中 查询到此对象
        """
        instance_id = kwargs["id"]
        instance = cls.get_search_query_set().filter(id=instance_id)
        return instance

    @classmethod
    def reindex(cls, *args, **kwargs):
        """
        删除全部索引并重新生成索引
        """
        RepositoryIndex().reindex()


class RepositoryUtils(BaseUtils):
    @classmethod
    def get_create_repository_data(cls, *args, **kwargs):
        """
        获取创建文章的参数
        """
        data = kwargs["data"]
        labels = data.get("labels", [])

        return labels, {k: v for k, v in data.items() if k != "labels"}

    @classmethod
    def get_user_repository_data(cls, *args, **kwargs):
        """
        获取查询用户收藏/用户自己的文章参数
        """
        request = kwargs["request"]
        search = request.GET.get("text")
        search_type = request.GET.get("search_type")

        return search, search_type

    @classmethod
    def init_repository_template(cls, *args, **kwargs):
        """
        初始化空白模版
        """
        RepositoryTemplate.objects.get_or_create(
            template_name=BLANK_TEMPLATE_DATA["template_name"], defaults=BLANK_TEMPLATE_DATA
        )

    @classmethod
    def add_repository_use_template_img(cls, instance_data):
        """
        找到使用模版的图片，集合到images_keys里
        并复制到oss
        """
        copy_images = []

        images_keys = instance_data.get("images", {})
        if not images_keys:
            return instance_data, copy_images

        template_obj = RepositoryTemplate.objects.get(id=instance_data["template_id"])
        template_image = (
            json.loads(template_obj.images) if isinstance(template_obj.images, str) else template_obj.images
        )

        if isinstance(template_image, list):
            template_image = {i: i for i in template_image}

        for image_key, image_name in images_keys.items():
            if image_key not in template_image:
                continue

            _, file_type = os.path.splitext(template_image[image_key])
            new_image_name = "{}{}".format(uuid.uuid4().hex, file_type)
            _, _new_image = RepositoryUtils.copy_images(
                old_file_name=template_image[image_key], file_name=new_image_name
            )  # 复制图片
            images_keys[image_key] = new_image_name
            copy_images.append(_new_image)

        instance_data["images"] = images_keys
        return instance_data, copy_images

    @classmethod
    def copy_repository_image(cls, instance_data):
        """
        把文章md里，使用了模版里的内容(图片)
        进行复制到新的文章里
        """
        copy_images = []  # 存放复制的图片

        for body_data in instance_data["body"]:
            if body_data["type"] != "markDown":
                continue

            content = body_data["content"]
            image_replace_mapping = cls.get_images_from_content(content)
            for old_image_name, uuid_image_name in image_replace_mapping.items():
                copy_result, _new_image = cls.copy_images(uuid_image_name, old_image_name)
                if not copy_result:
                    logger.warning("复制模版里的图片到新的文章出错, copy_image={}".format(old_image_name))
                else:
                    copy_images.append(_new_image)

            replace_content = cls.image_path_replace(content, image_replace_mapping)
            body_data["content"] = replace_content

        return copy_images

    @classmethod
    def template_delete_images(cls, instance, delete_images):
        """
        instance: 知识库模版
        查询所有使用到此模版的知识库的图片
        若模版图片被知识库使用，不删除，未使用 删除
        """
        if not delete_images:
            return set()

        repository_images = instance.repository_set.all().values_list("images", flat=True)

        use_images_set = set()
        for repository_image in repository_images:
            for image_value in repository_image.values():
                use_images_set.add(image_value)

        delete_images = delete_images if isinstance(delete_images, set) else set(delete_images)
        delete_set = delete_images.difference(use_images_set)
        return delete_set

    @classmethod
    def repository_delete_image(cls, instance):
        """
        拿图片组件里的图片
        从内容里扣出图片
        删除图片
        """
        image_set = set()

        body = json.loads(instance.body)
        content = ",".join(i["content"] for i in body if i["type"] == "markDown")  # 从文章里拿到是markdown的内容

        delete_images = json.loads(instance.images) if isinstance(instance.images, str) else instance.images

        if isinstance(delete_images, list):
            delete_images = {i: i for i in delete_images}

        image_set.update(set(delete_images.values()))

        img_re_compile, images_re_compile = cls.get_re_compiles()
        img_re_findall = re.findall(img_re_compile, content)
        images_re_findall = re.findall(images_re_compile, content)

        image_set.update(set(img_re_findall))
        image_set.update(set(images_re_findall))

        return image_set

    @classmethod
    def minio_repository_put_objects(cls, *args, **kwargs):
        """
        上传多个对象到minio
        images_dict dict: {images:[文件1.jpg,文件2.jpg], images_key:{key1:文件1.jpg, key2: 文件2.jpg}}
        images_key的value为 用户名称+文件内容 进行md5转换
        """
        error_keys = []  # 记录失败的上传记录
        images_dict = kwargs["images_dict"]
        images = images_dict["images"]

        for image in images:
            object_name = cls.join_repository_path(image.name)
            res = minio_client.put_object(
                bucket_name=REPOSITORY_BUCKET_NAME,
                object_name=object_name,
                data=image,
                length=image.size,
                content_type=image.content_type,
            )
            if not res:
                error_keys.append(image.name)

        return error_keys

    @classmethod
    def minio_delete_objects(cls, *args, **kwargs):
        """
        批量删除图片
        delete_images:list 可迭代对象
        """
        delete_images = kwargs["delete_images"]
        object_dir = kwargs.get("object_dir", REPOSITORY_UPLOAD_TO)
        bucket_name = kwargs.get("bucket_name", REPOSITORY_BUCKET_NAME)
        if not delete_images:
            return {"result": True, "delete_errors": "无删除图片"}

        objects_iter = [cls.join_repository_path(i, object_dir) for i in delete_images]
        async_delete_minio_images.delay(bucket_name, objects_iter)

    @classmethod
    def base_delete(cls, bucket_name, objects_iter):
        res = minio_client.remove_objects(bucket_name=bucket_name, objects_iter=objects_iter)
        logger.info("批量删除图片. bucket_name={},objects_iter={}, res={}".format(bucket_name, objects_iter, res))
        return res

    @classmethod
    def get_oss_images(cls, image):
        res = fake_minio_client.presigned_get_object(bucket_name=REPOSITORY_BUCKET_NAME, object_name=image)
        return res["data"]

    @classmethod
    def oss_upload(cls, image, file_name, object_dir):
        object_name = cls.join_repository_path(file_name, object_dir)
        res = minio_client.put_object(
            bucket_name=REPOSITORY_BUCKET_NAME,
            object_name=object_name,
            data=image,
            length=image.size,
            content_type=image.content_type,
        )

        if not res:
            raise BlueException("上传文件失败！请重试")

        return object_name

    @classmethod
    def join_repository_path(cls, file_name, object_dir=REPOSITORY_UPLOAD_TO):
        object_name = os.path.join(object_dir, file_name)
        return object_name

    @classmethod
    def get_stat_object(cls, object_name):
        dir_join_object_name = cls.join_repository_path(object_name)
        res = fake_minio_client.stat_object(bucket_name=REPOSITORY_BUCKET_NAME, object_name=dir_join_object_name)
        return res

    @classmethod
    def copy_images(cls, file_name, old_file_name):
        """
        复制图片
        """
        object_name = cls.join_repository_path(file_name)
        old_object_name = cls.join_repository_path(old_file_name)
        res = minio_client.copy_object(
            new_bucket=REPOSITORY_BUCKET_NAME,
            new_object=object_name,
            source_object=old_object_name,
            source_bucket=REPOSITORY_BUCKET_NAME,
        )
        return res, object_name

    @classmethod
    def get_images_from_content(cls, content):
        """
        从内容中，拿到图片名称
        返回新旧图片映射
        """
        image_replace_mapping = {}  # old:new

        img_re_compile, images_re_compile = cls.get_re_compiles()

        img_re_findall = re.findall(img_re_compile, content)
        images_re_findall = re.findall(images_re_compile, content)

        for re_result in [img_re_findall, images_re_findall]:
            for img in re_result:
                _, content_type = os.path.splitext(img)
                img_uuid_name = "{}{}".format(uuid.uuid4().hex, content_type)
                image_replace_mapping[img] = img_uuid_name

        return image_replace_mapping

    @classmethod
    def image_path_replace(cls, content, images_mapping):
        """
        把新的图片链接，返回到原本到图片位置
        """
        for old_img, new_img in images_mapping.items():
            content = content.replace(old_img, new_img)

        return content

    @classmethod
    def get_re_compiles(cls):
        img_re_compile = re.compile(r'<img src="(.*?)"\sstyle=.*')  # docx转md里图片的标签
        images_re_compile = re.compile(r"\!\[.*\]\((.*?)\).*")  # md里插入图片的标签
        return img_re_compile, images_re_compile
