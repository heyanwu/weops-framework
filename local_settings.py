# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.mysql",
#         "NAME": "bot_db",  # noqa
#         "USER": "root",
#         "PASSWORD": "1",
#         "HOST": "localhost",
#         "PORT": "3306",
#         # 单元测试 DB 配置，建议不改动
#         "TEST": {"NAME": "bot_db", "CHARSET": "utf8", "COLLATION": "utf8_general_ci"},
#     },
# }
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "weops_saas",  # noqa  数据库名
        "HOST": "10.10.26.237",  # noqa  数据库主机
        "USER": "root",  # noqa  数据库用户
        "PASSWORD": "jIUxdSqwQJss",  # noqa  数据库密码
        "PORT": 3306,  # noqa  数据库端口号
        'OPTIONS': {
            'init_command': 'SET sql_mode="STRICT_TRANS_TABLES"',
        },
        # 单元测试 DB 配置，建议不改动
        "TEST": {"NAME": "test_db", "CHARSET": "utf8", "COLLATION": "utf8_general_ci"},
    },
}

APP_TOKEN = "7297613c-de40-477a-b13c-f86b3cc3cb99"
APP_CODE = "weops_saas"






