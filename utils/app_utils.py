class AppUtils(object):
    def __init__(self):
        pass

    @staticmethod
    def interface_call(app_model, app_fun, kwargs):
        m = __import__(app_model, globals(), locals(), ["*"])
        method = getattr(m, app_fun, False)
        if method:
            return method(**kwargs)

    @staticmethod
    def class_call(app_model, class_name, app_fun, class_kwargs, fun_kwargs):
        m = __import__(app_model, globals(), locals(), ["*"])
        cls = getattr(m, class_name, False)
        if not cls:
            return
        cls_inst = cls(**class_kwargs)
        method = getattr(cls_inst, app_fun, False)
        if method:
            return method(**fun_kwargs)

    @staticmethod
    def static_class_call(app_model, class_name, app_fun, *fun_args, **fun_kwargs):
        m = __import__(app_model, globals(), locals(), ["*"])
        cls = getattr(m, class_name, False)
        if not cls:
            return
        method = getattr(cls, app_fun, False)
        if method:
            return method(*fun_args, **fun_kwargs)

    @staticmethod
    def get_model(app_path, model_name):
        m = __import__(app_path, globals(), locals(), ["*"])
        model = getattr(m, model_name, None)
        return model


# from common.app_utils import AppUtils
# utils = AppUtils()
# utils.interface_call('home_application.views', 'check_activation', {})
# utils.class_call(
# "home_application.credential_mgmt.vault_cred_helper",
# 'CredUtils',
# 'search_biz_hosts',
# {"cookies": None},
# {"biz_ids": [2],
# "is_super":True}
# )
