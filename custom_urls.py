from django.conf.urls import include, url
from rest_framework.routers import SimpleRouter

from apps.system_mgmt.views import (
    InstancesPermissionsModelViewSet,
    MenuManageModelViewSet,
    OperationLogViewSet,
    RoleManageViewSet,
    SysSettingViewSet,
    SysUserViewSet,
    UserManageViewSet,
    login_info,
)

urlpatterns = [
    # 系统管理
    url(r"^system/mgmt/", include("apps.system_mgmt.urls")),
    url(r"^login_info/$", login_info),

]
# 添加视图集路由
router = SimpleRouter()

# 3.5版本用户管理

router.register(r"system/mgmt/user_manage", UserManageViewSet, basename="sys-user")

# 3.5版本角色管理
router.register(r"system/mgmt/role_manage", RoleManageViewSet, basename="sys-role")

router.register(r"system/mgmt/menu_manage", MenuManageModelViewSet, basename="sys-menu")

router.register(r"system/mgmt/inst_permissions", InstancesPermissionsModelViewSet, basename="sys-permissions")

# 系统用户操作
router.register(r"system/mgmt/sys_users", SysUserViewSet, basename="sys-user")
# 系统操作日志
router.register(r"system/mgmt/operation_log", OperationLogViewSet, basename="sys-log")
# 系统配置
router.register(r"system/mgmt/sys_setting", SysSettingViewSet, basename="sys-setting")

urlpatterns += router.urls
