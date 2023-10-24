import datetime
import json
import os
import re

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from apps.system_mgmt.casbin_package.permissions import get_user_roles
from apps.system_mgmt.constants import MENUS_MAPPING
from apps.system_mgmt.models import MenuManage
from django.apps import apps

def get_init_data():
    init_data = {
        "email": os.getenv("BKAPP_ESB_EMAIL", "326"),
        "sms": os.getenv("BKAPP_ESB_SMS", "408"),
        "voice": os.getenv("BKAPP_ESB_VOICE", "325"),
        "weixin": os.getenv("BKAPP_ESB_WEIXIN", "328"),
        "remote_url": os.getenv("BKAPP_REMOTE_URL", "http://paas.weops.com/o/views/connect"),
        "is_activate": 1,
        "log_output_host": os.getenv("BKAPP_LOG_OUTPUT_HOST", "127.0.0.1:8000"),  # log输出地址
    }
    return init_data


def duplicate_removal_operate_ids(operate_ids):
    operate_dict = {}
    for operate in operate_ids:
        menu_id, operates = operate["menuId"], operate["operate_ids"]
        if menu_id not in operate_dict:
            operate_dict[menu_id] = []
        operate_dict[menu_id].extend(operates)

    return [{"menuId": menu_id, "operate_ids": list(set(operates))} for menu_id, operates in operate_dict.items()]

@require_GET
def login_info(request):
    pattern = re.compile(r"weops_saas[-_]+[vV]?([\d.]*)")
    version = [i.strip() for i in pattern.findall(os.getenv("FILE_NAME", "weops_saas-3.5.3.tar.gz")) if i.strip()]


    user_super, _, user_menus, chname, operate_ids = get_user_roles(request.user)
    notify_day = 30
    expired_day = 365

    app_list = apps.get_app_configs()
    applications = []
    for app in app_list:
        if app.name.startswith("apps."):
            app.name = app.name.replace("apps.", '')
            applications.append(app.name)
        elif app.name.startswith("apps_other."):
            app.name = app.name.replace("apps_other.", '')
            applications.append(app.name)

    # activation_obj = Activation.objects.first()
    # if activation_obj is None:
    #     raise Activation.DoesNotExist("WeOps未激活！")
    #
    # expiration_date = datetime.datetime.strptime(activation_obj.expiration_date, "%Y-%m-%d").date()
    #
    # if datetime.datetime.now().date() > expiration_date:
    #     user_super, _, user_menus, chname, operate_ids = get_user_roles(request.user, False)
    #     notify_day = 0
    #     expired_day = 0
    #     applications = []
    #
    # else:
    #     user_super, _, user_menus, chname, operate_ids = get_user_roles(request.user)
    #     notify_day = activation_obj.notify_day
    #     applications = activation_obj.applications
    #     expired_day = (expiration_date - datetime.datetime.now().date()).days
    # 去重user_menus
    user_menus = list(set(user_menus))
    # 去重operate_ids
    operate_ids = duplicate_removal_operate_ids(operate_ids)

    # 启用的菜单
    menu_instance = MenuManage.objects.filter(use=True).first()
    weops_menu = menu_instance.menu if menu_instance else []

    return JsonResponse(
        {
            "result": True,
            "data": {
                "weops_menu": weops_menu,
                "username": request.user.username,
                "applications": applications or list(MENUS_MAPPING.keys()),  # weops有的权限
                "is_super": user_super,
                "menus": user_menus,
                "chname": chname,
                "operate_ids": operate_ids,
                "role": request.user.role,
                "last_login_addr": request.user.get_property("last_login_addr") or "",
                "last_login": request.user.last_login.strftime("%Y-%m-%d %H:%M"),
                "bk_token": request.COOKIES.get("bk_token", ""),
                "version": version[0].strip(".") if version else "3.5.3",
                "expired_day": expired_day,
                "notify_day": notify_day,
            },
        }
    )