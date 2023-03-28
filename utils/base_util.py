# -*- coding: utf-8 -*-

# @File    : base_util.py
# @Date    : 2022-04-13
# @Author  : windyzhao
import json

from utils.app_log import api_logger


class BaseUtils(object):
    @classmethod
    def get_serializer(cls, *args, **kwargs):
        """
        分页实例化数据
        """
        self = kwargs["self"]
        instances = kwargs["instances"]
        model_serializer = kwargs.get("model_serializer")

        paginator = self.pagination_class()
        page_list = paginator.paginate_queryset(instances, self.request, view=self)
        if model_serializer:
            serializer = model_serializer(page_list, many=True, context={"request": self.request})
        else:
            serializer = self.get_serializer(page_list, many=True)
        response = paginator.get_paginated_response(serializer.data)

        return response

    @classmethod
    def create_file_logs(cls, *args, **kwargs):
        """
        from表单 包含文件的日志
        msg: str 接口说明
        file_key: 文件字段
        """
        msg = kwargs["msg"]
        request = kwargs["request"]
        drf = kwargs.get("drf", False)
        current_ip = request.COOKIES.get("current_ip", "127.0.0.1")
        file_names = request.FILES.keys()
        if drf:
            data = request.data
        else:
            data = request.POST
        params = {k: v for k, v in data.items() if k not in file_names}
        if file_names:
            for file_name in file_names:
                file_objects = request.FILES.getlist(file_name, [])
                params[file_name] = ",".join([i.name for i in file_objects])
        api_logger.info(
            f"[{current_ip}]使用帐号[{request.user.username}] 请求接口[{msg}]，"
            f"请求方法[{request.method}]，请求地址[{request.path}]，请求参数[{json.dumps(params)}]"
        )
