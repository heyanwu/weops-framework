# 系统默认Logo路径
import base64
import copy
import os

from django.conf import settings

from common.menu_service import Menus
from constants.apps_constants import CLASSIFICATIONS_GROUP, MONITOR_GROUP
from utils.common_models import VtypeMixin

DEFAULT_LOGO_PATH = os.path.join(settings.BASE_DIR, "static/img/default-logo.png")
# 系统设置表中提前置入的设置项
with open(DEFAULT_LOGO_PATH, "rb") as logo_file:
    SYSTEM_LOGO_INFO = {
        "key": "system_logo",
        "value": base64.b64encode(logo_file.read()).decode("utf8"),
        "vtype": VtypeMixin.STRING,
        "desc": "系统默认Logo",
    }

# 默认的应用显示字段
RES_BIZ_SHOW_FIELDS = "RES_BIZ_SHOW_FIELDS"
RES_HOST_SHOW_FIELDS = "RES_HOST_SHOW_FIELDS"

RES_HOST_RELATION_SHOW_FIELDS = "RES_HOST_RELATION_SHOW_FIELDS"

RES_HOST_OTHER_FIELDS = "RES_HOST_OTHER_FIELDS"
ACTION_MAPPING_FIELDS = "ACTION_MAPPING_FIELDS"

# 默认的其他模型显示字段前缀
RES_OTHER_OBJ_SHOW_FIELDS_PREFIX = "RES_OTHER_OBJ_SHOW_FIELDS_"
DEFAULT_RES_OTHER_OBJ_SHOW_FIELDS = ["bk_inst_name"]

# 默认的其他模型显示字段前缀（关联关系）
RES_OTHER_OBJ_RELATION_SHOW_FIELDS_PREFIX = "RES_OTHER_OBJ_RELATION_SHOW_FIELDS_"
DEFAULT_RES_OTHER_RELATION_OBJ_SHOW_FIELDS = ["bk_inst_name", "bk_module_name", "bk_set_name"]

IS_FIRST_MIGRATE = "IS_FIRST_MIGRATE"

# casbin 初始化一个时间进行为最新的加载policy的时间
CASBIN_TIME = "casbin_time"
# CASBIN_POLICY_LOAD_TIME = datetime.datetime.strptime("1970-01-01 08:00:00", "%Y-%m-%d %H:%M:%S")
CASBIN_POLICY_LOAD_TIME = "1970-01-01 08:00:00"

# 用户自定义应用ID列表
CUSTOM_BIZ_IDS = "CUSTOM_BIZ_IDS"
# 用户自定义菜单ID列表
CUSTOM_MENU_IDS = "CUSTOM_MENU_IDS"
MENU_MAPPING = [
    ("ticket", "工单管理"),
    ("km", "知识库"),
    ("application_monitor", "应用监控"),
    ("resource_monitor", "资源监控"),
    ("application_list", "应用列表"),
    ("resource_list", "资源列表"),
    ("application_health", "应用健康"),
    ("resource_health", "资源健康"),
    ("big_screen", "数据大屏"),
]
DEFAULT_MENU_IDS = "DEFAULT_MENU_IDS"
SYSTEM_SETTINGS_INIT_LIST = [
    SYSTEM_LOGO_INFO,
    {"key": RES_BIZ_SHOW_FIELDS, "value": ["bk_biz_name"], "vtype": VtypeMixin.JSON, "desc": "默认的应用显示字段"},
    {
        "key": RES_HOST_SHOW_FIELDS,
        "value": [
            "bk_host_innerip",
            "belong_app",
            "belong_set",
            "belong_module",
            "agent_status",
            "db_inst",
            "middleware_inst",
            "ad_server",
            "exchange_server",
        ],
        "vtype": VtypeMixin.JSON,
        "desc": "默认的主机显示字段",
    },
    {
        "key": RES_HOST_RELATION_SHOW_FIELDS,
        "value": ["bk_host_innerip"],
        "vtype": VtypeMixin.JSON,
        "desc": "默认的主机关联关系显示字段",
    },
    {
        "key": RES_HOST_OTHER_FIELDS,
        "value": [
            {"bk_property_id": "belong_app", "bk_property_name": "所属应用"},
            {"bk_property_id": "belong_set", "bk_property_name": "所属集群"},
            {"bk_property_id": "belong_module", "bk_property_name": "所属模块"},
            {"bk_property_id": "agent_status", "bk_property_name": "agent状态"},
            {"bk_property_id": "db_inst", "bk_property_name": "数据库实例"},
            {"bk_property_id": "middleware_inst", "bk_property_name": "中间件实例"},
            {"bk_property_id": "ad_server", "bk_property_name": "AD域服务"},
            {"bk_property_id": "exchange_server", "bk_property_name": "Exchange邮件服务"},
        ],
        "vtype": VtypeMixin.JSON,
        "desc": "RES_HOST_OTHER_FIELDS",
    },
    {
        "key": ACTION_MAPPING_FIELDS,
        "value": [
            {"action": "create", "action_name": "新增"},
            {"action": "update", "action_name": "修改"},
            {"action": "delete", "action_name": "删除"},
            {"action": "assign_host", "action_name": "分配到业务"},
            {"action": "unassign_host", "action_name": "归还到资源池"},
            {"action": "transfer_host_module", "action_name": "转移模块"},
            {"action": "archive", "action_name": "归档"},
            {"action": "recover", "action_name": "恢复"},
            {"action": "stop", "action_name": "停用"},
            {"action": "resume", "action_name": "启用"},
        ],
        "vtype": VtypeMixin.JSON,
        "desc": "CMDB操作映射",
    },
    {
        "key": DEFAULT_MENU_IDS,
        "value": ["workorder-MyTicket", "workorder-wikiPage", "MonitorApp", "ApplicationView", "health_AppHealth"],
        "vtype": VtypeMixin.JSON,
        "desc": "默认快捷入口",
    },
    {
        "key": CLASSIFICATIONS_GROUP,
        "value": Menus.get_menus_classification_list(),
        "vtype": VtypeMixin.JSON,
        "desc": "资产模型分类",
    },
    {"key": MONITOR_GROUP, "value": Menus.get_monitor_group_dict(), "vtype": VtypeMixin.JSON, "desc": "监控模型分类"},
    {"key": CASBIN_TIME, "value": CASBIN_POLICY_LOAD_TIME, "vtype": VtypeMixin.STRING, "desc": "casbin更新policy时间"},
    {"key": "modify_metric_and_tasks", "value": False, "vtype": VtypeMixin.BOOLEAN, "desc": "是否更新了网络设备监控模板"},
]

