import sqlite3
import os
import time
import traceback
from utility.debug import *

class uDatabase:
    __db_lock = False
    def __init__(self, db_path='udb.db'):
        dbg_trace("Create database instance")
        self.__db_path=db_path
        self.__db_connection = None
        self.__cursor = None
    def __lock(self):
        timeout_cnt=1000
        # dbg_debug('Get mutex ', self.__db_lock)
        while self.__db_lock is True:
            time.sleep(0.05)
            dbg_trace("Try to get mutex.")
            if timeout_cnt == 0:
                return False
            else:
                timeout_cnt -= 1

        self.__db_lock = True
        return True
    def __unlock(self):
        # dbg_debug('Release mutex ', self.__db_lock)
        if self.__db_lock is False:
            dbg_warning("Mutex is not locking")
        self.__db_lock = False
        return True

    def setup(self):
        query_str = """
                    SELECT name FROM sqlite_schema
                    WHERE type ='table' AND name NOT LIKE 'sqlite_%';
                    """
        # dbg_debug(query_str)
        table_list = self.execute(query_str)
        if not os.path.isfile(self.__db_path) or len(table_list) == 0:
            dbg_info("Initiialize database")

             # c.execute('''CREATE TABLE PROJECT
             #              (PID TEXT, Name CHAR(255), Description VARCHAR , StartDate date)''')

            # Create table
            # query_str='''CREATE TABLE UDB (
            #                 ID INTEGER AUTO_INCREMENT,
            #                 Operation TEXT,
            #                 Description VARCHAR,
            #                 Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            #                 )
            #           '''
            query_str='''CREATE TABLE UDB (
                            ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            Operation TEXT,
                            Description VARCHAR,
                            Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                            )
                      '''

            self.execute(query_str)

            # Insert a row of data
            query_str = "INSERT INTO UDB (Operation, Description) VALUES ('%s', '%s')" % ("Setup Database", "Create Database, and setup up udb table.")
            self.execute(query_str)


        return True
    def connect(self):
        dbg_trace("Connect to database")
        if self.__lock() is False:
            dbg_error("Database get lock fail!")
            return False
        if self.__db_connection is None:
            self.__db_connection = sqlite3.connect(self.__db_path)
            self.__cursor = self.__db_connection.cursor()
            self.__unlock()
            return True
        else:
            dbg_warning("Database is already connected!")
            self.__unlock()
            return True
    def close(self):
        self.commit()
        if self.__lock() is False:
            dbg_error("Database get lock fail!")
            return False
        if self.__db_connection is None:
            # print('there is nothing to do!')
            self.__unlock()
            return True
        else:
            self.__db_connection.close()
            self.__unlock()
            return True
    def commit(self):
        if self.__lock() is False:
            dbg_error("Database get lock fail!")
            return False
        dbg_trace("Database commit")
        self.__db_connection.commit()
        self.__unlock()
        return True
    def execute(self, query_str, fetchone=False):
        if self.__lock() is False:
            dbg_error("Database get lock fail!")
            return False
        dbg_debug("Query String: ", query_str)

        try:
            result = self.__cursor.execute(query_str)
            # if result is None:
            #     dbg_warning('Result is empty')
            if fetchone is True:
                result = result.fetchone()
            else:
                result = result.fetchall()
            dbg_debug(result)
        except Exception as e:

            dbg_error("Query String: ", query_str)
            dbg_error("Exception: ", e)

            traceback_output = traceback.format_exc()
            dbg_error(traceback_output)


        self.__unlock()
        return result

    def dump_db(self):

        query_str = """
                    SELECT name FROM sqlite_schema
                    WHERE type ='table' AND name NOT LIKE 'sqlite_%';
                    """
        # dbg_debug(query_str)

        table_list = self.execute(query_str)
        dbg_info(table_list)


        return table_list
    def dump_table(self, table, cnt=10):
        query_str = "SELECT * from %s;" % table
        # query_str = "PRAGMA table_info(%s);" % table
        # query_str = ".schema tablename"
        # dbg_debug(query_str)
        data_list = self.execute(query_str)
        dbg_info(data_list)

        return data_list
    def dump_all(self, cnt=10):
        table_list = self.dump_db()
        for each_table in table_list:
            self.dump_table(each_table)
    # def example(self):
    #     query_str = "SELECT times, familiar FROM WORD WHERE word == '%s'" % word
    #     query_str = "%s WHERE times == %i AND familiar == %i" % (query_str, times, familiar)
    #     query_str = "UPDATE WORD SET times = %i, familiar = %i WHERE word == '%s'" % (result[0] + times, result[1] + familiar, word)
    #     query_str = "INSERT INTO WORD (word, times, familiar) VALUES ('%s', %i, %i)" % (word, 1, familiar)

if __name__ == '__main__':
    DebugSetting.debug_level = DebugLevel.MAX
    print("Test uDB ")
    test = uDatabase()
    test.connect()
    test.setup()
    # test.insert('test')
    # print(test.update('test', 1))
    # print(test.quer_for_all_word())
    # table_list = test.dump_db()
    # test.dump_table(table_list[0])
    test.dump_all()

    test.close()
