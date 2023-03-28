from django.utils.deprecation import MiddlewareMixin

from utils.locals import set_current_request


class RequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_current_request(request)
        response = self.get_response(request)
        return response


class CrossCSRF4WEOPS(MiddlewareMixin):
    @staticmethod
    def process_request(request):
        # weops微前端定义得参数为AUTH-APP
        auth_app = request.META.get("HTTP_AUTH_APP")
        # 当自定义参数为"WEOPS"时，豁免csrf验证
        if auth_app and auth_app == "WEOPS":
            setattr(request, "_dont_enforce_csrf_checks", True)
