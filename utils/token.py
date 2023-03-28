import requests
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from MySQLdb import DatabaseError
from MySQLdb.cursors import DictCursor

from utils.app_log import logger


def generate_bk_token(username="admin"):
    """
    生成用户的登录态
    """
    try:
        url = f"{settings.BK_PAAS_HOST}/login/custom/get_user_bk_token/?username={username}"
        resp = requests.get(url=url, verify=False).json()
        return resp["data"]["bk_token"], resp["data"]["expire_time"]
    except Exception as e:
        logger.exception(e)
        return None, 0


def set_bk_token_to_cache(bk_token):
    # 两个小时自动过期
    cache.set("bk_token", bk_token, 60 * 60 * 2)


def set_bk_token_to_open_pass_db(bk_token, expire_time):
    """将token写入open_pass_db"""
    sql = f"""INSERT INTO
login_bktoken
(token, is_logout, inactive_expire_time)
VALUES ('{bk_token}', 0, {expire_time})
"""
    db_config = connection.get_connection_params()
    db_config.update(db="open_paas")
    con = connection.get_new_connection(db_config)
    cursor = con.cursor(DictCursor)
    try:
        cursor.execute(sql)
        con.commit()
    except DatabaseError as e:
        logger.exception(e)
    cursor.close()
    con.close()


def get_bk_token():
    bk_token = cache.get("bk_token")
    if not bk_token:
        bk_token = set_bk_token()
    return bk_token


def set_bk_token():
    # 生成token
    bk_token, expire_time = generate_bk_token()
    # bk_token为空时，不进行存库和缓存操作
    if not bk_token:
        logger.warning("bk_token 初始化设置失败！")
        return None
    # token入库
    set_bk_token_to_open_pass_db(bk_token, expire_time)
    # token放入缓存
    set_bk_token_to_cache(bk_token)

    return bk_token
