# -- coding: utf-8 --

# @File : policy_constants.py
# @Time : 2023/3/10 15:37
# @Author : windyzhao
from constants.sys_manage_constants import CREATE, DELETE, MODIFY, QUERY, checkAuth, operateAuth

PASS_PATH = {
    ("/itsm/", "GET"),
    ("/appWallScreen/", "GET"),
    ("/login_info/", "GET"),
    ("/get_flow_count/", "GET"),
    ("/open_api/user/get_user_role/", "GET"),
    ("/get_admins/", "GET"),
    ("/init_monitor_obj/", "GET"),
    ("/verify_user_auth/", "GET"),
    ("/get_application_overview/", "GET"),
    ("/create_remote_log/", "GET"),
    ("/get_biz_list/", "GET"),
    ("/open_api/get_biz_resource_top/", "GET"),
    ("/open_api/get_biz_resource_summary/", "GET"),
    ("/open_api/get_biz_alarm_summary/", "GET"),
    ("/open_api/get_esxi_summary/", "GET"),
    ("/open_api/get_cloud_monitor_summary/", "GET"),
    ("/open_api/get_cmdb_resource_summary/", "GET"),
    ("/open_api/get_monitor_top/", "GET"),
    ("/open_api/create_obj_and_group/", "GET"),
    ("/open_api/get_k8s_inst_id/", "GET"),
    ("/open_api/get_k8s_workload_id/", "GET"),
    ("/version_log/version_logs_list/", "GET"),
    ("/version_log/version_log_detail/", "GET"),
}

POLICY = {
    "RemoteVoucher": {
        checkAuth: {
            ("/cred_design/get_cred_params/", "GET", QUERY, "v3.12"),
            ("/vault_credential/", "GET", QUERY, "v3.12"),
            (r"/vault_credential/(?P<pk>[^/.]+)/get_cred_detail/", "GET", QUERY, "v3.12"),
            (r"/vault_credential/(?P<pk>[^/.]+)/get_resource_list/", "GET", QUERY, "v3.12"),
            (r"/vault_credential/(?P<pk>[^/.]+)/get_vault_cred_detail/", "GET", QUERY, "v3.12"),
            ("/system/mgmt/role_manage/search_role_list/", "GET", QUERY, "v3.10"),
            ("/system/mgmt/user_manage/search_user_list/", "GET", QUERY, "v3.10"),
        },
        operateAuth: {
            ("/vault_credential/", "POST", CREATE, "v3.12"),
            (r"/vault_credential/(?P<pk>[^/.]+)/", "PUT", MODIFY, "v3.12"),
            (r"/vault_credential/(?P<pk>[^/.]+)/", "DELETE", DELETE, "v3.12"),
            (r"/vault_credential/(?P<pk>[^/.]+)/set_resource_list/", "POST", MODIFY, "v3.12"),
            (r"/vault_credential/(?P<pk>[^/.]+)/set_auth_list/", "POST", MODIFY, "v3.12"),
        },
    },
}
