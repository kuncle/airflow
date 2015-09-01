import MySQLdb

from airflow.hooks.dbapi_hook import DbApiHook


class MySqlHook(DbApiHook):
    '''
    Interact with MySQL.
    '''

    conn_name_attr = 'mysql_conn_id'
    default_conn_name = 'mysql_default'
    supports_autocommit = True

    def get_conn(self):
        """
        Returns a mysql connection object
        """
        conn = self.get_connection(self.mysql_conn_id)
        port = conn.port or '3306'
        conn = MySQLdb.connect(
            host=conn.host,
            port=port,
            user=conn.login,
            passwd=conn.password,
            db=conn.schema)
        return conn
