# -*- coding: utf-8 -*-
from rest_framework import serializers


class ManyToManyRelatedField(serializers.RelatedField):
    """自定义m2m关系字段, 用作既返回id, 也返回name"""

    def __init__(self, **kwargs):
        self.pk_field = kwargs.pop("pk_field", None)
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        if self.pk_field is not None:
            data = self.pk_field.to_internal_value(data)
        return self.get_queryset().get(pk=data)

    def to_representation(self, value):
        return {"id": value.pk, "name": str(value)}
