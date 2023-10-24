# # -- coding: utf-8 --
#
# # @File : inst_permissions.py
# # @Time : 2023/7/18 17:09
# # @Author : windyzhao
# import importlib
import inspect
import os
import sys
from abc import ABCMeta

from rest_framework import serializers

#
INST_PERMISSIONS_MODELS = {}  # 模型

import importlib

from apps.system_mgmt.constants import INSTANCE_MONITORS


class InstPermissionsUtils(object):
    global INST_PERMISSIONS_MODELS

    ACTIVATE_APP_MAPPING = {
        "repository": "知识库",
        "operational_tools": "运维工具",
        "dashboard": "仪表盘",
        "custom_topology": "拓扑图",
    }

    apps = {"apps": os.listdir("apps"), "apps_other": os.listdir("apps_other")}
    for app_group, app_list in apps.items():
        for app_name in app_list:
            if app_name in ["__pycache__", "system_mgmt", "__init__.py"]:
                continue
            app_path = f"{app_group}.{app_name}.inst_permission_conf"
            try:
                module = importlib.import_module(app_path)
            except ModuleNotFoundError:
                continue

            class_objects = [cls for name, cls in inspect.getmembers(module) if inspect.isclass(cls)]

            for cls in class_objects:
                if cls.__name__.endswith("InstPermissions"):
                    ACTIVATE_APP_MAPPING[app_name] = cls.id



    @classmethod
    def object(cls, name):
        if name not in INST_PERMISSIONS_MODELS:
            raise Exception("此模型不存在！name={}".format(name))
        return INST_PERMISSIONS_MODELS[name]

    @classmethod
    def model(cls, name):
        return cls.object(name).model

    @classmethod
    def serializer(cls, name):
        return cls.object(name).serializer

    @classmethod
    def fields(cls, name):
        fields_map = cls.object(name).fields
        return list(fields_map.keys())

    @classmethod
    def path(cls, name):
        return cls.object(name).path

    @classmethod
    def default_filter(cls, name):
        return getattr(cls.object(name), "default_filter", {})

    @classmethod
    def search_fields(cls, name):
        return INST_PERMISSIONS_MODELS[name].search

    @classmethod
    def instances(cls, name, params, request, _self):
        if name in INSTANCE_MONITORS:
            # 监控和告警的查询实例
            params["cookies"] = request.COOKIES
            _object = cls.object(name)
            result = _object().get_instances(_self, request.user.is_super, kwargs=params)
        else:
            result = cls._instances(name, params, _self)

        return result

    @classmethod
    def _instances(cls, name, params, _self):
        _object = cls.object(name)
        model = _object.model
        serializer = _object.serializer
        search_value = params.get("search", "")
        search_fields = cls.search_fields(name)
        search_params = {f"{search_fields}__icontains": search_value} if search_value else {}
        search_params.update(cls.default_filter(name))
        instances = model.objects.filter(**search_params).order_by("-id")
        paginator = _self.pagination_class()
        page_list = paginator.paginate_queryset(instances, _self.request, view=_self)
        serializer = serializer(page_list, many=True, context={"request": _self.request})
        response = paginator.get_paginated_response(serializer.data)
        return response

    @classmethod
    def _import_modules(cls, path):
        _path = path.replace(".", "/")
        module = importlib.import_module(_path)
        return module

    @classmethod
    def get_model_attrs(cls):
        init_inst_permissions_models()
        result = []

        for model in INST_PERMISSIONS_MODELS.values():
            result.append(
                {
                    "instance_type": model.id,
                    "fields": getattr(model, "fields", {}),
                    "permissions": getattr(model, "permissions", {}),
                    "show": getattr(model, "search", ""),
                    "unique_id": getattr(model, "unique_id", "id"),
                }
            )

        return result

    @classmethod
    def get_monitor_and_monitor_policy_attr(cls, name, bk_obj_id):
        _object = cls.object(name)()
        field_map = _object._fields()
        result = field_map.get(bk_obj_id, _object.default_fields())
        return result

def init_inst_permissions_models():
    apps = {"apps": os.listdir("apps"), "apps_other": os.listdir("apps_other")}
    for app_group, app_list in apps.items():
        for app_name in app_list:
            if app_name in ["__pycache__", "system_mgmt", "__init__.py"]:
                continue
            app_path = f"{app_group}.{app_name}.inst_permission_conf"
            try:
                module = importlib.import_module(app_path)
            except ModuleNotFoundError:
                continue

            class_objects = [cls for name, cls in inspect.getmembers(module) if inspect.isclass(cls)]

            for cls in class_objects:
                if cls.__name__.endswith("InstPermissions"):
                    INST_PERMISSIONS_MODELS[cls.id] = cls





# class newAppInstPermissionsFormat(BaseInstPermissionsFormat):
#
#     # 额外将新添加的app添加进激活app中
#     app_others = os.listdir("apps_other")
#     dir_list = [i for i in app_others if os.path.isdir(f"apps_other/{i}") and not i.startswith("__")]
#     for i in dir_list:
#         app_config = apps.get_app_config(i)
#         name = app_config.verbose_name  # 导入app的中文名
#         id = name
#         all_models = list(app_config.get_models())
#         model = all_models[0] if all_models else None
#         fields = {"name": "标题", "id": "", "created_User": "创建人", "created_Date": "创建时间"}  # 查询模型字段
#         serializers_module = app_config.module.serializers
#         serializer_list = [item for item in dir(serializers_module) if item.endswith('Serializer')]
#         for serializer_name in serializer_list:
#             serializer_module = getattr(serializers_module, serializer_name)
#             if model.__name__ in serializer_name:
#                 serializer = serializer_module
#                 break
#         search = "name"  # 搜索字段

# class MonitorPolicyPermissionsFormat(BaseInstPermissionsFormat):
#     id = "监控策略"
#
#     @classmethod
#     def default_fields(cls):
#         """
#         cmdb实例的
#         """
#         result = {"show": "name", "fields": {"name": "策略名称", "id": "", "created_at": "创建时间"}}
#         return result
#
#     @classmethod
#     def _fields(cls):
#         """log的"""
#         result = {
#             "show": "title",
#             "fields": {"title": "策略名称", "id": "", "created_at": "创建时间", "created_by": "创建人"},
#         }
#         return {"log": result}
#
#     @staticmethod
#     def get_log_instances(params):
#         search = params.pop("search", "")
#         filters = {"title__icontains": search} if search else {}
#         instances = AlarmStrategy.objects.filter(**filters).values(
#             "event_definition_id", "title", "created_by", "created_at"
#         )
#         for instance in instances:
#             instance["id"] = instance["event_definition_id"]
#             instance["created_at"] = instance["created_at"].strftime("%Y-%m-%d %H:%M:%S")
#
#         return instances
#
#     def get_instances(self, _self, is_super, kwargs):
#         result = {"count": 0, "items": []}
#         bk_obj_id = kwargs.pop("bk_obj_id")
#         if bk_obj_id == "log":
#             return self.get_log_instances(kwargs)
#         else:
#             kwargs.update(
#                 {
#                     "super": True,
#                     "username": "admin",
#                     "name": kwargs["search"],
#                     "monitor_object_type": bk_obj_id,
#                     "strategy_type": "1",
#                 }
#             )
#             res = ApiManager.monitor.get_strategy(**kwargs)
#             if res["result"]:
#                 result["count"] = res["data"]["count"]
#                 result["items"] = res["data"]["results"]
#
#         return result
