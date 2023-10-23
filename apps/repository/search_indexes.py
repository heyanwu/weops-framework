# -*- coding: utf-8 -*-

# @File    : search_indexes.py
# @Date    : 2022-03-31
# @Author  : windyzhao
from haystack import indexes  # 导入索引

from apps.repository.celery_task import rebuild_index_task
from apps.repository.models import Repository  # 导入模型
from utils.app_log import logger


# RepositoryIndex是固定格式命名，Repository是你models.py中的类名
class RepositoryIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    repository_id = indexes.IntegerField(model_attr="id")
    content = indexes.CharField(model_attr="content")
    title = indexes.CharField(model_attr="title")
    created_by = indexes.CharField(model_attr="created_by")

    def get_model(self):
        return Repository

    def index_queryset(self, using=None):
        # 把草稿箱的文章过滤掉
        return self.get_model().objects.filter(drafts=False).prefetch_related("labels")

    def update_object(self, instance, using=None, **kwargs):
        if self.should_update(instance, **kwargs):
            backend = self.get_backend(using)
            if not backend:
                return
            res = backend.update(self, [instance])
            if not res:
                return

            logger.info("第一次更新索引失败，开始从新更新索引--")
            again_res = backend.update(self, [instance])
            logger.info("第二次更新索引结束，新更新索引{}--".format("失败" if again_res else "成功"))

            if again_res:
                # 再次更新索引也失败时  走celery
                rebuild_index_task.delay()
