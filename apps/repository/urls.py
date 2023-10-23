# -*- coding: utf-8 -*-

# @File    : urls.py
# @Date    : 2022-04-02
# @Author  : windyzhao

from rest_framework.routers import SimpleRouter

from apps.repository.views import RepositoryLabelsModelViewSet, RepositoryModelViewSet, RepositoryTemplateModelViewSet

urlpatterns = ()

router = SimpleRouter()

# 知识库
router.register(r"labels", RepositoryLabelsModelViewSet, basename="repository_labels")
router.register(r"templates", RepositoryTemplateModelViewSet, basename="repository_templates")
router.register(r"", RepositoryModelViewSet, basename="repository")

urlpatterns += tuple(router.urls)
