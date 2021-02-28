import sqlite3

class DatabaseManager:
    '''
        Database Manager
        Special thanks to: https://cppsecrets.com/users/110711510497115104971101075756514864103109971051084699111109/Python-SQLite-Check-If-Database-Exists-or-Not.php
    '''

    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None

    def check_database(self, log):
        # log.info(self.conn)
        if self.conn == None:
            try:
                self.conn = sqlite3.connect(self.db_name, uri=True, check_same_thread=False)
                log.info(f'Succesfully connected to {self.db_name} database.')

                if self.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='words';") != 'words':
                    self.execute("CREATE TABLE IF NOT EXISTS words (word TEXT PRIMARY KEY)")
                    log.info(f'Created "words" table because it did not exist.')

            except sqlite3.OperationalError as err:
                log.error(f'Error: {err}')

            finally:
                return False

        # log.info(self.count_words())
        return True

    def count_words(self):
        return self.execute("SELECT COUNT(*) FROM words")[0][0]

    def close_connection(self):
        if self.conn is not None:
            self.conn.close()

    def execute(self, sql_string):
        cursorObj = self.conn.cursor()
        cursorObj.execute(sql_string)
        self.conn.commit()

        return cursorObj.fetchall()
