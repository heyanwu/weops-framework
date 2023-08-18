from django.apps import AppConfig

app_name = "apps_other.app_bot"


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps_other.app_bot'
    verbose_name = '机器人--语料管理'  # 设置 app 名称为中文