"""
用户 角色的常量
"""

INIT_POLICY = "init_policy"
INIT_POLICY_DISPLAY_NAME = "v3.16重新初始化策略"

DB_OPERATE_IDS = "operate_ids"
DB_OPERATE_IDS_DISPLAY_NAME = "菜单操作权限"

DB_MENU_IDS = "menu_ids"
DB_MENU_IDS_DISPLAY_NAME = "菜单权限"

DB_APPS = "app_ids"
DB_APPS_DISPLAY_NAME = "应用权限"

DB_API_PATHS = "api_id"
DB_API_PATHS_DISPLAY_NAME = "角色api路由"

DB_BIZ_IDS = "biz_id"
DB_BIZ_IDS_DISPLAY_NAME = "系统关注业务ID列表(对应CMDB业务ID)"

# 角色
DB_NORMAL_USER = "normal_group"
DB_NORMAL_USER_DISPLAY_NAME = "普通用户"

DB_SUPER_USER = "admin_group"
DB_SUPER_USER_DISPLAY_NAME = "超级管理员"

DB_NOT_ACTIVATION_ROLE = "not_activation"
DB_NOT_ACTIVATION_ROLE_DISPLAY_NAME = "未激活角色"


"""
性别枚举
"""
SEX_MAPPING = {"男": 0, "女": 1}

DOMAIN = "default.local"  # 用户 默认目录 可修改

init_policy_data = {"key": INIT_POLICY, "value": True, "vtype": VtypeMixin.BOOLEAN, "desc": "v3.16重新初始化策略"}

init_templates = [
    {"role_name": DB_NORMAL_USER, "describe": "本角色为普通用户，需要超级管理员赋予其他权限", "built_in": True},
    {"role_name": DB_SUPER_USER, "describe": "本角色为超级管理员，有全部的权限", "built_in": True},
    {"role_name": DB_NOT_ACTIVATION_ROLE, "describe": "本角色为未激活weops的用户的默认角色", "built_in": True},
]

"""
角色操作权限中心
"""

"""
页面权限控制 按照功能
"""

"""
基础服务:
    远程
"""

# 默认的app 基础服务
DEFAULT_MENUS_MAPPING = {
    "resource": "基础资产",
    "auto_discovery": "基础资产能力",
    "system_mgmt": "系统配置",
    "index": "首页",
    "bk_sops": "自动化能力",
}

