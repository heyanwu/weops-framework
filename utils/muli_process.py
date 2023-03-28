# -*- coding: utf-8 -*-
from functools import partial
from multiprocessing.pool import ThreadPool
from threading import Thread

from django import db
from django.utils import timezone, translation

from blueapps.utils.logger import logger
from utils.local import local


class MultiProcess(ThreadPool):
    @staticmethod
    def get_func_with_local(func):
        tz = timezone.get_current_timezone().zone
        lang = translation.get_language()
        items = [item for item in local]
        return partial(run_func_with_local, items, tz, lang, func)

    def map_ignore_exception(self, func, iterable, return_exception=False):
        """
        忽略错误版的map
        """
        futures = []
        for params in iterable:
            if not isinstance(params, (tuple, list)):
                params = (params,)
            futures.append(self.apply_async(func, args=params))

        results = []
        for future in futures:
            try:
                results.append(future.get())
            except Exception as e:
                if return_exception:
                    results.append(e)
                logger.exception(e)

        return results

    def map_async(self, func, iterable, chunksize=None, callback=None, error_callback=None):
        return super().map_async(
            self.get_func_with_local(func),
            iterable,
            chunksize=chunksize,
            callback=callback,
            error_callback=error_callback,
        )

    def apply_async(self, func, args=(), kwds=None, callback=None, error_callback=None):
        if kwds is None:
            kwds = {}
        return super().apply_async(
            self.get_func_with_local(func), args=args, kwds=kwds, callback=callback, error_callback=error_callback
        )

    def imap(self, func, iterable, chunksize=1):
        return super().imap(self.get_func_with_local(func), iterable, chunksize)

    def imap_unordered(self, func, iterable, chunksize=1):
        func = partial(run_func_with_local, func, local)
        return super().imap_unordered(self.get_func_with_local(func), iterable, chunksize)


def run_func_with_local(items, tz, lang, func, *args, **kwargs):
    """
    线程执行函数
    :param func: 待执行函数
    :param items: Thread Local Items
    :param tz: 时区
    :param lang: 语言
    :param args: 位置参数
    :param kwargs: 关键字参数
    :return: 函数返回值
    """
    # 同步local数据
    for item in items:
        setattr(local, item[0], item[1])

    # 设置时区及语言
    timezone.activate(tz)
    translation.activate(lang)

    try:
        data = func(*args, **kwargs)
    except Exception as e:
        logger.exception(e)
        raise e
    finally:
        # 关闭db连接
        db.connections.close_all()

        # 清理local数据
        for item in local:
            delattr(local, item[0])

    return data


class InheritParentThread(Thread):
    def __init__(self, *args, **kwargs):
        self.inherit_data = []
        for item in local:
            self.inherit_data.append(item)
        self.timezone = timezone.get_current_timezone().zone
        self.language = translation.get_language()
        super(InheritParentThread, self).__init__(*args, **kwargs)

    def sync(self):
        for sync_item in self.inherit_data:
            setattr(local, sync_item[0], sync_item[1])
        timezone.activate(self.timezone)
        translation.activate(self.language)

    @staticmethod
    def unsync():
        # 新的线程会往local再写一些数据
        # 线程结束的时候，需要把所有线程相关的所有变量都清空
        for item in local:
            delattr(local, item[0])

        # db._connections 也是线程变量，所以在线程结束的时候需要主动的释放
        db.connections.close_all()

    def run(self):
        self.sync()
        try:
            super(InheritParentThread, self).run()
        except Exception as e:
            logger.exception(e)

        self.unsync()


if __name__ == "__main__":
    InheritParentThread().start()
