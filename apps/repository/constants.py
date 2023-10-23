# -*- coding: utf-8 -*-

# @File    : constants.py
# @Date    : 2022-04-08
# @Author  : windyzhao

import os

from django.conf import settings

# 我的文章
SEARCH_TYPE_USER = "user"
# 我的收藏
SEARCH_TYPE_COLLECT = "collect"

SEARCH_TYPE_ALL = "all"

# 空白模版 template_img
BLANK_TEMPLATE_NAME = "空白模版"
BLANK_TEMPLATE_DATA = {"template_name": BLANK_TEMPLATE_NAME, "body": []}

# Minio图片的upload_to
REPOSITORY_BUCKET_NAME = settings.REPOSITORY_BUCKET  # 知识库桶的名称
TEMPLATE_UPLOAD_TO = "template"  # 知识库模版路径
REPOSITORY_UPLOAD_TO = "repository"  # 知识库图片路径

# 上传word,txt到知识库到常量

# 执行命令
EXEC_LINE = "pandoc  -t gfm --extract-media {} -o {} {}"
if not settings.DEBUG:
    EXEC_LINE = "./" + EXEC_LINE

BASE_PATH = settings.CURRENT_FILE_PATH  # 文件暂存地址
SAVE_IMAGE_DIR = os.path.join(BASE_PATH, "images")  # 存储图片文件夹
FILE_TYPE = {".docx", ".doc"}  # 允许转换的文件类型
TXT_TYPE = ".txt"  # txt文档
TEMPLATE_BODY = {
    "type": "markDown",
    "name": "MarkDown",
    "id": "",  # uuid生成
    "isEdit": False,
    "mdConfigs": {"editable": False, "autofocus": False, "subfield": False, "toolbarsFlag": True},
    "content": "",  # 内容
    "html": "",
    "height": "",
    "icon": "cw-icon-markdown",
    "isError": False,
    "message": "内容不能为空！",
}
