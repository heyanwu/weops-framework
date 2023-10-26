# -*- coding: utf-8 -*-

# @File    : pages.py
# @Date    : 2022-02-14
# @Author  : windyzhao
from packages.drf.pagination import CustomPageNumberPagination


class LargePageNumberPagination(CustomPageNumberPagination):
    page_size_query_param = "page_size"
    max_page_size = 1000000
