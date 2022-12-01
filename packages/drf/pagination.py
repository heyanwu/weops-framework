# -*- coding: utf-8 -*-
"""
自定义drf pagination 综合页码和url
使用方法:
config/default  REST_FRAMEWORK 中添加 如下配置

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "packages.drf.pagination.CustomPageNumberPagination",
}

"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):

    page_size_query_param = "page_size"
    max_page_size = 10000

    def get_paginated_response(self, data):
        return Response(
            dict(
                [
                    ("page", self.page.number),
                    ("total_page", self.page.paginator.num_pages),
                    ("count", self.page.paginator.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("items", data),
                ]
            )
        )
