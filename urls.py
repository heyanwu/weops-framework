# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import os

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r"^admin/", admin.site.urls),
    url(r"^account/", include("blueapps.account.urls")),
    # 如果你习惯使用 Django 模板，请在 home_application 里开发你的应用，
    # 这里的 home_application 可以改成你想要的名字
    url(r"^", include("base_index.urls")),
    # 如果你习惯使用 mako 模板，请在 mako_application 里开发你的应用，
    # 这里的 mako_application 可以改成你想要的名字
    url(r"^i18n/", include("django.conf.urls.i18n")),
]
apps = {
    "apps": os.listdir("apps"),
    "apps_other": os.listdir("apps_other")
}
for key, app_list in apps.items():
    dir_list = [i for i in app_list if not (i.startswith("__") or i.startswith(".")) and i not in ["system_mgmt"]]
    for i in dir_list:
        urlpatterns.append(url(r"^{}/".format(i), include(f"{key}.{i}.urls")))  # noqa

if settings.RUN_MODE == "DEVELOP":
    """
    开发时添加SWAGGER API DOC
    访问地址: http://dev.cwbk.com:8000/docs/
    """
    from rest_framework_swagger.views import get_swagger_view

    schema_view = get_swagger_view(title="%s API" % settings.APP_ID.upper())
    urlpatterns += [url(r"^docs/$", schema_view)]

try:
    from custom_urls import urlpatterns as custom_url

    urlpatterns += custom_url
except ImportError:
    pass
