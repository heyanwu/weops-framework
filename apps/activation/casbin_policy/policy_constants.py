# -- coding: utf-8 --

# @File : policy_constants.py
# @Time : 2023/3/8 16:46
# @Author : windyzhao


PASS_PATH = {
    ("/activation/get_applications/", "GET"),
    ("/activation/get_sys_info/", "GET"),
    ("/activation/check_node_nums/", "GET"),
    ("/activation/get_sys_info/", "GET"),
    ("/activation/get_applications/", "GET"),
    ("/activation/reset_activation/", "GET"),
    ("/activation/check_activation/", "GET"),
    ("/activation/set_expired_notify_day/", "POST"),
    ("/activation/", "GET"),
    ("/activation/", "PUT"),
}
MATCH_PASS_PATH = set()