# 可选的app 还需要加到utils/casbin_register_policy.py下的MENUS里
MENUS_MAPPING = {
    "health_advisor": "健康顾问",
    "monitor_mgmt": "监控告警",
    "operational_tools": "自动化（工具）",
    "repository": "知识库",
    "big_screen": "运营分析",
    "senior_resource": "资产（进阶）",
    "custom_topology": "拓扑图",
    "patch_mgmt": "自动化（补丁管理）",
    "auto_process": "自动化（编排）",
    "syslog": "日志",
    "chat_ops": "ChatOps",
    "dashboard": "仪表盘",
}

# 可选的app的path
MENUS_CHOOSE_MAPPING = {
    # 健康扫描
    "health_advisor": ["health_advisor/resource", "health_advisor/scan_package", "health_advisor/scan_task"],
    # 监控告警
    "monitor_mgmt": [
        "monitor_mgmt/monitor",
        "monitor_mgmt/uac",
        "monitor_mgmt/cloud",
        "monitor_mgmt/dashboard",
        "monitor_mgmt/metric_view",
        "monitor_mgmt/metric_group",
        "monitor_mgmt/metric_obj",
        "monitor_mgmt/k8s_collect",
        "monitor_mgmt/monitor_collect",
        "monitor_mgmt/network_collect",
        "monitor_mgmt/network_classification",
        "monitor_mgmt/cloud_monitor_task",
        "monitor_mgmt/hardware_monitor_task",
    ],
    # 运维工具
    "operational_tools": [
        "operational_tools/tools",
        "operational_tools/tools_manage",
        "operational_tools/network_tool/template",
        "operational_tools/network_tool/template_march",
    ],
    # 知识库
    "repository": ["repository", "repository/labels", "repository/templates"],
    # 大屏
    "big_screen": ["big_screen", "big_screen/v2"],
    # 资产（进阶）
    "senior_resource": ["senior_resource/v2/obj", "senior_resource/subscribe"],
    # 补丁管理
    "patch_mgmt": ["patch_mgmt/patchtask", "patch_mgmt/patchfile"],
    # 自动化编排
    "auto_process": [],
    # 日志
    "syslog": ["syslog", "syslog/probe", "syslog/collectors_config"],
    # 拓扑图
    "custom_topology": ["custom_topology"],
}

#  默认页面权限
MENUS_DEFAULT = {
    "index": ["index"],  # 首页
    "big_screen": ["big_screen"],  # 数据大屏
    "system_manage": [
        "system/mgmt/sys_users",
        "system/mgmt/operation_log",
        "system/mgmt/user_manage",
        "system/mgmt/role_manage",
        "system/mgmt/sys_setting",
        "activation",  # weops激活
    ],  # 系统管理
    "resource": [
        "resource/v2/host/inst",
        "resource/v2/profile",
        "resource",
        "resource/v2/service_instance",
        "resource/v2/biz/inst",
        "resource/v2/other_obj",
        "resource/v2/obj",
        "resource/objects",
    ],  # 资源记录
}

# 页面菜单和权限去除的模型分类 主机 数据库 配置文件
MENUS_REMOVE_CLASSIFICATIONS = ["bk_file"]

# 菜单管理常量
MENU_DATA = {
    "menu_name": "默认菜单",
    "default": True,
    "use": True,
    "menu": list,
    "created_by": "admin",
    "updated_by": "admin",
}

# 权限类
USE = "use"
VIEW = "view"
MANAGE = "manage"
PERMISSIONS_CHOICES = (
    (VIEW, "查询"),
    # (USE, "使用"),
    (MANAGE, "管理"),
)

PERMISSIONS_MAPPING = {"view": "查询", "manage": "管理", "use": "使用"}

INSTANCE_MONITOR = "监控采集"
INSTANCE_MONITOR_POLICY = "监控策略"
INSTANCE_MONITORS = [INSTANCE_MONITOR, INSTANCE_MONITOR_POLICY]

INSTANCE_TYPES = {"仪表盘", "拓扑图", "知识库", "运维工具", INSTANCE_MONITOR, INSTANCE_MONITOR_POLICY}

# 监控里，非这些的统一都是统一链路
NOT_BASIC_MONITOR = ["bk_device", "hard_server", "Cloud", "process", "k8s", "uptimecheck"]
BASIC_MONITOR = "basic_monitor"  # 监控采集默认
BASIC_MONITOR_POLICY = "basic_monitor_policy"  # 监控策略默认
BASIC_MONITOR_POLICY_ALL = [BASIC_MONITOR, BASIC_MONITOR_POLICY]

ALL_INST_PERMISSIONS_OBJ = copy.deepcopy(NOT_BASIC_MONITOR)
ALL_INST_PERMISSIONS_OBJ.extend(BASIC_MONITOR_POLICY_ALL)
