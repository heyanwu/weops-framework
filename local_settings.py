DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "bot",  # noqa
        "USER": "root",
        "PASSWORD": "1",
        "HOST": "localhost",
        "PORT": "3306",
        # 单元测试 DB 配置，建议不改动
        "TEST": {"NAME": "bot_db", "CHARSET": "utf8", "COLLATION": "utf8_general_ci"},
    },
}





