# -*- coding: utf-8 -*-
"""自定义的一些错误类"""
from django.utils.translation import gettext_lazy as _

from blueapps.core.exceptions import ClientBlueException, ServerBlueException


class UploadFileError(ServerBlueException):
    """自定义上传文件错误类"""

    MESSAGE = _("上传文件错误")
    ERROR_CODE = "50000"
    STATUS_CODE = 500


class RequestParamsError(ClientBlueException):
    """自定义请求参数错误类"""

    MESSAGE = _("请求参数错误")
    ERROR_CODE = "40000"
    STATUS_CODE = 400


class OperateError(ClientBlueException):
    """自定义操作错误类"""

    MESSAGE = _("操作错误")
    ERROR_CODE = "40000"
    STATUS_CODE = 400


class GetDateError(ServerBlueException):
    """自定义调用接口获取数据错误"""

    MESSAGE = _("调用接口获取数据错误")
    ERROR_CODE = "50000"
    STATUS_CODE = 500


class FileError(ServerBlueException):
    """自定义文件错误类"""

    MESSAGE = _("操作文件错误")
    ERROR_CODE = "50000"
    STATUS_CODE = 500


class JurisdictionError(ClientBlueException):
    """权限错误"""

    MESSAGE = _("无操作权限")
    ERROR_CODE = "40300"
    STATUS_CODE = 403


class JobExeError(ServerBlueException):
    """自定义调用接口获取数据错误"""

    MESSAGE = _("作业执行失败")
    ERROR_CODE = "50000"
    STATUS_CODE = 500


class CustomApiException(Exception):
    def __init__(self, api_obj, msg, resp=None):
        if resp is not None:
            msg = f"""请求地址：{api_obj.total_url}
请求方式：{api_obj.method}
返回数据：{resp.text}
{msg}
"""
        self.error_message = msg
        super(CustomApiException, self).__init__(msg)


class BKException(Exception):
    def __init__(self, msg):
        self.message = msg


class NoneData(Exception):
    def __init__(self, msg):
        self.message = msg
