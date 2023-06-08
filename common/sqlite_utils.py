import sqlite3
import time

from sqlite3 import Error

from SSLScan_UI.common.log import log


class SqliteUtils:
    def __init__(self):
        self.db_name = '../conf/time_consuming.db'
        self.con = self.sql_connection()
        self.cursorObj = self.con.cursor()
        # self.ini_db()

    def sql_connection(self):
        try:
            con = sqlite3.connect(self.db_name)
            return con
        except Error:
            log.info(Error)

    def sql_table(self):
        self.cursorObj.execute(
            "CREATE TABLE time_consuming(datetime char, website char, ca char, time_consuming integer)")
        self.con.commit()

    def ini_db(self):
        try:
            con = self.sql_connection()
            self.sql_table()
            log.info(f'create table time_consuming')
        except sqlite3.OperationalError:
            log.info(f'table time_consuming already exists')

    def set_time_consuming(self, data):
        self.cursorObj.execute("INSERT INTO time_consuming VALUES(?, ?, ?, ?)", data)
        self.con.commit()
        self.cursorObj.close()
        self.con.close()

    def get_time_consuming(self, website):
        self.cursorObj.execute(f"SELECT * FROM time_consuming where website = '{website}'")

        rows = self.cursorObj.fetchall()
        self.cursorObj.close()
        self.con.close()

        # print(rows)
        # for row in rows:
        #     print(row)
        return rows

    def get_time_consuming_all(self):
        self.cursorObj.execute(f"SELECT * FROM time_consuming")

        rows = self.cursorObj.fetchall()
        # log.info(f'sqlite查询结果为：{rows}')
        self.cursorObj.close()
        self.con.close()

        return rows

    def clear_time_consuming(self):
        log.info('==========清除缓存==========')
        self.cursorObj.execute("DELETE FROM time_consuming")
        self.con.commit()
        self.cursorObj.close()
        self.con.close()

    def close_con_cursor(self):
        self.con.close()
        self.cursorObj.close()


if __name__ == '__main__':
    print(len(SqliteUtils().get_time_consuming_all()))
