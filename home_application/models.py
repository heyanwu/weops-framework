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

from django.db import models
from django_mysql.models import JSONField


class BaseModel(models.Model):
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    created_by = models.CharField("创建人", max_length=100, null=True)
    updated_at = models.DateTimeField("修改时间", auto_now=True)
    updated_by = models.CharField("修改人", max_length=100, null=True)

    class Meta:
        abstract = True


class ModuleCredDesign(models.Model):
    bk_obj_id = models.CharField(max_length=30, db_index=True, verbose_name="模型类型ID")
    credential_type = models.CharField(max_length=30, verbose_name="凭据类型")  # 网络设备有snmp，和ssh、telnet
    param_set = JSONField(default=list, verbose_name="凭据参数配置")

    class Meta:
        unique_together = ("bk_obj_id", "credential_type")


class VaultCredentials(BaseModel):
    name = models.CharField(max_length=64, db_index=True, verbose_name="凭据名称")
    module_cred_design = models.ForeignKey(ModuleCredDesign, on_delete=models.CASCADE)
    vault_path = models.CharField(max_length=100, verbose_name="vault路径")
    param_set = JSONField(default=list, verbose_name="凭据参数配置")
    bk_inst_id_list = JSONField(default=list, verbose_name="资源实例ID列表")
    user_list = JSONField(default=list, verbose_name="授权用户")
    role_list = JSONField(default=list, verbose_name="授权角色列表")

    class Meta:
        unique_together = ("name", "module_cred_design")
