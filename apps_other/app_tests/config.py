app_name = "app_test"

celery_tasks = ("apps_other.app_test.celery_tasks",)

add_middleware = (
    "apps_other.app_test.middleware.TestMiddleware",
)

APP_TEST_ID = 1