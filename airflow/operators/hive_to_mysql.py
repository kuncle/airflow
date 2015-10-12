import logging

from airflow.hooks import HiveServer2Hook, MySqlHook
from airflow.models import BaseOperator
from airflow.utils import apply_defaults

from tempfile import NamedTemporaryFile

class HiveToMySqlTransfer(BaseOperator):
    """
    Moves data from Hive to MySQL, note that for now the data is loaded
    into memory before being pushed to MySQL, so this operator should
    be used for smallish amount of data.
    :param sql: SQL query to execute against the MySQL database
    :type sql: str
    :param mysql_table: target MySQL table, use dot notation to target a
        specific database
    :type mysql_table: str
    :param mysql_conn_id: source mysql connection
    :type mysql_conn_id: str
    :param hiveserver2_conn_id: destination hive connection
    :type hiveserver2_conn_id: str
    :param mysql_preoperator: sql statement to run against mysql prior to
        import, typically use to truncate of delete in place of the data
        coming in, allowing the task to be idempotent (running the task
        twice won't double load data)
    :type mysql_preoperator: str
    :param mysql_postoperator: sql statement to run against mysql after the
        import, typically used to move data from staging to production
        and issue cleanup commands.
    :type mysql_postoperator: str
    :param bulk_load: flag to use bulk_load option.  This loads mysql directly
        from a tab-delimited text file in a single statement.
    :type bulk_load: bool
    """

    template_fields = ('sql', 'mysql_table', 'mysql_preoperator',
        'mysql_postoperator')
    template_ext = ('.sql',)
    ui_color = '#a0e08c'

    @apply_defaults
    def __init__(
            self,
            sql,
            mysql_table,
            hiveserver2_conn_id='hiveserver2_default',
            mysql_conn_id='mysql_default',
            mysql_preoperator=None,
            mysql_postoperator=None,
            bulk_load = False,
            *args, **kwargs):
        super(HiveToMySqlTransfer, self).__init__(*args, **kwargs)
        self.sql = sql
        self.mysql_table = mysql_table
        self.mysql_conn_id = mysql_conn_id
        self.mysql_preoperator = mysql_preoperator
        self.mysql_postoperator = mysql_postoperator
        self.hiveserver2_conn_id = hiveserver2_conn_id
        self.bulk_load = bulk_load

    def execute(self, context):
        hive = HiveServer2Hook(hiveserver2_conn_id=self.hiveserver2_conn_id)
        logging.info("Extracting data from Hive")
        logging.info(self.sql)

        if self.bulk_load:
            tmpfile = NamedTemporaryFile()
            hive.to_csv(self.sql, tmpfile.name)
        else:
            results = hive.get_records(self.sql)

        mysql = MySqlHook(mysql_conn_id=self.mysql_conn_id)
        if self.mysql_preoperator:
            logging.info("Running MySQL preoperator")
            mysql.run(self.mysql_preoperator)

        logging.info("Inserting rows into MySQL")


        if self.bulk_load:
            mysql.bulk_load(table=self.mysql_table, tmp_file=tmpfile.name)
            tmpfile.close()
        else:
            mysql.insert_rows(table=self.mysql_table, rows=results)

        if self.mysql_postoperator:
            logging.info("Running MySQL postoperator")
            mysql.run(self.mysql_postoperator)

        logging.info("Done.")
