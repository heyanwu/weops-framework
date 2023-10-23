# -- coding: utf-8 --
# @Time : 2022/7/25 16:35
# @Author : windyzhao
# @File : pandoc_utils.py
"""
pandoc的工具类
"""
import copy
import json
import os
import re
import time
import uuid

from apps.repository.constants import (
    BASE_PATH,
    EXEC_LINE,
    FILE_TYPE,
    REPOSITORY_BUCKET_NAME,
    REPOSITORY_UPLOAD_TO,
    SAVE_IMAGE_DIR,
    TEMPLATE_BODY,
    TXT_TYPE,
)
from apps.repository.dao import RepositoryModels
from apps.repository.models import RepositoryLabels
from apps.repository.search_indexes import RepositoryIndex
from apps.repository.utils_package.minio_client import minio_client
# from home_application.decorators import decorator_except
from utils.app_log import logger


class DocxChangeMarkdownUtils(object):
    """
    批量文件上传到知识库，入库成为知识库文章
    1.上传多个文件到后端，类型有txt和word
    2.txt文件直接读取内容，入库即可
    3.若是word，先存到服务器，再使用pandoc转为markdown，存到服务器
    4.读取markdown，正则拿到图片位置，把图片上传到oss，得到路径，替换到markdown中
    5.markdown内容入库成为知识库文章，删除docx文件，markdown文件
    6.统计上传成功/失败的文章，返回给前端做提示
    """

    @classmethod
    def main(cls, files, labels, username, model_manage):

        error_files = set()
        success_files = set()
        instances = []

        for file in files:
            old_file_name, _ = os.path.splitext(file.name)
            file_name, file_type = cls.file_name_replace(file)
            if file_type == TXT_TYPE:
                # txt文件
                content = file.read()
                md_content = content.decode("utf-8")
            else:
                # word
                docx_path = cls.save_docx_file_to_service(file)
                logger.info("==DocxChangeMarkdown==, docx_path={}".format(docx_path))

                if docx_path is None:
                    logger.error("文章【{}】导入失败".format(file.name))
                    error_files.add(file.name)
                    continue

                change_result = cls.docx_change_md(docx_path)
                if change_result is None:
                    logger.error("文章【{}】转为markdown失败".format(file.name))
                    error_files.add(file.name)
                    cls.delete_file(docx_path)
                    continue

                image_path, md_path = change_result
                logger.info("==DocxChangeMarkdown==, image_path={}, md_path={}".format(image_path, md_path))

                images, md_content = cls.read_markdown(md_path)  # 读取markdown

                if not md_content:
                    error_files.add(file.name)
                    logger.error("文章【{}】转为markdown失败或者内容为空".format(file.name))
                    cls.delete_file(docx_path)  # 删除docx
                    cls.delete_file(md_path)  # 删除md
                    continue

                logger.info("==DocxChangeMarkdown==, images={}".format(images))
                md_content = cls.replace_images(images, md_content)  # 替换图片路径

                cls.delete_file(docx_path)  # 删除docx
                cls.delete_file(md_path)  # 删除md

            create_data = cls.repository_create_data(md_content, old_file_name, username)
            instance = cls.repository_save(model_manage, create_data, labels)
            instances.append(instance)
            success_files.add(file.name)

        return success_files, error_files, instances

    @classmethod
    def file_name_replace(cls, file):
        """
        去除文件名称存在空格或者中文符号
        导致的命令执行失败问题
        """
        file_name, file_type = os.path.splitext(file.name)

        res = uuid.uuid4().hex + str(time.time()).replace(".", "")
        file.name = "{}{}".format(res, file_type)

        return res, file_type

    @classmethod
    def repository_save(cls, model_manage, create_data, labels):
        """
        数据入库
        """
        instance = RepositoryModels.model_create(model_objects=model_manage, data=create_data)
        if labels:
            labels_instances = RepositoryLabels.objects.filter(id__in=labels)
            RepositoryModels.add_many_to_many_field(instance=instance, add_attr="labels", add_data=labels_instances)

        RepositoryIndex().update_object(instance=instance)

        return instance

    @classmethod
    def repository_create_data(cls, content, file_name, username):
        """
        入库数据组装
        """
        body = copy.deepcopy(TEMPLATE_BODY)
        re_content = cls.repository_content_img_replace(content)
        body["id"] = uuid.uuid4().hex
        body["content"] = content
        res = {
            "title": file_name,
            "content": re_content,
            "template_id": RepositoryModels.get_blank_template(),
            "body": json.dumps([body]),
            "created_by": username,
        }

        return res

    # @classmethod
    # @decorator_except
    # def delete_file(cls, path):
    #     """
    #     删除文件
    #     """
    #     if os.path.exists(path) and os.path.isfile(path):
    #         os.remove(path)

    # @classmethod
    # @decorator_except
    # def save_docx_file_to_service(cls, file):
    #     """
    #     多文件存储到服务器
    #     """
    #     docx_path = os.path.join(BASE_PATH, file.name)
    #     with open(docx_path, "wb") as w:
    #         for chunk in file.chunks(chunk_size=1024):
    #             w.write(chunk)
    #         logger.info("知识库上传文章，文件写入到服务器完成，路径为:{}".format(docx_path))
    #
    #     return docx_path

    # @classmethod
    # @decorator_except
    # def docx_change_md(cls, docx_path):
    #     """
    #     docx转为md。 md路径和名称都与docx一致
    #     return
    #     image_path: 图片路径
    #     save_path: md文件路径
    #     file_path: docx文件路径
    #     """
    #     if not os.path.exists(docx_path):
    #         logger.warning("此文件[{}]不存在！".format(docx_path))
    #         return
    #
    #     dir_path, file_name = os.path.split(docx_path)
    #     docx_name, file_type = os.path.splitext(file_name)
    #
    #     if file_type not in FILE_TYPE:
    #         logger.exception("此文件格式[{}]不符合要求！请上传以下类型的文件！{}".format(file_type, FILE_TYPE))
    #         return
    #
    #     if not os.path.exists(SAVE_IMAGE_DIR):
    #         os.mkdir(SAVE_IMAGE_DIR)
    #
    #     md_path = os.path.join(dir_path, "{}.md".format(docx_name))
    #     exec_line = EXEC_LINE.format(SAVE_IMAGE_DIR, md_path, docx_path)
    #     logger.info("==DocxChangeMarkdown==, exec_line={}".format(exec_line))
    #     os.system(exec_line)  # 执行命令
    #
    #     image_path = os.path.join(SAVE_IMAGE_DIR, "media")  # 图片生成的位置
    #
    #     return image_path, md_path

    @classmethod
    def read_markdown(cls, markdown_path):
        """
        读取markdown，替换里边的图片
        """
        if not os.path.exists(markdown_path):
            logger.warning("找不到生成的markdown文件！请检查pandoc是否正常！")
            return [], ""

        with open(markdown_path, "r") as r:
            md_content = r.read()

        images = re.findall(cls.re_search_images(), md_content)
        return images, md_content

    @classmethod
    def replace_images(cls, images, md_content):
        """
        替换图片 图片字段images存dict, key为uuid唯一标识，values
        """

        for image in images:
            if not os.path.exists(image):
                logger.info("==DocxChangeMarkdown==, 图片查询不存在！image={}".format(image))
                continue
            upload_image_path = cls.images_upload_oss(image)
            md_content = md_content.replace(image, upload_image_path)
            cls.delete_file(image)

        return md_content

    @classmethod
    def images_upload_oss(cls, image):
        """
        图片上传到minio
        """
        _, file_name = os.path.split(image)
        file_name = "{}{}".format(uuid.uuid4().hex, file_name)
        res = minio_client.fput_object(
            bucket_name=REPOSITORY_BUCKET_NAME,
            object_name="{}/{}".format(REPOSITORY_UPLOAD_TO, file_name),
            file_path=image,
        )
        return file_name if res else res

    @classmethod
    def repository_content_img_replace(cls, content):
        """
        把内容里的图片标签都替换为空
        做为全文检索都搜索内容
        """
        # re_compile = re.compile(r"<img .*[\s\>]*style=.* \/>")
        re_compile = re.compile(r"<img src=.*?\/>")
        re_content = re.sub(re_compile, "", content)
        return re_content

    @classmethod
    def re_search_images(cls):
        # reg = re.compile(r'<img src="(.*?)"[\s\>]*style=.*')
        reg = re.compile(r'<img src="(.*?)"')
        return reg
