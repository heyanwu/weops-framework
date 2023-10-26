# -*- coding: utf-8 -*-

# @File    : policy_constants.py
# @Date    : 2022-07-01
# @Author  : windyzhao
"""
存储静态接口 也可存为json
"""

# ==== casbin mesh 的静态常量
MESH_NAMESPACE = "weops_rbac"
MESH_MODEL = """
[request_definition]
r = sub, obj, act
[policy_definition]
p = sub, obj, act, operate, menu, version
[role_definition]
g = _, _
[policy_effect]
e = some(where (p.eft == allow))
[matchers]
m = g(r.sub, p.sub) && regexMatch(r.obj, p.obj) && r.act == p.act
"""

# ====


# 3.8数据初始化到3.9格式

OPERATE_ENDSWITH = "Manage"
CONFIG_IDS = "configFile"

OPERATE_IDS_MAPPING = {
    "AssetRecordsHost": ["host", "serviceInstance", "configFile"],
}

checkAuth = "checkAuth"  # 查看
operateAuth = "operateAuth"  # 操作
manageMyArticlesAuth = "manageMyArticlesAuth"  # 管理我的文章
manageAllArticlesAuth = "manageAllArticlesAuth"  # 管理所有文章
manageDeskArticlesAuth = "manageDeskArticlesAuth"  # 管理服务台文章

hostManage = "hostManage"  # 主机管理
serviceInstanceManage = "serviceInstanceManage"  # 服务实例管理
configFileManage = "configFileManage"  # 配置文件管理

QUERY = "query"  # 查看

# 操作
CREATE = "create"
MODIFY = "modify"
DELETE = "delete"
UPLOAD = "upload"
DOWNLOAD = "download"
RESET = "reset"
EXEC = "exec"
COLLECT = "collect"
IMPORT = "import"
LONG_DISTANCE = "long_distance"
OUTPUT = "output"

OPERATE = {
    CREATE: "新增",
    MODIFY: "修改",
    DELETE: "删除",
    UPLOAD: "上传",
    DOWNLOAD: "下载",
    RESET: "重置",
    COLLECT: "收藏",
    LONG_DISTANCE: "远程",
    EXEC: "执行",
    IMPORT: "导入",
    OUTPUT: "导出",
}

# 内嵌通过
PASS_MENUS = {
    "AlarmManage",  # 告警管理
    "ServiceDeskManage",  # 服务台管理
    "NoticeWays",  # 通知渠道
    "CreditManage",  # 许可管理
    "Digital",  # 数据大屏
}

# 基础监控和资产记录的其他的 全部用一下的接口
RESOURCE_OTHER = "AssetRecordsOther"
BASICMONITOR_OTHER = "BasicMonitorOTHERS"

# 根据版本动态进行增加新版本的接口 每个版本都需要修改
POLICY_VERSION = "v4.2"

# 菜单操作 合并 拆分 新增 删除
MENU_OPERATOR = {
    "merge": {"v3.14": [("CloudMonitorVMware", ["VirtualMonitorVM", "VirtualMonitorESXI", "VirtualMonitorStorage"])]},
    "split": {
        "v3.16": [
            ("AutoManage", ["PackageManage", "OperationToolsManage", "AutoProcessManage", "WebEquipmentlManage"])
        ],
        "v4.2": [
            (
                "MonitorManage",
                ["MonitorGather", "MonitorPolicy", "MonitorObject", "DynamicGroup", "IndicatorManage", "AgentManage"],
            ),
            ("AssetModel", ["ModelManage", "AutoDiscovery", "OidManage"]),
            ("loreManage", ["ArticleTemplateManage", "ArticleTagManage"]),
        ],
    },
    "add": {},
    "remove": {"CloudMonitorVMware", "AutoManage", "MonitorManage", "AssetModel"},
}

# 静态路由白名单
PASS_PATH = {
    ("/", "GET"),
    ("/mobile/", "GET"),
    ("/mobile/login/user/info/", "GET"),
    # 回调函数
    ("/operational_tools/job_call_back/", "POST"),
    ("/auto_mate/auto_mate_exec_ansible_call_back/", "POST"),
    ("/health/advisor/job_call_back/", "POST"),
    ("/open_api/user/get_user_role/", "GET"),
    ("/get_admins/", "GET"),
    ("/verify_user_auth/", "GET"),
    ("/get_application_overview/", "GET"),
    ("/create_remote_log/", "GET"),
    ("/get_biz_list/", "GET"),
    ("/system/mgmt/reset_policy_init/", "POST"),
    ("/system/mgmt/sys_users/", "GET"),
    ("/login_info/", "GET"),
    ("/system/mgmt/logo/", "GET"),
    ("/system/mgmt/role_manage/menus/", "GET"),
    ("/system/mgmt/sys_users/bizs/", "GET"),
    ("/resource/v2/biz/inst/attributes/", "GET"),
    ("/resource/v2/biz/inst/attributes/", "PUT"),
    ("/resource/v2/host/inst/attributes/", "GET"),
    ("/resource/v2/host/inst/attributes/", "PUT"),
    ("/resource/v2/profile/get_object_association/", "GET"),
    ("/resource/v2/biz/inst/list_objects_relation/", "GET"),
    ("/resource/v2/biz/inst/biz_list/", "GET"),
    ("/system/mgmt/role_manage/get_all_roles/", "GET"),
    ("/node/management/meta/filter_conditiong/", "GET"),
    ("/node/management/cloud/", "GET"),
    ("/node/management/ap/", "GET"),
    ("/resource/v2/obj/asst/list/", "GET"),
    ("/resource/v2/obj/label/", "GET"),
    ("/resource/business/", "GET"),
    ("/resource/v2/other_obj/host/inst/attributes/", "GET"),
    ("/resource/v2/host/inst/relation_attributes/", "PUT"),
    ("/resource/v2/other_obj/log/detail/", "GET"),
    ("/bk_sops/common_template", "GET"),
    ("/bk_sops/taskflow", "POST"),
    ("/account/login_success/", "GET"),
    ("/patch_mgmt/distribute_file_callback/", "POST"),
    ("/patch_mgmt/patch_file_callback/", "POST"),
    ("/resource/v2/obj/mainline/obj_topo/", "GET"),
    ("/auto_mate/open_oid/", "POST"),
    ("/auto_mate/open_access_point/", "GET"),
    ("/system/mgmt/sys_setting/wx_app_id/", "POST"),
    ("/system/mgmt/role_manage/sync_alarm_center_group/", "GET"),
}

