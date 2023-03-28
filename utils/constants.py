# -*- coding: utf-8 -*-

# 数据库初始化 管理员列表
import os

ADMIN_USERNAME_LIST = ["admin"]

# 蓝鲸用户每页个数最大值
BK_USER_MAX_PAGE_SIZE = 2000

# 业务下主机限制个数
BK_CC_BIZ_HOSTS_LIMIT_NUMBER = 500

# 默认缓存的过期时间
DEFAULT_CACHE_TTL = int(os.getenv("BKAPP_DEFAULT_CACHE_TTL", 5 * 60))

# 无穷大的每页个数(请求所有数据)
PAGE_SIZE_INFINITE_NUM = -1

# 列表数据最大限制个数
LIST_MAX_LIMIT_NUM = 200

LIST_BIZ_HOSTS_MAX_NUM = 200
SEARCH_INST_MAX_NUM = 200
SEARCH_BUSINESS_MAX_NUM = 200
LIST_OPERATION_AUDIT_MAX_NUM = 200
# 获取工单最大个数
SEARCH_WORK_ORDER_MAX_NUM = 100
# 查询agent最大数量
SEARCH_AGENT_MAX_NUM = 10000

# 作业状态码
JOB_STATUS_SUCCESS = 3  # 执行成功

IP_STATUS_SUCCESS = 9  # 主机任务状态码,5.等待执行; 7.正在执行; 9.执行成功; 11.任务失败;

OS_TYPE_MAPPING = {"Linux": "1", "Windows": "2"}

RESOURCE_POOL_BIZ_ID_LIST = [1]  # 资源池业务id

OPERATION_CODE_STOP_JOB = 1  # 操作作业实例之停止作业

OPERATION_CODE_STOP_JOB_ERROR = 1241003  # 不支持的操作,当去停止 已经执行完成/执行失败 的任务时，会返回此状态码

AGENT_STATUS_NAME = {
    "RUNNING": "正常",
    "TERMINATED": "异常",
    "NOT_INSTALLED": "未安装",
    "UNKNOWN": "未知",
}
