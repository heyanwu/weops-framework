# -- coding: utf-8 --

# @File : permissions.py
# @Time : 2023/7/20 13:53
# @Author : windyzhao
from apps.system_mgmt.casbin_package.permissions import BaseInstPermission


class RepositoryInstPermission(BaseInstPermission):
    """
    知识库修改
    """

    INSTANCE_TYPE = "知识库"
    INST_PERMISSION = "manage"

    def get_instance_id(self, request, view):
        if view.action == "drafts":
            return request.data["base_id"]
        return view.kwargs["pk"]