# 动态路由白名单
MATCH_PASS_PATH = {
    (r"/bk_sops/common_template/(?P<template_id>\d+)", "DELETE"),
    (r"/resource/v2/other_obj/(?P<bk_obj_id>.+?)/inst/attributes/", "PUT"),
    (r"/resource/v2/other_obj/(?P<bk_obj_id>.+?)/inst/relation_attributes/", "PUT"),
    (r"/resource/v2/other_obj/(?P<bk_obj_id>.+?)/inst/relation_attributes/", "PUT"),
    (r"/api/cc/*", "PUT"),
    (r"/api/cc/*", "GET"),
    (r"/api/cc/*", "POST"),
}

# 告警操作通用接口
ALARM_OPERATE = {
    ("/uac/add_execute/", "POST", CREATE, "v3.9"),
    ("/uac/delete_execute/", "POST", DELETE, "v3.9"),
    ("/uac/modify_execute/", "POST", MODIFY, "v3.9"),
    ("/uac/set_execute_status/", "POST", MODIFY, "v3.9"),
    ("/uac/auto_execute/", "POST", MODIFY, "v3.9"),
    ("/uac/only_response/", "POST", MODIFY, "v3.9"),
    ("/uac/transmit/", "POST", MODIFY, "v3.9"),
    ("/uac/approval/", "POST", MODIFY, "v3.9"),
    ("/uac/close/", "POST", MODIFY, "v3.9"),
    # 运维工具
    ("/tools/get_tool_type/", "GET", QUERY, "v3.9"),
    ("/tools/", "GET", QUERY, "v3.9"),
    ("/tools/hosts/", "GET", QUERY, "v3.9"),
    ("/tools/exec_tool/", "POST", EXEC, "v3.9"),
    ("/tools/exec_history/", "GET", QUERY, "v3.9"),
    ("/tools/reports/", "GET", QUERY, "v3.9"),
    ("/tools/report_info/", "GET", QUERY, "v3.9"),
    ("/tools/stop_jobs/", "POST", EXEC, "v3.9"),
    ("/tools/download_log/", "POST", DOWNLOAD, "v3.9"),
    ("/long_distance/upload_files/", "POST", CREATE, "v3.9"),
}

# 知识库操作
LORE_OPERATE = {
    ("/repository/", "POST", CREATE, "v3.9"),
    (r"/repository/(?P<pk>[^/.]+)/", "PUT", MODIFY, "v3.9"),
    (r"/repository/(?P<pk>[^/.]+)/", "DELETE", DELETE, "v3.9"),
    ("/repository/upload_repositories/", "POST", CREATE, "v3.10"),
    ("/repository/delete_images/", "POST", DELETE, "v3.10"),
    ("/repository/upload_image/", "POST", CREATE, "v3.10"),
    ("/repository/drafts/", "POST", CREATE, "v3.10"),
}

