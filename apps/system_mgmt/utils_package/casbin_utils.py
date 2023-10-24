# -*- coding: utf-8 -*-

# @File    : casbin_utils.py
# @Date    : 2022-07-01
# @Author  : windyzhao
"""
casbin policy 的入库
角色存在变动时  把规则入库
"""
import copy
from distutils.version import LooseVersion
from functools import wraps

from casbin_adapter.models import CasbinRule
from django.db import transaction
from django.db.models import Q

from apps.system_mgmt.casbin_package.cabin_inst_rbac import INST_MODEL, INST_NAMESPACE
from apps.system_mgmt.casbin_package.policy_constants import (
    BASICMONITOR_OTHER,
    MENU_OPERATOR,
    MESH_MODEL,
    MESH_NAMESPACE,
    OPERATE_ENDSWITH,
    POLICY_VERSION,
    RESOURCE_OTHER,
    checkAuth,
    configFileManage,
    operateAuth,
)
from apps.system_mgmt.constants import (
    DB_MENU_IDS,
    DB_NOT_ACTIVATION_ROLE,
    DB_NOT_ACTIVATION_ROLE_DISPLAY_NAME,
    DB_OPERATE_IDS,
    DB_OPERATE_IDS_DISPLAY_NAME,
    DB_SUPER_USER,
    INIT_POLICY,
    MENUS_REMOVE_CLASSIFICATIONS,
    init_policy_data,
)
from apps.system_mgmt.models import SysApps, SysRole, SysSetting
from apps.system_mgmt.sys_setting import sys_setting
from apps.system_mgmt.utils_package.dao import RoleModels
from common.casbin_mesh_common import CasbinMeshApiServer
from common.casbin_register_policy import POLICY_DICT
from common.menu_service import Menus
from common.utils import split_list
from utils.app_log import logger


