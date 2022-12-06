APP_ID = ""
APP_TOKEN = ""
RUN_VER = "open"
BK_URL = ""
BK_PAAS_HOST = ""
BK_PAAS_INNER_HOST = ""
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "",  # noqa
        "USER": "root",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "3306",
        # 单元测试 DB 配置，建议不改动
        "TEST": {"NAME": "test_db", "CHARSET": "utf8", "COLLATION": "utf8_general_ci"},
    },
}
BROKER_URL = 'amqp://guest:guest@localhost:5672//'