# (路由，请求方式，操作方式，版本)
POLICY = {
    # 首页
    "Home": {
        checkAuth: {
            ("/monitor_mgmt/uac/get_actives_alarm_statistics/", "GET", QUERY, "v3.9"),
            ("/monitor_mgmt/uac/search_history_alarm_list/", "GET", QUERY, "v3.9"),
            ("/monitor_mgmt/uac/search_active_alarm_list/", "GET", QUERY, "v3.9"),
            ("/monitor_mgmt/uac/search_my_alarm_list/", "GET", QUERY, "v3.9"),
            ("/monitor_mgmt/uac/get_alarm_detail/", "GET", QUERY, "v3.9"),
            ("/monitor_mgmt/uac/alarm_metric/", "GET", QUERY, "v3.9"),
            ("/monitor_mgmt/uac/alarm_lifecycle/", "GET", QUERY, "v3.9"),
            ("/monitor_mgmt/uac/get_alarm_obj_topo/", "GET", QUERY, "v3.9"),
            ("/monitor_mgmt/uac/get_notify_id_data/", "GET", QUERY, "v3.11"),
            ("/monitor_mgmt/uac/get_alarm_id_notify_data/", "GET", QUERY, "v3.11"),
        },
        operateAuth: {
            ("/monitor_mgmt/uac/add_execute/", "POST", CREATE, "v3.9"),
            ("/monitor_mgmt/uac/delete_execute/", "POST", DELETE, "v3.9"),
            ("/monitor_mgmt/uac/modify_execute/", "POST", MODIFY, "v3.9"),
            ("/monitor_mgmt/uac/set_execute_status/", "POST", MODIFY, "v3.9"),
            ("/monitor_mgmt/uac/auto_execute/", "POST", MODIFY, "v3.9"),
            ("/monitor_mgmt/uac/only_response/", "POST", MODIFY, "v3.9"),
            ("/monitor_mgmt/uac/transmit/", "POST", MODIFY, "v3.9"),
            ("/monitor_mgmt/uac/approval/", "POST", MODIFY, "v3.9"),
            ("/monitor_mgmt/uac/close/", "POST", MODIFY, "v3.9"),
        },
    },
    # 事件-工单
    "Ticket": {
        checkAuth: {
        },
    },
    # 自动化运维-运维工具
    "OperationTools": {
        checkAuth: {
            ("/tools/get_tool_type/", "GET", QUERY, "v3.9"),
            ("/tools/", "GET", QUERY, "v3.9"),
            ("/tools/hosts/", "GET", QUERY, "v3.9"),
            ("/tools/exec_history/", "GET", QUERY, "v3.9"),
            ("/tools/report_info/", "GET", QUERY, "v3.9"),
            ("/tools/reports/", "GET", QUERY, "v3.9"),
            ("/tools/get_networks/", "GET", QUERY, "v3.12"),
        },
        operateAuth: {
            ("/tools/exec_tool/", "POST", EXEC, "v3.9"),
            ("/tools/stop_jobs/", "POST", EXEC, "v3.9"),
            ("/tools/download_log/", "POST", DOWNLOAD, "v3.9"),
        },
    },
    # 自动化运维-健康扫描
    "HealthAdvisor": {
        checkAuth: {
            ("/health/advisor/scan_task/", "GET", QUERY, "v3.9"),
            ("/health/advisor/scan_package/obj/", "GET", QUERY, "v3.9"),
            ("/health/advisor/scan_package/", "GET", QUERY, "v3.9"),
            ("/resource/obj_inst_list/", "GET", QUERY, "v3.9"),
            (r"/health/advisor/scan_task/(?P<scan_task_id>\d+)/overview/", "GET", QUERY, "v3.9"),
            (r"/health/advisor/scan_task/(?P<task_id>\d+)/", "GET", QUERY, "v3.9"),
            (r"/health/advisor/scan_task/(?P<task_id>\d+)/resources/", "GET", QUERY, "v3.9"),
            (r"/health/advisor/scan_task/resource/(?P<job_task_record_id>\d+)/report/", "GET", QUERY, "v3.9"),
        },
        operateAuth: {
            (r"/health/advisor/scan_task/(?P<task_id>\d+)/run_task/", "GET", EXEC, "v3.9"),
            ("/health/advisor/scan_task/", "POST", CREATE, "v3.9"),
            (r"/health/advisor/scan_task/(?P<task_id>\d+)/", "PATCH", MODIFY, "v3.9"),
            (r"/health/advisor/scan_task/(?P<task_id>\d+)/", "DELETE", DELETE, "v3.9"),
            (r"/health/advisor/scan_task/(?P<job_task_record_id>\d+)/repeat_run_job/", "GET", EXEC, "v3.9"),
        },
    },
    # 资产事件订阅
    "EventSubscription": {
        checkAuth: {
            ("/resource/subscribe/", "GET", QUERY, "v3.13"),
            ("/resource/business/", "GET", QUERY, "v3.13"),
            ("/resource/v2/obj/list/", "GET", QUERY, "v3.13"),
            ("/resource/v2/obj/host/attrs/", "GET", QUERY, "v3.13"),
            (r"/resource/obj_inst_list/(?P<bk_obj_id>.+?)/(?P<bk_biz_id>\d+)/", "GET", QUERY, "v3.13"),
        },
        operateAuth: {
            ("/resource/subscribe/", "POST", CREATE, "v3.13"),
            (r"/resource/subscribe/(?P<pk>\d+)/", "DELETE", DELETE, "v3.13"),
            (r"/resource/subscribe/(?P<pk>\d+)/", "PATCH", MODIFY, "v3.13"),
            (r"/resource/subscribe/(?P<pk>\d+)/run", "POST", EXEC, "v3.13"),
        },
    },
    # 自动化运维-补丁安装
    "PatchInstall": {
        checkAuth: {
            ("/patch_mgmt/match_ip/", "GET", QUERY, "v3.10"),
            ("/patch_mgmt/upload_temp/", "GET", QUERY, "v3.10"),
            ("/patch_mgmt/get_business_list/", "GET", QUERY, "v3.10"),
            ("/patch_mgmt/list_maintainer/", "GET", QUERY, "v3.10"),
            ("/patch_mgmt/get_biz_inst_topo/", "GET", QUERY, "v3.10"),
            ("/patch_mgmt/list_nodeman_host/", "POST", QUERY, "v3.10"),
            ("/patchtask/", "GET", QUERY, "v3.10"),
            (r"/patchtask/(?P<pk>[^/.]+)/", "GET", QUERY, "v3.10"),
            ("/patchtask/file_exists/", "GET", QUERY, "v3.10"),
            ("/patchtask/get_task_server_detail/", "GET", QUERY, "v3.10"),
            ("/patchtask/import_task_server_detail/", "GET", DOWNLOAD, "v3.10"),
            ("/patchfile/", "GET", QUERY, "v3.10"),
            (r"/patchfile/(?P<pk>[^/.]+)/get_related_task/", "GET", QUERY, "v3.10"),
        },
        operateAuth: {
            ("/patch_mgmt/upload_temp/", "POST", UPLOAD, "v3.10"),
            ("/patch_mgmt/cancel_upload_temp/", "POST", DELETE, "v3.10"),
            ("/patchtask/", "POST", CREATE, "v3.10"),
            (r"/patchtask/(?P<pk>[^/.]+)/", "PUT", MODIFY, "v3.10"),
            (r"/patchtask/(?P<pk>[^/.]+)/", "DELETE", DELETE, "v3.10"),
            (r"/patchtask/(?P<pk>[^/.]+)/run_task/", "POST", EXEC, "v3.10"),
            ("/patchtask/upload_file/", "POST", UPLOAD, "v3.10"),
            ("/patchtask/delete_file/", "DELETE", DELETE, "v3.10"),
            ("/patchfile/merge_files/", "POST", CREATE, "v3.10"),
        },
    },
    # 知识库
    "lore": {
        checkAuth: {
            ("/repository/", "GET", QUERY, "v3.9"),
            ("/repository_labels/", "GET", QUERY, "v3.9"),
            ("/repository_templates/", "GET", QUERY, "v3.9"),
            (r"/repository/(?P<pk>[^/.]+)/repository_collect/", "POST", COLLECT, "v3.9"),
            (r"/repository/(?P<pk>[^/.]+)/repository_cancel_collect/", "POST", COLLECT, "v3.9"),
            ("/repository/get_images/", "POST", QUERY, "v3.10"),
            ("/repository/get_drafts/", "GET", QUERY, "v3.10"),
        },
        manageMyArticlesAuth: LORE_OPERATE,
        manageAllArticlesAuth: LORE_OPERATE,
        manageDeskArticlesAuth: {
            (r"/repository/(?P<pk>[^/.]+)/is_it_service/(?P<judge>.+?)/", "PATCH", COLLECT, "v3.9"),
        },
    },
    # 资产数据-应用
    "ApplicationManage": {
        checkAuth: {
            ("/resource/v2/host/inst/", "GET", QUERY, "v3.9"),
            (r"/resource/v2/obj/(?P<pk>[^/.]+)/attrs/", "GET", QUERY, "v3.9"),
            ("/resource/v2/biz/inst/", "GET", QUERY, "v3.9"),
            ("/resource/v2/biz/inst/disabled_business/", "GET", QUERY, "v3.9"),
            (r"/resource/v2/biz/inst/(?P<pk>[^/.]+)/logs/", "GET", QUERY, "v3.9"),
            (r"/resource/v2/biz/inst/(?P<pk>[^/.]+)/topo/", "GET", QUERY, "v3.9"),
            ("/resource/v2/service_instance/inst/detail/", "POST", QUERY, "v3.9"),
            ("/service_instance/process_list/by_module/", "POST", QUERY, "v3.9"),
            ("/api/vision/search_topology_graph_by_instance", "POST", QUERY, "v3.9"),
            ("/api/vision/search_topology_config", "POST", QUERY, "v3.9"),
            ("/resource/v2/other_obj/log/detail/", "GET", QUERY, "v3.9"),
            (r"/resource/v2/host/inst/(?P<pk>[^/.]+)/logs/", "GET", QUERY, "v3.9"),
            (r"/resource/v2/host/inst/(?P<pk>[^/.]+)/relations/", "GET", QUERY, "v3.9"),
            (r"/resource/v2/other_obj/(?P<bk_obj_id>.+?)/inst/(?P<bk_inst_id>\d+)/", "GET", QUERY, "v3.9"),
            (r"/resource/v2/other_obj/(?P<bk_obj_id>.+?)/inst/(?P<bk_inst_id>\d+?)/logs/", "GET", QUERY, "v3.9"),
            ("/resource/v2/obj/inst_info_by_code/", "GET", QUERY, "v3.15"),
        },
        operateAuth: {
            ("/resource/v2/host/inst/", "GET", OUTPUT, "v3.9"),
            (r"/resource/v2/biz/inst/(?P<pk>[^/.]+)/topo_node/", "PATCH", MODIFY, "v3.9"),
            (r"/resource/v2/biz/inst/(?P<pk>[^/.]+)/topo_node/", "DELETE", DELETE, "v3.14"),
            ("/resource/v2/biz/inst/create_business/", "POST", CREATE, "v3.9"),
            (r"/resource/v2/biz/inst/(?P<pk>[^/.]+)/topo_node/", "POST", CREATE, "v3.9"),
            ("/resource/v2/biz/inst/transfer_resource_to_business/", "POST", CREATE, "v3.9"),
            ("/resource/v2/biz/inst/business_status/", "PUT", MODIFY, "v3.9"),
            ("/resource/v2/host/inst/bult_update/", "PUT", MODIFY, "v3.9"),
            ("/resource/v2/host/inst/create_resource/", "POST", CREATE, "v3.9"),
            ("/resource/v2/service_instance/inst/", "POST", CREATE, "v3.9"),
            ("/resource/v2/service_instance/inst/", "PUT", MODIFY, "v3.9"),
            ("/resource/v2/service_instance/inst/", "DELETE", DELETE, "v3.9"),
            (r"/resource/v2/host/inst/(?P<pk>[^/.]+)/logs/", "POST", CREATE, "v3.9"),
            (r"/resource/v2/other_obj/(?P<bk_obj_id>.+?)/inst/(?P<bk_inst_id>\d+?)/logs/", "POST", CREATE, "v3.9"),
            ("/resource/v2/obj/generate_code/", "POST", CREATE, "v3.15"),
        },
    },
    # 资产数据-主机
    "AssetRecordsHost": {
        checkAuth: {
            ("/credential/", "GET", QUERY, "v3.9"),
            ("/vault_credential/", "GET", QUERY, "v3.12"),
            (r"/vault_credential/(?P<pk>[^/.]+)/get_vault_cred_detail/", "GET", QUERY, "v3.12"),
            (r"/vault_credential/get_remote_credential_list/", "GET", QUERY, "v3.12"),
            ("/resource/v2/host/inst/", "GET", OUTPUT, "v3.9"),
            ("/long_distance/push_file_status/", "GET", QUERY, "v3.9"),
            (r"/resource/v2/other_obj/(?P<bk_obj_id>.+?)/inst/(?P<bk_inst_id>\d+?)/logs/", "GET", QUERY, "v3.9"),
            (r"/resource/v2/obj/(?P<pk>[^/.]+)/attrs/", "GET", QUERY, "v3.9"),
            ("/resource/v2/host/inst/relation_attributes/", "GET", QUERY, "v3.9"),
            ("/resource/v2/service_instance/inst/detail/", "POST", QUERY, "v3.9"),
            ("/service_instance/process_list/by_module/", "POST", QUERY, "v3.9"),
            ("/api/vision/search_topology_graph_by_instance", "POST", QUERY, "v3.9"),
            ("/api/vision/search_topology_config", "POST", QUERY, "v3.9"),
            ("/resource/v2/other_obj/log/detail/", "GET", QUERY, "v3.9"),
            (r"/resource/v2/host/inst/(?P<pk>[^/.]+)/logs/", "GET", QUERY, "v3.9"),
            (r"/resource/v2/host/inst/(?P<pk>[^/.]+)/relations/", "GET", QUERY, "v3.9"),
            ("/resource/v2/biz/inst/list_search_inst/", "GET", QUERY, "v3.9"),
            ("/resource/v2/profile/", "GET", QUERY, "v3.9"),
            (r"/resource/v2/profile/(?P<pk>[^/.]+)/", "GET", QUERY, "v3.9"),
            ("/resource/v2/profile/get_instance_profile/", "GET", QUERY, "v3.9"),
            (r"/resource/v2/other_obj/(?P<bk_obj_id>.+?)/inst/relation_attributes/", "GET", QUERY, "v3.9"),
            (r"/resource/v2/other_obj/(?P<bk_obj_id>.+?)/inst/attributes/", "GET", QUERY, "v3.9"),
            ("/resource/v2/obj/inst_info_by_code/", "GET", QUERY, "v3.15"),
        },
        hostManage: {
            ("/long_distance/upload_files/", "POST", CREATE, "v3.9"),
            ("/long_distance/upload_files/", "POST", CREATE, "v3.9"),
            ("/resource/v2/host/inst/relation_attributes/", "PUT", MODIFY, "v3.9"),
            ("/resource/v2/host/inst/bult_update/", "PUT", MODIFY, "v3.9"),
            ("/resource/v2/host/inst/create_resource/", "POST", CREATE, "v3.9"),
            (r"/resource/v2/host/inst/(?P<pk>[^/.]+)/logs/", "POST", CREATE, "v3.9"),
            ("/resource/v2/biz/inst/add_inst_relation/", "POST", CREATE, "v3.9"),
            ("/resource/v2/biz/inst/delete_instance_relation/", "POST", DELETE, "v3.9"),
            ("/resource/(?P<bk_obj_id>.+?)/download/importtemplate/", "GET", DOWNLOAD, "v3.10"),
            ("/resource/(?P<bk_obj_id>.+?)/import_insts/", "POST", IMPORT, "v3.10"),
            ("/resource/v2/obj/generate_code/", "POST", CREATE, "v3.15"),
        },
        serviceInstanceManage: {
            ("/resource/v2/service_instance/inst/", "POST", CREATE, "v3.9"),
            ("/resource/v2/service_instance/inst/", "PUT", MODIFY, "v3.9"),
            ("/resource/v2/service_instance/inst/", "DELETE", DELETE, "v3.9"),
            ("/resource/v2/biz/inst/add_inst_relation/", "POST", CREATE, "v3.9"),
            ("/resource/v2/biz/inst/delete_instance_relation/", "POST", DELETE, "v3.9"),
            (r"/resource/v2/other_obj/(?P<bk_obj_id>.+?)/inst/relation_attributes/", "PUT", MODIFY, "v3.9"),
        },
        configFileManage: {
            ("/resource/v2/profile/", "POST", CREATE, "v3.9"),
            (r"/resource/v2/profile/(?P<pk>[^/.]+)/", "PUT", MODIFY, "v3.9"),
            (r"/resource/v2/profile/(?P<pk>[^/.]+)/", "POST", CREATE, "v3.9"),
            (r"/resource/v2/profile/(?P<pk>[^/.]+)/", "DELETE", DELETE, "v3.9"),
            ("/resource/v2/profile/create_profile/", "POST", CREATE, "v3.9"),
            ("/resource/v2/profile/download_save_log/", "GET", DOWNLOAD, "v3.9"),
            (r"/resource/v2/other_obj/(?P<bk_obj_id>.+?)/inst/relation_attributes/", "PUT", MODIFY, "v3.9"),
            (r"/resource/v2/other_obj/(?P<bk_obj_id>.+?)/inst/(?P<bk_inst_id>\d+)/", "PATCH", MODIFY, "v3.9"),
            (r"/resource/v2/other_obj/(?P<bk_obj_id>.+?)/inst/(?P<bk_inst_id>\d+?)/logs/", "POST", CREATE, "v3.9"),
        },
    },
    # 资产记录其他的 包括 数据库-其他的模型分组
    "AssetRecordsOther": {
        checkAuth: {
            ("/long_distance/push_file_status/", "GET", QUERY, "v3.9"),
            ("/credential/", "GET", QUERY, "v3.9"),
            ("/vault_credential/", "GET", QUERY, "v3.12"),
            (r"/vault_credential/(?P<pk>[^/.]+)/get_vault_cred_detail/", "GET", QUERY, "v3.12"),
            ("/resource/v2/biz/inst/list_search_inst/", "GET", QUERY, "v3.9"),
            ("/api/vision/search_topology_graph_by_instance", "POST", QUERY, "v3.9"),
            (r"/resource/v2/obj/(?P<pk>[^/.]+)/attrs/", "GET", QUERY, "v3.9"),
            ("/resource/v2/host/inst/relation_attributes/", "GET", QUERY, "v3.9"),
            (r"/resource/v2/other_obj/(?P<bk_obj_id>.+?)/inst/relation_attributes/", "GET", QUERY, "v3.9"),
            (r"/resource/v2/other_obj/(?P<bk_obj_id>.+?)/inst/(?P<bk_inst_id>\d+)/", "GET", QUERY, "v3.9"),
            (r"/resource/v2/other_obj/(?P<bk_obj_id>.+?)/inst/(?P<bk_inst_id>\d+)/relations/", "GET", QUERY, "v3.9"),
            (r"/resource/v2/other_obj/(?P<bk_obj_id>.+?)/inst/(?P<bk_inst_id>\d+?)/logs/", "GET", QUERY, "v3.9"),
            (r"/resource/v2/other_obj/(?P<bk_obj_id>.+?)/inst/", "GET", QUERY, "v3.9"),
            (r"/resource/v2/other_obj/(?P<bk_obj_id>.+?)/inst/attributes/", "GET", QUERY, "v3.9"),
            ("/resource/v2/profile/", "GET", QUERY, "v3.9"),
            (r"/resource/v2/profile/(?P<pk>[^/.]+)/", "GET", QUERY, "v3.9"),
            ("/resource/v2/profile/get_instance_profile/", "GET", QUERY, "v3.9"),
            ("/resource/v2/obj/inst_info_by_code/", "GET", QUERY, "v3.15"),
        },
        operateAuth: {
            ("/long_distance/upload_files/", "POST", CREATE, "v3.9"),
            ("/resource/v2/host/inst/create_resource/", "POST", CREATE, "v3.9"),
            ("/long_distance/upload_files/", "POST", CREATE, "v3.9"),
            (r"/resource/v2/other_obj/(?P<bk_obj_id>.+?)/inst/(?P<bk_inst_id>\d+)/", "POST", CREATE, "v3.9"),
            (r"/resource/v2/other_obj/(?P<bk_obj_id>.+?)/inst/(?P<bk_inst_id>\d+?)/logs/", "POST", CREATE, "v3.9"),
            (r"/resource/v2/other_obj/(?P<bk_obj_id>.+?)/inst/bult_update/", "PUT", MODIFY, "v3.9"),
            ("/resource/v2/host/inst/batch_delete_resource/", "POST", CREATE, "v3.9"),
            ("/resource/v2/host/inst/transfer/", "POST", MODIFY, "v3.14"),
            ("/resource/v2/biz/inst/add_inst_relation/", "POST", CREATE, "v3.9"),
            ("/resource/v2/biz/inst/delete_instance_relation/", "POST", DELETE, "v3.9"),
            ("/resource/(?P<bk_obj_id>.+?)/download/importtemplate/", "GET", DOWNLOAD, "v3.10"),
            ("/resource/(?P<bk_obj_id>.+?)/import_insts/", "POST", IMPORT, "v3.10"),
            ("/resource/v2/obj/generate_code/", "POST", CREATE, "v3.15"),
        },
        configFileManage: {
            ("/resource/v2/profile/", "POST", CREATE, "v3.9"),
            (r"/resource/v2/profile/(?P<pk>[^/.]+)/", "POST", CREATE, "v3.9"),
            (r"/resource/v2/profile/(?P<pk>[^/.]+)/", "PUT", MODIFY, "v3.9"),
            (r"/resource/v2/profile/(?P<pk>[^/.]+)/", "DELETE", DELETE, "v3.9"),
            ("/resource/v2/profile/create_profile/", "POST", CREATE, "v3.9"),
            ("/resource/v2/profile/download_save_log/", "GET", DOWNLOAD, "v3.9"),
            (r"/resource/v2/other_obj/(?P<bk_obj_id>.+?)/inst/(?P<bk_inst_id>\d+)/", "PATCH", MODIFY, "v3.9"),
            (r"/resource/v2/other_obj/(?P<bk_obj_id>.+?)/inst/(?P<bk_inst_id>\d+?)/logs/", "POST", CREATE, "v3.9"),
        },
    },
    # 资产数据-远程凭据
    "RemoteVoucher": {
        checkAuth: {
            ("/credential/", "GET", QUERY, "v3.9"),
            (r"/credential/(?P<pk>[^/.]+)/", "GET", QUERY, "v3.9"),
            ("/cred_design/get_cred_params/", "GET", QUERY, "v3.12"),
            ("/vault_credential/", "GET", QUERY, "v3.12"),
            (r"/vault_credential/(?P<pk>[^/.]+)/get_cred_detail/", "GET", QUERY, "v3.12"),
            (r"/vault_credential/(?P<pk>[^/.]+)/get_resource_list/", "GET", QUERY, "v3.12"),
            (r"/vault_credential/(?P<pk>[^/.]+)/get_vault_cred_detail/", "GET", QUERY, "v3.12"),
            ("/system/mgmt/role_manage/search_role_list/", "GET", QUERY, "v3.10"),
            ("/system/mgmt/user_manage/search_user_list/", "GET", QUERY, "v3.10"),
        },
        operateAuth: {
            ("/credential/", "POST", CREATE, "v3.9"),
            (r"/credential/(?P<pk>[^/.]+)/", "PUT", MODIFY, "v3.9"),
            (r"/credential/(?P<pk>[^/.]+)/", "DELETE", DELETE, "v3.9"),
            ("/vault_credential/", "POST", CREATE, "v3.12"),
            (r"/vault_credential/(?P<pk>[^/.]+)/", "PUT", MODIFY, "v3.12"),
            (r"/vault_credential/(?P<pk>[^/.]+)/", "DELETE", DELETE, "v3.12"),
            (r"/vault_credential/(?P<pk>[^/.]+)/set_resource_list/", "POST", MODIFY, "v3.12"),
            (r"/vault_credential/(?P<pk>[^/.]+)/set_auth_list/", "POST", MODIFY, "v3.12"),
        },
    },
    # 自动化管理 包括了 工具管理 扫描包管理 网络设备模版
    "AutoManage": {
        checkAuth: {
            ("/health/advisor/scan_package/", "GET", QUERY, "v3.9"),
            ("/tools_manage/", "GET", QUERY, "v3.9"),
            (r"/tools_manage/(?P<pk>[^/.]+)/", "GET", QUERY, "v3.12"),
            ("/tools_manage/get_tool_type_count/", "GET", QUERY, "v3.12"),
            ("/network_tool/template_march/", "GET", QUERY, "v3.12"),
            (r"/network_tool/template_march/(?P<pk>[^/.]+)/", "GET", QUERY, "v3.12"),
            ("/network_tool/template/", "GET", QUERY, "v3.12"),
            (r"/network_tool/template/(?P<pk>[^/.]+)/", "GET", QUERY, "v3.12"),
        },
        operateAuth: {
            ("/health/advisor/scan_package/import/", "POST", IMPORT, "v3.9"),
            (r"/health/advisor/scan_package/(?P<scan_package_id>\d+)/index/", "PUT", MODIFY, "v3.9"),
            (r"/health/advisor/scan_package/(?P<scan_package_id>\d+)/params/", "PATCH", MODIFY, "v3.9"),
            (r"/health/advisor/scan_package/(?P<scan_package_id>\d+)/", "DELETE", DELETE, "v3.9"),
            ("/tools_manage/", "POST", CREATE, "v3.9"),
            (r"/tools_manage/(?P<pk>[^/.]+)/", "PUT", MODIFY, "v3.9"),
            (r"/tools_manage/(?P<pk>[^/.]+)/", "DELETE", DELETE, "v3.9"),
            (r"/tools_manage/(?P<pk>[^/.]+)/status/", "PATCH", MODIFY, "v3.9"),
            ("/network_tool/template/", "POST", CREATE, "v3.12"),
            (r"/network_tool/template/(?P<pk>[^/.]+)/", "PUT", MODIFY, "v3.12"),
            (r"/network_tool/template/(?P<pk>[^/.]+)/", "DELETE", DELETE, "v3.12"),
            ("/network_tool/template_march/", "POST", CREATE, "v3.12"),
            (r"/network_tool/template_march/(?P<pk>[^/.]+)/", "PUT", MODIFY, "v3.12"),
            (r"/network_tool/template_march/(?P<pk>[^/.]+)/", "DELETE", DELETE, "v3.12"),
        },
    },
    # 管理-管理中心-资产管理
    "AssetModel": {
        checkAuth: {
            ("/resource/v2/obj/count/list/", "GET", QUERY, "v3.9"),
            ("/resource/v2/obj/classification/list/", "GET", QUERY, "v3.9"),
            (r"/resource/v2/obj/(?P<pk>[^/.]+)/attrs/", "GET", QUERY, "v3.9"),
            (r"/resource/v2/obj/(?P<pk>[^/.]+)/relationship/", "GET", QUERY, "v3.9"),
            (r"/kube/search_task/", "GET", QUERY, "v3.10"),
            # 自动发现
            ("/automate/", "GET", QUERY, "v3.12"),
            ("/automate/get_vcenter_or_cloud/", "GET", QUERY, "v3.14"),
            ("/automate/list_regions/", "GET", QUERY, "v3.14"),
            (r"/automate/(?P<pk>[^/.]+)/", "GET", QUERY, "v3.12"),
            (r"/network/topology/", "GET", QUERY, "v3.12"),
            ("/automate/get_task_percent/", "POST", QUERY, "v3.12"),
            (r"/network/topology_scan/status/", "GET", QUERY, "v3.12"),
            (r"/network/network_credential_v2/", "GET", QUERY, "v3.12"),
            ("/automate/access_point/", "GET", QUERY, "v3.14"),
            # oid管理
            ("/oid/", "GET", QUERY, "v3.14"),
            (r"/oid/(?P<pk>[^/.]+)/", "GET", QUERY, "v3.14"),
        },
        operateAuth: {
            ("/automate/", "POST", CREATE, "v3.12"),
            (r"/automate/(?P<pk>[^/.]+)/", "PUT", MODIFY, "v3.12"),
            (r"/automate/(?P<pk>[^/.]+)/", "DELETE", DELETE, "v3.12"),
            (r"/automate/(?P<pk>[^/.]+)/exec_task/", "POST", EXEC, "v3.12"),
            ("/resource/v2/obj/create/association/", "POST", CREATE, "v3.9"),
            (r"/resource/v2/obj/update/association/(?P<association_id>\d+?)/", "POST", MODIFY, "v3.9"),
            (r"/resource/v2/obj/delete/association/(?P<association_id>\d+?)/", "DELETE", DELETE, "v3.9"),
            (r"/resource/v2/obj/(?P<pk>[^/.]+)/attr/", "POST", CREATE, "v3.9"),
            (r"/resource/v2/obj/attr/(?P<attr_id>\d+?)/", "PATCH", MODIFY, "v3.9"),
            (r"/resource/v2/obj/attr/(?P<attr_id>\d+?)/", "DELETE", DELETE, "v3.9"),
            ("/resource/v2/obj/create_classification/", "POST", CREATE, "v3.9"),
            ("/resource/v2/obj/update_classification/", "PUT", MODIFY, "v3.9"),
            (r"/resource/v2/obj/delete_classification/(?P<id>\d+?)/", "DELETE", DELETE, "v3.9"),
            ("/resource/v2/obj/create_object/", "POST", CREATE, "v3.9"),
            ("/resource/v2/obj/update_object/", "PATCH", MODIFY, "v3.9"),
            ("/resource/v2/obj/delete_object/", "POST", DELETE, "v3.9"),
            ("/kube/add_task/", "POST", CREATE, "v3.10"),
            (r"/kube/delete_task/(?P<task_id>\d+)/", "DELETE", DELETE, "v3.10"),
            ("/kube/update_task/", "PUT", MODIFY, "v3.10"),
            (r"/kube/run_task/(?P<task_id>\d+)/", "POST", EXEC, "v3.10"),
            (r"/network/update/topology/", "POST", MODIFY, "v3.12"),
            (r"/network/topology_scan/", "POST", EXEC, "v3.12"),
            # oid管理
            ("/oid/", "POST", CREATE, "v3.14"),
            (r"/oid/(?P<pk>[^/.]+)/", "PUT", MODIFY, "v3.14"),
            (r"/oid/(?P<pk>[^/.]+)/", "DELETE", DELETE, "v3.14"),
            (r"/resource/v2/obj/(?P<pk>[^/.]+)/delete_objectattgroup/", "DELETE", DELETE, "v3.15"),
            ("/resource/v2/obj/update_objectattgroup/", "PUT", MODIFY, "v3.15"),
            ("/resource/v2/obj/create_objectattgroup/", "POST", CREATE, "v3.15"),
        },
    },
    # 管理-管理中心-知识库管理
    "loreManage": {
        checkAuth: {("/repository_labels/", "GET", QUERY, "v3.9"), ("/repository_templates/", "GET", QUERY, "v3.9")},
        operateAuth: {
            ("/repository_labels/", "POST", CREATE, "v3.9"),
            (r"/repository_labels/(?P<pk>[^/.]+)/", "PUT", MODIFY, "v3.9"),
            (r"/repository_labels/(?P<pk>[^/.]+)/", "DELETE", DELETE, "v3.9"),
            ("/repository_templates/", "POST", CREATE, "v3.9"),
            (r"/repository_templates/(?P<pk>[^/.]+)/", "PUT", MODIFY, "v3.9"),
            (r"/repository_templates/(?P<pk>[^/.]+)/", "DELETE", DELETE, "v3.9"),
        },
    },
    # 管理-系统管理-角色管理
    "SysRole": {
        checkAuth: {
            ("/system/mgmt/role_manage/get_roles/", "GET", QUERY, "v3.9"),
            ("/system/mgmt/role_manage/get_role_applications/", "GET", QUERY, "v3.9"),
        },
        operateAuth: {
            ("/system/mgmt/role_manage/create_role/", "POST", CREATE, "v3.9"),
            ("/system/mgmt/role_manage/delete_role/", "DELETE", DELETE, "v3.9"),
            ("/system/mgmt/role_manage/edit_role/", "PUT", MODIFY, "v3.9"),
            ("/system/mgmt/role_manage/get_role_menus/", "GET", QUERY, "v3.9"),
            ("/system/mgmt/role_manage/set_role_menus/", "POST", MODIFY, "v3.9"),
            ("/system/mgmt/role_manage/set_app_permissions/", "POST", MODIFY, "v3.9"),
        },
    },
    # 管理-系统管理-用户管理
    "SysUser": {
        checkAuth: {
            ("/system/mgmt/user_manage/get_users/", "GET", QUERY, "v3.9"),
            ("/system/mgmt/sys_setting/get_login_set/", "GET", QUERY, "v3.10"),
            ("/system/mgmt/role_manage/search_role_list/", "GET", QUERY, "v3.10"),
            ("/system/mgmt/user_manage/search_user_list/", "GET", QUERY, "v3.10"),
            ("/system/mgmt/sys_setting/get_domain/", "GET", QUERY, "v3.13"),
        },
        operateAuth: {
            ("/system/mgmt/user_manage/create_user/", "POST", CREATE, "v3.9"),
            ("/system/mgmt/user_manage/edit_user/", "PATCH", MODIFY, "v3.9"),
            ("/system/mgmt/user_manage/set_user_roles/", "POST", CREATE, "v3.9"),
            ("/system/mgmt/user_manage/reset_password/", "PATCH", MODIFY, "v3.9"),
            ("/system/mgmt/user_manage/delete_users/", "DELETE", DELETE, "v3.9"),
            ("/system/mgmt/sys_users/pull_bk_user/", "POST", CREATE, "v3.9"),
            ("/system/mgmt/sys_setting/update_login_set/", "POST", QUERY, "v3.10"),
            ("/system/mgmt/sys_setting/send_validate_code/", "POST", QUERY, "v3.10"),
            ("/system/mgmt/sys_setting/set_domain/", "POST", QUERY, "v3.13"),
        },
    },
    # 管理-系统管理-自愈流程
    "SelfCureProcess": {
        checkAuth: {
            ("/uac/search_execute_list/", "GET", QUERY, "v3.9"),
            ("/uac/get_execute_template_list/", "GET", QUERY, "v3.9"),
        },
        operateAuth: {
            ("/uac/add_execute/", "POST", CREATE, "v3.9"),
            ("/uac/modify_execute/", "PUT", MODIFY, "v3.9"),
            ("/uac/set_execute_status/", "PATCH", MODIFY, "v3.9"),
            ("/uac/delete_execute/", "POST", DELETE, "v3.9"),
        },
    },
    # 管理-系统管理-操作日志
    "SysLog": {checkAuth: {("/system/mgmt/operation_log/", "GET", QUERY, "v3.9")}},
    # 管理-系统管理-Logo设置
    "SysLogo": {
        checkAuth: {("/system/mgmt/logo/", "GET", QUERY, "v3.9")},
        operateAuth: {
            ("/system/mgmt/logo/", "PUT", MODIFY, "v3.9"),
            ("/system/mgmt/logo/reset/", "POST", MODIFY, "v3.9"),
        },
    },
    # 自动化流程（暂时不进行API层级管控）
    # "BkSops": {
    #     checkAuth: {
    #         ("/bk_sops/common_template", "GET", QUERY, "v3.9"),  # 查询公共流程
    #         ("/bk_sops/taskflow", "POST", QUERY, "v3.9"),    # 查询流程执行记录
    #     },
    #     operateAuth: {
    #         (r"/bk_sops/common_template/(?P<template_id>\d+)", "DELETE", DELETE, "v3.9"),    # 删除公共流程
    #         ("/uac/add_execute/", "POST", CREATE, "v3.9"),  # 公共流程设为告警自愈流程
    #         ("/uac/delete_execute/", "POST", DELETE, "v3.9"),   # 公共流程取消设置告警自愈流程
    #     },
    # },
    # 大屏权限
    "Digital": {
        checkAuth: {
            ("/appWallScreen/", "GET", QUERY, "v3.13"),
            ("/resource/large_screen/biz_list/", "GET", QUERY, "v3.13"),
            ("/resource/large_screen/biz_alarm/count_list/", "GET", QUERY, "v3.13"),
            ("/resource/large_screen/biz_alarm/", "GET", QUERY, "v3.13"),
            ("/resource/large_screen/biz_topo/", "GET", QUERY, "v3.13"),
            ("/uac/get_alarm_detai", "GET", QUERY, "v3.13"),
            ("/uac/alarm_metric", "GET", QUERY, "v3.13"),
        },
        operateAuth: {},
    },
    # 网络设备模版
    "WebEquipmentlManage": {
        checkAuth: {
            ("/network_tool/template_march/", "GET", QUERY, "v3.12"),
            (r"/network_tool/template_march/(?P<pk>[^/.]+)/", "GET", QUERY, "v3.12"),
            ("/network_tool/template/", "GET", QUERY, "v3.12"),
            (r"/network_tool/template/(?P<pk>[^/.]+)/", "GET", QUERY, "v3.12"),
        },
        operateAuth: {
            ("/network_tool/template/", "POST", CREATE, "v3.12"),
            (r"/network_tool/template/(?P<pk>[^/.]+)/", "PUT", MODIFY, "v3.12"),
            (r"/network_tool/template/(?P<pk>[^/.]+)/", "DELETE", DELETE, "v3.12"),
            ("/network_tool/template_march/", "POST", CREATE, "v3.12"),
            (r"/network_tool/template_march/(?P<pk>[^/.]+)/", "PUT", MODIFY, "v3.12"),
            (r"/network_tool/template_march/(?P<pk>[^/.]+)/", "DELETE", DELETE, "v3.12"),
        },
    },
    "OperationToolsManage": {
        checkAuth: {
            ("/tools_manage/", "GET", QUERY, "v3.9"),
            (r"/tools_manage/(?P<pk>[^/.]+)/", "GET", QUERY, "v3.12"),
            ("/tools_manage/get_tool_type_count/", "GET", QUERY, "v3.12"),
        },
        operateAuth: {
            ("/tools_manage/", "POST", CREATE, "v3.9"),
            (r"/tools_manage/(?P<pk>[^/.]+)/", "PUT", MODIFY, "v3.9"),
            (r"/tools_manage/(?P<pk>[^/.]+)/", "DELETE", DELETE, "v3.9"),
            (r"/tools_manage/(?P<pk>[^/.]+)/status/", "PATCH", MODIFY, "v3.9"),
        },
    },
    "PackageManage": {
        checkAuth: {("/health/advisor/scan_package/", "GET", QUERY, "v3.9")},
        operateAuth: {
            ("/health/advisor/scan_package/import/", "POST", IMPORT, "v3.9"),
            (r"/health/advisor/scan_package/(?P<scan_package_id>\d+)/index/", "PUT", MODIFY, "v3.9"),
            (r"/health/advisor/scan_package/(?P<scan_package_id>\d+)/params/", "PATCH", MODIFY, "v3.9"),
            (r"/health/advisor/scan_package/(?P<scan_package_id>\d+)/", "DELETE", DELETE, "v3.9"),
        },
    },
    "AutoProcessManage": {
        checkAuth: {
            ("/bk_sops/common_template/", "GET", QUERY, "v3.9"),  # 查询公共流程
            ("/bk_sops/taskflow/", "POST", QUERY, "v3.9"),  # 查询流程执行记录
        },
        operateAuth: {
            (r"/bk_sops/common_template/(?P<template_id>\d+)", "DELETE", DELETE, "v3.9"),  # 删除公共流程
            ("/bk_sops/add_execute/", "POST", CREATE, "v3.9"),  # 公共流程设为告警自愈流程
            ("/bk_sops/delete_execute/", "POST", DELETE, "v3.9"),  # 公共流程取消设置告警自愈流程
        },
    },
}

# from utils.casbin_register_policy import casbin_policy
#
# POLICY_DICT = casbin_policy.policy()
