import requests
from django.conf import settings
from django.db import connection
from MySQLdb._mysql import DatabaseError
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
