from utils.sql_utils import SQLClient


class UsermgmtSQLUtils(SQLClient):
    def __init__(self, db_name="bk_user"):
        super().__init__(db_name)

    def get_domain(self):
        sql = "SELECT domain FROM categories_profilecategory WHERE enabled = 1 AND `status` = 'normal' order by `default` desc"  # noqa
        result = self.execute_mysql_sql(sql)
        return [i["domain"] for i in result]
