# -- coding: utf-8 --

# @File : urls.py
# @Time : 2022/9/19 11:35
# @Author : windyzhao

from django.conf.urls import url
from rest_framework.routers import SimpleRouter

from apps.activation import views

router = SimpleRouter()

urlpatterns = (
    url(r"^get_sys_info/$", views.get_sys_info),
    url(r"^get_applications/$", views.get_applications),
    url(r"^check_activation/$", views.check_activation),
    url(r"^check_node_nums/$", views.check_node_nums),
    url(r"set_expired_notify_day/$", views.set_expired_notify_day),
)

router.register(r"", views.ActivationModelViewSet, basename="activation")

urlpatterns += tuple(router.urls)
