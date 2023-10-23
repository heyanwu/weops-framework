# -*- coding: utf-8 -*-

from collections import namedtuple


def tuple_choices(tupl):
    """从django-model的choices转换到namedtuple"""
    return [(t, t) for t in tupl]


def dict_to_namedtuple(dic):
    """从dict转换成namedtuple"""
    return namedtuple("AttrStore", dic.keys())(**dic)


def choices_to_namedtuple(choices):
    """从django-model的choices转换到namedtuple"""
    return dict_to_namedtuple(dict(choices))


CODE_STATUS_TUPLE = (
    "OK",
    "UNAUTHORIZED",
    "VALIDATE_ERROR",
    "METHOD_NOT_ALLOWED",
    "PERMISSION_DENIED",
    "SERVER_500_ERROR",
    "OBJECT_NOT_EXIST",
)
CODE_STATUS_CHOICES = tuple_choices(CODE_STATUS_TUPLE)
ResponseCodeStatus = choices_to_namedtuple(CODE_STATUS_CHOICES)

MENUS_DEFAULT = {
    # "index": "首页",
    "resource": "资产清单",
    "big_screen": "数据大屏",
}


MENUS_MAPPING = {
    "repository": "知识库",
}
