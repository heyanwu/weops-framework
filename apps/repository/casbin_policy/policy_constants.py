# -- coding: utf-8 --

# @File : policy_constants.py
# @Time : 2023/2/27 11:31
# @Author : windyzhao
"""
casbin的policy常量定义
包括内容：
    页面app对应的url policy
    静态+动态的开放 url policy
"""
from constants.sys_manage_constants import COLLECT, CREATE, DELETE, MODIFY, QUERY, checkAuth, operateAuth

manageMyArticlesAuth = "manageMyArticlesAuth"  # 管理我的文章
manageAllArticlesAuth = "manageAllArticlesAuth"  # 管理所有文章
manageDeskArticlesAuth = "manageDeskArticlesAuth"  # 管理服务台文章

# 知识库操作
LORE_OPERATE = {
    ("/repository/", "POST", CREATE, "v3.9"),
    (r"/repository/(?P<pk>[^/.]+)/", "PUT", MODIFY, "v3.9"),
    (r"/repository/(?P<pk>[^/.]+)/", "DELETE", DELETE, "v3.9"),
    ("/repository/upload_repositories/", "POST", CREATE, "v3.10"),
    ("/repository/delete_images/", "POST", DELETE, "v3.10"),
    ("/repository/upload_image/", "POST", CREATE, "v3.10"),
    ("/repository/drafts/", "POST", CREATE, "v3.10"),
}

# 白名单
PASS_PATH = set()
# 动态白名单
MATCH_PASS_PATH = set()
# 权限policy
POLICY = {
    "lore": {
        checkAuth: {
            ("/repository/", "GET", QUERY, "v3.9"),
            ("/repository/labels/", "GET", QUERY, "v3.9"),
            ("/repository/templates/", "GET", QUERY, "v3.9"),
            (r"/repository/(?P<pk>[^/.]+)/repository_collect/", "POST", COLLECT, "v3.9"),
            (r"/repository/(?P<pk>[^/.]+)/repository_cancel_collect/", "POST", COLLECT, "v3.9"),
            ("/repository/get_images/", "POST", QUERY, "v3.10"),
            ("/repository/get_drafts/", "GET", QUERY, "v3.10"),
        },
        manageMyArticlesAuth: LORE_OPERATE,
        manageAllArticlesAuth: LORE_OPERATE,
        manageDeskArticlesAuth: {
            (r"/repository/(?P<pk>[^/.]+)/is_it_service/(?P<judge>.+?)/", "PATCH", COLLECT, "v3.9"),
        },
    },
    # 知识库模版管理
    "ArticleTemplateManage": {
        checkAuth: {
            ("/repository/templates/", "GET", QUERY, "v3.9"),
        },
        operateAuth: {
            ("/repository/templates/", "POST", CREATE, "v3.9"),
            (r"/repository/templates/(?P<pk>[^/.]+)/", "PUT", MODIFY, "v3.9"),
            (r"/repository/templates/(?P<pk>[^/.]+)/", "DELETE", DELETE, "v3.9"),
        },
    },
    # 知识库标签管理
    "ArticleTagManage": {
        checkAuth: {
            ("/repository/labels/", "GET", QUERY, "v3.9"),
        },
        operateAuth: {
            ("/repository/labels/", "POST", CREATE, "v3.9"),
            (r"/repository/labels/(?P<pk>[^/.]+)/", "PUT", MODIFY, "v3.9"),
            (r"/repository/labels/(?P<pk>[^/.]+)/", "DELETE", DELETE, "v3.9"),
        },
    },
}
