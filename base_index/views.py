from django.shortcuts import render
from utils.app_utils import AppUtils


def home(request):
    """
    首页
    """
    utils = AppUtils()
    init_data = utils.interface_call('home_application.views', 'get_init_data', {})
    response = render(request, "index.prod.html", init_data)
    response.set_cookie("current_ip", getattr(request, "current_ip", "127.0.0.1"), httponly=True)
    return response


