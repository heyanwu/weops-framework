# -*- coding: utf-8 -*-

from django.contrib.auth.models import Group
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from blueapps.account.models import User, UserProperty
from blueapps.core.exceptions import ApiResultError
from blueking.component.shortcuts import get_client_by_user

from .serializers import GroupSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """系统用户管理"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    search_fields = ["username", "properties__value"]
    ordering_fields = ["date_joined", "username"]
    ordering = ["-date_joined"]

    @action(methods=["get"], detail=False)
    def get_all_bk_users(self, request=None):
        """获取蓝鲸所有的用户"""
        client = get_client_by_user(request.user.username)
        result_dict = client.bk_login.get_all_users()
        if not result_dict["result"]:
            raise ApiResultError("获取蓝鲸用户出错: %s" % result_dict.get("message", ""))

        user_list = result_dict["data"]
        # 去掉已加入到系统中的用户
        bk_username_user_dict = {i["bk_username"]: i for i in user_list}
        system_bk_username_list = User.objects.filter(username__in=bk_username_user_dict.keys()).values_list(
            "username", flat=True
        )

        return_list = [
            bk_username_user_dict[username]
            for username in set(bk_username_user_dict.keys()) - set(system_bk_username_list)
        ]

        return Response(return_list, status=status.HTTP_200_OK)

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        """批量添加用户"""
        params = request.data
        user_list = params.get("user_list", [])
        group_id_list = params.get("group_id_list", [])

        username_userinfo_mapping = {i["bk_username"]: i for i in user_list}
        User.objects.bulk_create([User(username=i) for i in username_userinfo_mapping.keys()])
        username_userinstance_mapping = {
            u.username: u for u in User.objects.filter(username__in=username_userinfo_mapping.keys())
        }

        user_property_create_list = []
        for username, userinstance in username_userinstance_mapping.items():

            # 添加用户&用户组关系
            if group_id_list:
                userinstance.groups.add(*group_id_list)

            # 添加用户property
            userinfo = username_userinfo_mapping.get(username, {})
            userinfo.pop("bk_username", None)
            userinfo.pop("username", None)
            if not userinfo:
                continue
            for property_key, property_value in userinfo.items():
                user_property_create_list.append(
                    UserProperty(user_id=userinstance.id, key=property_key, value=property_value)
                )

        UserProperty.objects.bulk_create(user_property_create_list)

        return Response(status=status.HTTP_201_CREATED)


class GroupViewSet(viewsets.ModelViewSet):
    """系统用户组管理"""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    search_fields = ["name"]
    ordering_fields = ["name"]
    ordering = ["name"]
