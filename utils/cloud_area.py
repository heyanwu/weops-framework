# -*- coding: utf-8 -*-

# @File    : cloud_area.py
# @Date    : 2022-02-28
# @Author  : windyzhao


class BkCloudAreaUtils(object):
    """
    cmdb 云区域接口工具
    """

    @staticmethod
    def search_cloud_area(client, page=None, condition=None):
        if page is None:
            page = {}
        start = 0
        limit = 200
        count = 0
        data = []
        content = {"page": page}
        if condition:
            content["condition"] = condition

        while True:
            if count > 10000:
                break
            count += 1
            content["page"]["start"] = start
            content["page"]["limit"] = limit
            res = client.cc.search_cloud_area(content)
            if res["result"]:
                res_data = res["data"]["info"]
                data.extend(res_data)
                if len(res_data) > 0:
                    start += limit
                else:
                    break
            else:
                break

        return data
