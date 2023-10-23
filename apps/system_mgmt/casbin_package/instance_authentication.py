from apps.system_mgmt.casbin_package.cabin_inst_rbac import INST_NAMESPACE
from apps.system_mgmt.constants import DB_SUPER_USER
from apps.system_mgmt.models import InstancesPermissions, SysRole
from blueapps.core.exceptions import RequestForbidden
from common.casbin_inst_service import CasBinInstService
from common.casbin_mesh_common import CasbinMeshApiServer


def is_super(username: str) -> bool:
    """判断用户是否为超管"""
    if username == "admin":
        return True
    return SysRole.objects.filter(role_name=DB_SUPER_USER, sysuser__bk_username=username).exists()


def check_inst(username: str, inst_id: str, inst_type: str, permission_type: str):
    """检查用户是否拥有实例权限"""
    if is_super(username):
        return
    policy = [username, inst_type, permission_type, str(inst_id)]
    if not CasbinMeshApiServer.enforce(namespace=INST_NAMESPACE, params=policy):
        raise RequestForbidden("无实例权限!")


def get_empower_inst(username: str, inst_type: str) -> set:
    """获取用户被授权的实例集合"""
    inst_set = set()
    query_dict = dict(
        instance_type=inst_type, permissions__contains={"view": True}, role__sysuser__bk_username=username
    )
    instances = InstancesPermissions.objects.filter(**query_dict).values("instances")
    for instance in instances:
        inst_set.update(set(instance["instances"]))
    return inst_set


# 实例列表权限过滤装饰器
def inst_filter(inst_type: str):
    def filter_(func):
        def wrapper(*args, **kwargs):
            query_set = func(*args, **kwargs)
            if not is_super(args[0]):
                empower_inst_set = get_empower_inst(args[0], inst_type)
                empower_inst_set.update(set(query_set.filter(created_by=args[0]).values_list("id", flat=True)))
                query_set = query_set.filter(id__in=empower_inst_set)
            return query_set

        return wrapper

    return filter_


# 添加角色实例权限
def add_policies(username, inst_id, inst_type, permission_type):
    role_names = SysRole.get_user_roles(username)
    policies = [[role_name, inst_type, permission_type, str(inst_id), "0"] for role_name in role_names]
    result = CasBinInstService.create_policies(policies=policies, sec="p", ptype="p")
    if not result:
        raise RequestForbidden("权限同步到casbin失败!")


# 移除角色实例权限
def remove_policies(username, inst_id, inst_type, permission_type):
    role_names = SysRole.get_user_roles(username)
    policies = [[role_name, inst_type, permission_type, str(inst_id), "0"] for role_name in role_names]
    result = CasBinInstService.remove_policies(policies=policies, sec="p", ptype="p")
    if not result:
        raise RequestForbidden("权限同步到casbin失败!")
