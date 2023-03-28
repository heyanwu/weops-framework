# -*- coding: utf-8 -*-
import json

from djcelery.models import CrontabSchedule, PeriodicTask

from utils.app_log import celery_logger


def cycle_task_create_or_update(name, crontab, args, task):
    """创建或更新周期任务"""
    celery_logger.info("创建或更新周期任务：{}、crontab：{}、arags：{}、task：{}".format(name, crontab, args, task))
    minute, hour, day, month, week = crontab.split()
    kwargs = dict(minute=minute, hour=hour, day_of_week=week, day_of_month=day, month_of_year=month)
    crontab, _ = CrontabSchedule.objects.get_or_create(**kwargs, defaults=kwargs)
    defaults = dict(
        crontab=crontab,
        name=name,
        task=task,
        enabled=True,
        args=json.dumps(args),
    )
    PeriodicTask.objects.update_or_create(name=name, defaults=defaults)


def delete_cycle_task(name):
    """删除周期任务"""
    celery_logger.info("删除周期任务：{}!".format(name))
    PeriodicTask.objects.filter(name=name).delete()
