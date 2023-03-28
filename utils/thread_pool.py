from concurrent.futures import wait, ALL_COMPLETED
from concurrent.futures.thread import ThreadPoolExecutor
from django.conf import settings

from blueapps.core.exceptions import ServerBlueException
from utils.app_log import logger


class ThreadPool(object):
    def __init__(self, workers=None):
        self.max_workers = workers or int(settings.THREAD_POOL_MAX_WORKERS)
        self.result_list = []
        self.task_list = []
        self.is_error = False
        self.pool = self.create_thread_pool()

    def create_thread_pool(self):
        return ThreadPoolExecutor(max_workers=self.max_workers)

    def submit(self, *args, **kwargs):
        return self.pool.submit(*args, **kwargs)

    def handle_result(self, shit):
        # 捕获线程执行中的错误，并抛出到主线程
        shit_exception = shit.exception()
        if shit_exception:
            self.is_error = True
            logger.exception(shit_exception.message)
            raise ServerBlueException(shit_exception.message)
        else:
            result = shit.result()
            self.result_list.append({result["task_id"]: result["data"]})

    def add_task(self, task, *args):
        """添加异步任务"""
        task = self.pool.submit(task, *args)
        self.task_list.append(task)
        task.add_done_callback(self.handle_result)

    def wait(self):
        """等待任务执行完毕"""
        wait(self.task_list, return_when=ALL_COMPLETED)

    def wait_end(self):
        """等待任务执行完毕，并关闭线程池"""
        self.pool.shutdown(wait=True)

    def get_result(self, format_type=None):
        """获取任务结果"""
        if self.is_error:
            raise ServerBlueException("ThreadPool exist task error!")
        result = {}
        for data in self.result_list:
            result.update(data)
        if format_type == "dict":
            return result
        return result.values()

    def clear(self):
        """清除任务与任务结果"""
        self.result_list.clear()
        self.task_list.clear()