def decorator_except(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
        except Exception as e:
            logger.exception("函数【{}】执行报错, error={}".format(func.__name__, e))
            res = None

        return res

    return inner


class CasbinUtils(object):
    """
    1. 3.8之后，会把之前页码的权限转化为查询权限和操作权限
    2. 在后续迭代中，若存在菜单合并/新增/拆分 那么需要在
    部署时，重新初始化policy
    3. 每个版本的部署 都会把此版本新增的policy新增入库初始化到角色上
    """

    @staticmethod
    def merge(app_menus, app_key):
        """
        合并页面
        合并的页面中，只要有一个有操作权限
        那么合并后的这个页面，拥有全部权限
        如果都没有操作，那么就都只有查看权限
        """

        if app_key != DB_OPERATE_IDS:
            return

        merge_menus = MENU_OPERATOR.get("merge").get(POLICY_VERSION)
        if not merge_menus:
            return

        menu_operate = {i["menuId"]: i["operate_ids"] for i in app_menus}
        for new_menu, merge_menu in merge_menus:
            if menu_operate.get(new_menu):
                continue
            check_auth = any([[checkAuth] == menu_operate.get(i, []) for i in merge_menu])  # 存在查看权限
            operate_auth = any([[operateAuth] == menu_operate.get(i, []) for i in merge_menu])  # 存在操作权限
            add_menu_list = []

            if operate_auth:
                add_menu_list.append(operateAuth)
            elif not operate_auth and check_auth:
                add_menu_list.append(checkAuth)

            app_menus.append({"menuId": new_menu, "operate_ids": add_menu_list})

    @staticmethod
    def split(app_menus: list, app_key: str):
        """
        拆分分页 或者拆分操作
        1. 3.12 监控管理下的监控采集，监控策略 从查看权限拆分为操作权限和查询权限
        存在查询/操作权限，那么就拥有查询/操作权限，不存在查询/操作权限，什么都没有
        app_menus: [] or [{}, ]
        app_key: 类型key operate_ids or menu_ids
        """
        merge_menus_dict = MENU_OPERATOR.get("split")
        if not merge_menus_dict:
            return

        for version, menus in merge_menus_dict.items():
            if LooseVersion(POLICY_VERSION) < LooseVersion(version):
                continue

            for old_menu, split_menu in menus:
                for _split_menu in split_menu:
                    if app_key != DB_OPERATE_IDS:
                        if old_menu in app_menus:
                            app_menus.append(_split_menu)
                    else:
                        menu_operate = {i["menuId"]: i["operate_ids"] for i in app_menus}
                        old_menu_operate = menu_operate.get(old_menu, [])
                        if not old_menu_operate:
                            continue
                        else:
                            app_menus.append({"menuId": _split_menu, "operate_ids": old_menu_operate})

    @staticmethod
    def remove(*args, **kwargs):
        """
        删除每个版本去除的policy
        """
        remove_menus = MENU_OPERATOR.get("remove")
        if not remove_menus:
            return
        for menus_name in remove_menus:
            res = CasbinMeshApiServer.remove_filter_policies(
                namespace=MESH_NAMESPACE, sec="p", ptype="p", field_index=4, field_values=[menus_name]
            )
            logger.info("Init Removed Policy. res={}".format(res))

    @classmethod
    def menu_operator(cls):
        sys_apps = SysApps.objects.filter(
            Q(app_key__in=[DB_OPERATE_IDS, DB_MENU_IDS])
            & ~Q(sys_role__role_name__in=[DB_SUPER_USER, DB_NOT_ACTIVATION_ROLE])
        )
        for apps in sys_apps:
            app_key = apps.app_key
            app_menus = apps.app_ids
            for operator, values in MENU_OPERATOR.items():
                func = getattr(cls, operator, None)
                if func is None:
                    continue
                func(app_menus, app_key)
            apps.app_ids = app_menus

        sys_apps.bulk_update(sys_apps, fields=["app_ids"], batch_size=100)



    @classmethod
    @decorator_except
    def init_policy_v2(cls):
        """
        v3.16 重新根据页面权限 生成policy
        """
        casbin_rule = []
        CasbinRule.objects.all().delete()
        with transaction.atomic():
            sid = transaction.savepoint()
            try:
                init_policy, _create = SysSetting.objects.get_or_create(key=INIT_POLICY, defaults=init_policy_data)
                if not _create:
                    return
                pass_role = [DB_SUPER_USER, DB_NOT_ACTIVATION_ROLE]
                roles = SysRole.objects.filter(~Q(role_name__in=pass_role)).prefetch_related("sysuser_set")
                for role in roles:
                    # 获取operate_ids
                    role_apps = role.sysapps_set.filter(app_key=DB_OPERATE_IDS).first()
                    if role_apps is None:
                        continue

                    # 把用户和组的关系加入到policy
                    for user in role.sysuser_set.all():
                        casbin_rule.append(CasbinRule(ptype="g", v0=user.bk_username, v1=role.role_name))

                    cls.policy_controller(casbin_rule, role_apps.app_ids, role.role_name, add=True)

                cls.bulk_create_policy(casbin_rule)
            except Exception:
                import traceback

                logger.exception("init_policy_v2 初始化policy失败, err={}".format(traceback.format_exc()))
                transaction.savepoint_rollback(sid)
                transaction.savepoint_commit(sid)

    @classmethod
    @decorator_except
    def init_operate_ids(cls, *args, **kwargs):
        """
        根据v3.8的角色页面
        初始化出角色对应的操作权限
        """

        if LooseVersion(POLICY_VERSION) < LooseVersion("v3.9"):
            return

        classifications, monitors = cls.get_classification_monitor_list()

        roles = SysRole.activate_manage.exclude(role_name=DB_SUPER_USER)

        for role in roles:

            if role.role_name == DB_NOT_ACTIVATION_ROLE:
                menu_add_data = {
                    "sys_role_id": role.id,
                    "app_name": DB_NOT_ACTIVATION_ROLE_DISPLAY_NAME,
                    "app_key": DB_MENU_IDS,
                    "app_ids": ["CreditManage"],
                }
                RoleModels.set_role_resource(role_id=role.id, data=menu_add_data)
                continue

            if role.sysapps_set.filter(app_key=DB_OPERATE_IDS).exists():
                continue

            role_app = role.sysapps_set.filter(app_key=DB_MENU_IDS).first()
            if role_app is None:
                continue

            operate_ids = []

            for menu_id in role_app.app_ids:
                menu_id = cls.menus(menu_id, classifications, monitors)
                for menu in menu_id:

                    if menu in classifications:
                        # 资产
                        operate_ids_list = [configFileManage, "{}{}".format(menu, OPERATE_ENDSWITH)]

                    else:
                        if menu in monitors:
                            # 监控告警
                            operate_ids_value = POLICY_DICT.get(BASICMONITOR_OTHER, {})
                        else:
                            operate_ids_value = POLICY_DICT.get(menu, {})

                        operate_ids_list = [i for i in operate_ids_value.keys() if i != checkAuth]

                    operate_ids.append({"menuId": menu, "operate_ids": operate_ids_list})

            SysApps.objects.update_or_create(
                app_key=DB_OPERATE_IDS,
                sys_role_id=role_app.sys_role_id,
                defaults=dict(
                    sys_role_id=role_app.sys_role_id,
                    app_ids=operate_ids,
                    app_key=DB_OPERATE_IDS,
                    app_name=DB_OPERATE_IDS_DISPLAY_NAME,
                ),
            )
            logger.info("==初始化角色对应的操作权限==, 角色为{}".format(role.role_name))

    @classmethod
    def get_menus(cls):
        classification_list = (
            []
            if sys_setting.CLASSIFICATIONS_GROUP is None
            else [i for i in sys_setting.CLASSIFICATIONS_GROUP if i["bk_classification_id"] != "bk_host_manage"]
        )

        monitor = Menus.get_monitor_group_dict()
        classification = {
            i["bk_classification_id"]: i["bk_classification_name"]
            for i in classification_list
            if i["bk_classification_id"] not in MENUS_REMOVE_CLASSIFICATIONS
        }

        return {"classification": classification, "monitor": monitor}

    @classmethod
    def get_classification_monitor_list(cls):
        """
        获取最新的监控和应用的"其他"的模型分组
        """
        res = cls.get_menus()
        classification = list(res["classification"].keys())
        monitor = [f"BasicMonitor{i}" for i in res["monitor"].keys()]

        return classification, monitor

    @classmethod
    def menus(cls, menus, classifications, monitors):

        if menus == RESOURCE_OTHER:
            # 资源的
            menus = classifications
        elif menus == BASICMONITOR_OTHER:
            # 监控告警的
            menus = monitors
        else:
            menus = [menus]

        return menus

    @classmethod
    def bulk_create_policy(cls, casbin_rule):
        CasbinRule.objects.bulk_create(casbin_rule, batch_size=100)

    @classmethod
    def policy_controller(cls, casbin_rule, role_apps, role_name, add=False):
        """
        casbin_rule： list 存CasbinRule对象
        role_apps: 有权限的页面
        role: 角色
        add: 不做校验直接新增
        """
        classifications, monitors = cls.get_classification_monitor_list()
        casbin_rule_set = set(
            CasbinRule.objects.filter(ptype="p", v0=role_name).values_list("ptype", "v0", "v1", "v2", "v3", "v4", "v5")
        )

        for operate_id_dict in role_apps:
            menu_id = operate_id_dict["menuId"]  # 菜单
            operate_ids = operate_id_dict["operate_ids"]  # 菜单操作

            if menu_id in classifications:
                # 对于资产，动态变化的模型分组，名称为 "模型名称+Manage"
                policy_dict = POLICY_DICT.get(RESOURCE_OTHER, {})
                menu_id_manage = "{}{}".format(menu_id, OPERATE_ENDSWITH)
                if menu_id_manage in operate_ids:
                    operate_ids = [operateAuth] + [i for i in operate_ids if i != menu_id_manage]
            # elif menu_id.startswith(CLOUDMONITOR):
            #     policy_dict = POLICY_DICT.get(CLOUDMONITOR, {})
            elif menu_id in monitors:
                policy_dict = POLICY_DICT.get(BASICMONITOR_OTHER, {})
            else:
                policy_dict = POLICY_DICT.get(menu_id, {})

            policy = copy.deepcopy(policy_dict.get(checkAuth, set()))
            for operate_id in operate_ids:
                policy.update(policy_dict.get(operate_id, set()))

            for (path, method, operate, version) in policy:
                if add:
                    casbin_rule.append(
                        CasbinRule(ptype="p", v0=role_name, v1=path, v2=method, v3=operate, v4=menu_id, v5=version)
                    )
                else:
                    if ("p", role_name, path, method, operate, menu_id, version) not in casbin_rule_set:
                        casbin_rule.append(
                            CasbinRule(ptype="p", v0=role_name, v1=path, v2=method, v3=operate, v4=menu_id, v5=version)
                        )

    @classmethod
    def save_role_policy(cls, role, operate_ids, menu_ids, add=True):
        """
        用户设置角色 角色加入policy
        role: 角色
        operate_ids: 应用
        """
        operate_ids_menus = {i["menuId"] for i in operate_ids}
        add_operate_ids = set(menu_ids).difference(operate_ids_menus)

        for add_operate_id in add_operate_ids:
            operate_ids.append({"menuId": add_operate_id, "operate_ids": []})

        casbin_rule = []
        cls.policy_controller(
            casbin_rule=casbin_rule,
            role_apps=operate_ids,
            role_name=role.role_name,
            add=add,
        )
        cls.bulk_create_policy(casbin_rule)

        casbin_mesh_policies = [[role.role_name, i.v1, i.v2, i.v3, i.v4, i.v5] for i in casbin_rule]

        return casbin_mesh_policies

    @classmethod
    def set_user_role_policy(cls, user_name, role_names, delete_roles):
        """
        设置用户角色时，加入policy
        """

        casbin_rule = []

        CasbinRule.objects.filter(ptype="g", v0=user_name, v1__in=delete_roles).delete()

        for role_name in role_names:
            casbin_rule.append(CasbinRule(ptype="g", v0=user_name, v1=role_name))

        cls.bulk_create_policy(casbin_rule)

    @classmethod
    def set_role_user_policy(cls, role_name, add_user_names, delete_user_names):
        CasbinRule.objects.filter(ptype="g", v0__in=delete_user_names, v1=role_name).delete()
        add_casbin_rule = [CasbinRule(ptype="g", v1=role_name, v0=i) for i in add_user_names]
        CasbinRule.objects.bulk_create(add_casbin_rule)

    @classmethod
    def policy_operator(cls):
        """
        把casbin_rule表的数据迁移到casbin_mesh的数据格式转换
        """
        db_rules = CasbinRule.objects.all().values()
        policies = []
        group_policies = []
        for rule in db_rules:
            if rule["ptype"] == "g":
                group_policies.append([rule["v0"], rule["v1"]])
            else:
                policies.append([rule["v0"], rule["v1"], rule["v2"], rule["v3"], rule["v4"], rule["v5"]])

        return group_policies, policies

    @classmethod
    def casbin_set_model_namespace(cls, namespace, text):
        """
        1. 创建namespace
        2.创建models
        """
        namespace_res = CasbinMeshApiServer.create_namespace(namespace=namespace)
        if not namespace_res["success"]:
            if not isinstance(namespace_res["data"], dict):
                logger.exception("创建namespace失败！")
                return
            if namespace_res["data"].get("error") != "namespace already existed":
                logger.exception("创建namespace失败！未知的错误！data={}".format(namespace_res))
                return

        set_model_res = CasbinMeshApiServer.set_model(namespace=namespace, text=text)
        if not set_model_res["success"]:
            logger.exception("设置模型配置失败！data={}".format(set_model_res))
            return

        return True

    @classmethod
    @decorator_except
    def casbin_change_workflow(cls):
        """
        3.新增/删除policy
        """
        if not cls.casbin_set_model_namespace(namespace=MESH_NAMESPACE, text=MESH_MODEL):
            logger.exception("创建namespace和创建models失败！新增policy失败！")
            return False

        groups, policies_list = cls.policy_operator()
        policies_spilt = split_list(policies_list, count=500)
        groups_res = CasbinMeshApiServer.add_policies(namespace=MESH_NAMESPACE, sec="g", ptype="g", rules=groups)
        logger.info("新增group policy success={}".format(groups_res["success"]))

        for policies in policies_spilt:
            p_res = CasbinMeshApiServer.add_policies(namespace=MESH_NAMESPACE, sec="p", ptype="p", rules=policies)
            logger.info("新增policy success={}".format(p_res["success"]))

        return True


class CasBinInstUtils(object):
    @classmethod
    @decorator_except
    def casbin_inst_workflow(cls):
        """
        实例权限初始化到casbin_mesh
        """
        if not CasbinUtils.casbin_set_model_namespace(namespace=INST_NAMESPACE, text=INST_MODEL):
            logger.exception("创建namespace和创建models失败！新增policy失败！func={}".format("casbin_inst_workflow"))
            return False

        rules = cls.init_casbin_mesh_user()
        rules_spilt = split_list(rules, count=500)
        for rules in rules_spilt:
            groups_res = CasbinMeshApiServer.add_policies(namespace=INST_NAMESPACE, sec="g", ptype="g", rules=rules)
            logger.info("新增group policy success={}".format(groups_res["success"]))

        # for policies in policies_spilt:
        #     p_res = CasbinMeshApiServer.add_policies(namespace=MESH_NAMESPACE, sec="p", ptype="p", rules=policies)
        #     logger.info("新增policy success={}".format(p_res["success"]))

        return True

    @classmethod
    def policy_operator(cls):

        return 1, 2

    @classmethod
    def init_casbin_mesh_user(cls):
        policies = []
        roles = SysRole.activate_manage.exclude(role_name=DB_SUPER_USER)
        for role in roles:
            users = role.sysuser_set.all().values_list("bk_username", flat=True)
            for user in users:
                policies.append([user, role.role_name])

        return policies
