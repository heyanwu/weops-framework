import json
from json import JSONDecodeError

from django.db.models import Q
from django_filters import CharFilter, DateTimeFromToRangeFilter, FilterSet, NumberFilter

from apps.system_mgmt.models import InstancesPermissions, MenuManage, OperationLog, SysRole, SysUser


class SysUserFilter(FilterSet):
    """用户过滤器"""

    search = CharFilter(method="filter_search", label="全局模糊搜索")
    role = NumberFilter(field_name="role", label="角色")
    biz_ids = CharFilter(method="filter_biz_ids", label="应用权限")

    class Meta:
        models = SysUser
        fields = ["search", "role", "biz_ids"]

    @staticmethod
    def filter_search(qs, field_name, value):
        """全局模糊过滤查询"""
        return qs.filter(
            Q(bk_username__icontains=value)
            | Q(chname__icontains=value)
            | Q(email__icontains=value)
            | Q(phone__icontains=value)
        )

    @staticmethod
    def filter_biz_ids(qs, field_name, value):
        """根据业务权限过滤查询"""
        try:
            value = json.loads(value)
        except JSONDecodeError:
            return qs
        return qs.filter(biz_ids__contains=value)


class NewSysUserFilter(FilterSet):
    """用户过滤"""

    search = CharFilter(method="filter_search", label="全局模糊搜索")
    roles = CharFilter(method="filter_roles", label="角色")

    class Meta:
        models = SysUser
        fields = ["search", "roles"]

    @staticmethod
    def filter_search(qs, field_name, value):
        """全局模糊过滤查询"""
        return qs.filter(
            Q(bk_username__icontains=value)
            | Q(chname__icontains=value)
            | Q(email__icontains=value)
            | Q(phone__icontains=value)
        )

    @staticmethod
    def filter_roles(qs, field_name, value):
        """根据业务权限过滤查询"""
        try:
            value = json.loads(value)
        except JSONDecodeError:
            return qs
        if value:
            return qs.filter(roles__in=value).distinct()
        return qs


class SysRoleFilter(FilterSet):
    """用户过滤器"""

    search = CharFilter(method="filter_search", label="全局模糊搜索")

    class Meta:
        models = SysRole
        fields = ["search"]

    @staticmethod
    def filter_search(qs, field_name, value):
        """全局模糊过滤查询"""
        return qs.filter(role_name__icontains=value)


class OperationLogFilter(FilterSet):
    operator = CharFilter(field_name="operator", lookup_expr="icontains", label="操作者")
    operate_type = CharFilter(field_name="operate_type", lookup_expr="exact", label="操作行为")
    create_time = DateTimeFromToRangeFilter(field_name="created_at", lookup_expr="range", label="创建时间区间")

    class Meta:
        models = OperationLog
        fields = ["operator", "operate_type", "create_time"]


class MenuManageFilter(FilterSet):
    """菜单过滤器"""

    search = CharFilter(field_name="menu_name", lookup_expr="icontains", label="菜单名称")

    class Meta:
        models = MenuManage
        fields = ["search"]


class InstancesPermissionsFilter(FilterSet):
    role = NumberFilter(field_name="role", label="角色")

    # search = CharFilter(field_name="menu_name", lookup_expr="icontains", label="菜单名称")

    class Meta:
        models = InstancesPermissions
        fields = ["role"]
