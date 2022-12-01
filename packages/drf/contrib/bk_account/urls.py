# -*- coding: utf-8 -*-
"""
系统用户管理相关url
使用方法:
项目根目录urls中 添加
from packages.drf.contrib.bk_account.urls import router as bk_account_router

urlpatterns = [...]

urlpatterns += bk_account_router.urls

"""

from rest_framework import routers

from .views import GroupViewSet, UserViewSet

router = routers.SimpleRouter()
router.register(r"bk_account/users", UserViewSet)
router.register(r"bk_account/groups", GroupViewSet)
