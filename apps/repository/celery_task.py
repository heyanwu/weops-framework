# -*- coding: utf-8 -*-

# @File    : celery_task.py
# @Date    : 2022-04-25
# @Author  : windyzhao

from celery import task
from celery.schedules import crontab
from celery.task import periodic_task

from apps.repository.utils_package.minio_client import minio_client
from utils.app_log import celery_logger


@periodic_task(run_every=crontab(minute="0", hour="0", day_of_month="*"))
def rebuild_index_task():
    """
    当两次写入索引都失败时，启动celery去进行自动更新一次索引
    """

    celery_logger.info("==定时更新索引==")
    try:
        from apps.repository.controller import RepositoryController

        RepositoryController.rebuild()
    except BaseException as e:
        celery_logger.exception("celery 手动更新索引失败:{}".format(e))

    celery_logger.info("==定时更新索引结束==")


# @periodic_task(run_every=crontab(minute="0", hour="*/1", day_of_month="*"))
# def every_day_update_classifications_group():
#     # 更新模型分组
#     sys_setting.CLASSIFICATIONS_GROUP = Menus.get_menus_classification_list()
#     celery_logger.info("--定时更新模型分组--")

# menu_ids_queryset = SysApps.objects.filter(app_key=DB_MENU_IDS)
# update_list = []
# for menu_id_queryset in menu_ids_queryset:
#     app_key = menu_id_queryset.app_key
# menu_id_queryset.app_key = [for i in app_key if ]


@task
def async_delete_minio_images(bucket_name, images):
    """
    批量删除minio图片
    """
    res = minio_client.remove_objects(bucket_name=bucket_name, objects_iter=images)
    celery_logger.info("批量删除图片. bucket_name={},objects_iter={}, res={}".format(bucket_name, images, res))
