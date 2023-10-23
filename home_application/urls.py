# -*- coding: utf-8 -*-


from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from home_application import views

urlpatterns = (
    url(r"^login_info/$", views.login_info),
)
# # 监控告警
routers = DefaultRouter(trailing_slash=True)
# routers.register(r"common", CommonViewSet, basename="common")
# routers.register(r"vault_credential", VaultCredentialsViewSet)
# routers.register(r"cred_design", ModuleCredDesignViewSet)

urlpatterns += tuple(routers.urls)
