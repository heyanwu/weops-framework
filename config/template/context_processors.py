# -*- coding: utf-8 -*-

from django.conf import settings


def custom_settings(request):
    """
    :summary: 这里可以返回前端需要的公共变量
    :param request:
    :return:
    """
    context = {
        "CSRF_COOKIE_NAME": settings.CSRF_COOKIE_NAME,
    }
    return context
