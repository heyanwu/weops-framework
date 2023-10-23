# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

# Create your tests here.

# import os

# from django.test import TestCase
from unittest import TestCase

# from django.core.files import File
from common.minio_utils import MinIoClient


class TextMinIo(TestCase):
    """
    minio 服务类 测试
    """

    def setUp(self) -> None:
        self.minio_cli = MinIoClient()
        self.bucket_name = "test-bucket-01"
        self.file_path = "static/img/logo.png"
        self.object_name = "logo.png"
        self.file_path2 = "static/img/python3-vue.png"
        self.object_name2 = "python3-vue.png"

    def tearDown(self):
        pass

    def test_01make_bucket(self):
        """
        创建桶
        :return:
        """
        res = self.minio_cli.make_bucket(bucket_name=self.bucket_name)
        self.assertTrue(res)

    def test_02bucket_exists(self):
        """
        检查桶是否存在
        :return:
        """
        res = self.minio_cli.bucket_exists(bucket_name=self.bucket_name)
        self.assertTrue(res)

    def test_03put_object(self):
        """
        向桶里上传一个对象文件
        :return:
        """
        pass
        # with open(self.file_path, "rb") as f:
        #     my_file = File(f)
        #     content_type = self.minio_cli.get_file_content_type(file_path=self.file_path)
        #     res = self.minio_cli.put_object(
        #         bucket_name=self.bucket_name,
        #         object_name=os.path.split(self.file_path)[-1],
        #         length=my_file.size,
        #         data=f,
        #         content_type=content_type,
        #     )
        #     self.assertTrue(res)

    def test_04fput_object(self):
        """
        通过文件路径上传到对象中
        :return:
        """
        res = self.minio_cli.fput_object(
            bucket_name=self.bucket_name, object_name=self.object_name2, file_path=self.file_path2
        )
        self.assertTrue(res)

    def test_05list_buckets(self):
        """
        列出所有的存储桶
        :return:
        """
        res = self.minio_cli.list_buckets()
        self.assertTrue(res["result"])

    def test_06list_objects(self):
        """
        列出桶里的全部对象
        :return:
        """
        res = self.minio_cli.list_objects(bucket_name=self.bucket_name, recursive=True)
        self.assertTrue(res["result"])

    def test_07presigned_get_object(self):
        """
        生成一个用于HTTP GET操作
        :return:
        """
        res = self.minio_cli.presigned_get_object(bucket_name=self.bucket_name, object_name="虎年大吉2.jpeg")
        # print(res)
        self.assertTrue(res["result"])

    def test_08get_object(self):
        """
        下载对象到本地
        :return:
        """
        res = self.minio_cli.get_object(bucket_name=self.bucket_name, object_name=self.object_name)
        self.assertTrue(res)

    def test_09remove_object(self):
        """
        移除一个对象
        :return:
        """
        res = self.minio_cli.remove_object(bucket_name=self.bucket_name, object_name=self.object_name2)
        self.assertTrue(res)

    def test_10remove_objects(self):
        """
        移除多个对象
        :return:
        """
        res = self.minio_cli.remove_objects(bucket_name=self.bucket_name, objects_iter=[self.object_name])
        self.assertTrue(res["result"])

    def test_11remove_bucket(self):
        res = self.minio_cli.remove_bucket(bucket_name=self.bucket_name)
        self.assertTrue(res)

    def test_12copy_object(self):
        """
        测试对象复制
        """
        res = self.minio_cli.copy_object(
            new_bucket="weops-repository-private",
            new_object="repository/ttttttttttt11111.png",
            source_bucket="weops-repository-private",
            source_object="repository/socket_84db7fd9581e4884add843bd7e7e3c21.png",
        )

        self.assertTrue(res)
