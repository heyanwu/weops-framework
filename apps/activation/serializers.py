# -*- coding: utf-8 -*-

import datetime
import json

from rest_framework import serializers
from rest_framework.fields import empty

from apps.activation import models
from apps.activation.utils.constants import MENUS_DEFAULT, MENUS_MAPPING
from blueking.component.shortcuts import get_client_by_user


class ActivationSerializer(serializers.ModelSerializer):
    """Activation序列号器"""

    activation_info = serializers.SerializerMethodField(read_only=True)
    residue_agent_num = serializers.SerializerMethodField()
    applications = serializers.SerializerMethodField()

    class Meta:
        model = models.Activation
        fields = "__all__"

    def __init__(self, instance=None, data=empty, **kwargs):
        super(ActivationSerializer, self).__init__(instance, data, **kwargs)
        client = get_client_by_user("admin")

        params = {
            "bk_biz_ids": [],
            "conditions": [{"key": "status", "value": ["RUNNING", "TERMINATED"]}],
            "page": 1,
            "page_size": 1,
        }
        res = client.nodeman.get_agent_status_info(params)
        if not res["result"]:
            self.used_agent_num = 0
        else:
            self.used_agent_num = res["data"]["total"]

    @staticmethod
    def get_applications(obj):
        app_mapping = MENUS_MAPPING
        app_mapping.update(MENUS_DEFAULT)
        applications = obj.applications if isinstance(obj.applications, list) else json.loads(obj.applications)
        res = ",".join([app_mapping.get(i, "") for i in applications])
        return res

    def get_residue_agent_num(self, obj: models.Activation):
        return obj.agent_num - self.used_agent_num

    @staticmethod
    def get_activation_info(obj):
        activation_status = obj.activation_status
        now_date = datetime.datetime.strptime(str(datetime.datetime.now().date()), "%Y-%m-%d")
        expiration_date = datetime.datetime.strptime(obj.expiration_date, "%Y-%m-%d")
        valid_days = (expiration_date - now_date).days
        if valid_days < 0:
            valid_days = 0
            activation_status = "已到期"
        activation_info = {
            "valid_days": valid_days,
            "activation_status": activation_status,
        }
        return activation_info
