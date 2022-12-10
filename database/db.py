import sqlite3
import time
from sqlite3 import Error
import logging
import os
import pathlib


class Database:

    def __init__(self):
        # logging.basicConfig(
        #     level=logging.DEBUG,
        #     format="%(asctime)s [%(levelname)s] %(message)s",
        #     datefmt='%Y-%m-%d %H:%M:%S',
        #     handlers=[
        #         logging.FileHandler("aquarium_log.log"),
        #         logging.StreamHandler()
        #     ]
        # )
        self.__connection = self.__get_connection()
        self.__cursor = self.__get_cursor()
        self.__que = []
        self.__retry_counter = 0
        self.__make_migrations()
        self.__lock = False

    def __make_migrations(self):
        done_migrations = []
        try:
            fetch = self.__cursor.execute("SELECT migration FROM info").fetchall()
            for migration in fetch:
                done_migrations.append(migration[0])
        except:
            pass
        migration_scripts_path = os.path.join(os.path.dirname(__file__), 'migrations')
        for migration in os.listdir(migration_scripts_path):
            if migration.replace(".sql", "") not in done_migrations:
                with open(os.path.join(migration_scripts_path, migration), 'r') as sql_file:
                    sql_script = sql_file.read()
                    self.__cursor.executescript(sql_script)
                    self.__connection.commit()
                    logging.info(f"Database migration: {migration} done!")
            else:
                logging.info(f"Migration {migration} skipped.")

    def __validate_connection(self):
        try:
            self.__cursor.execute("SELECT * FROM info LIMIT 1;")
            self.__retry_counter = 0
        except sqlite3.ProgrammingError:
            self.__retry_counter += self.__retry_counter
            logging.warning(f"Broken connection to database. Attempt to reconnect no: {self.__retry_counter}")
            try:
                self.__cursor.close()
                self.__connection.close()
            except:
                logging.warning("Unable to close existing database connections.")
            time.sleep(1)
            self.__connection = self.__get_connection()
            self.__cursor = self.__get_cursor()
            if self.__retry_counter < 10:
                self.__validate_connection()
            else:
                logging.error("Unable to connect to database.")

    @staticmethod
    def __get_connection():
        connection = None
        try:
            connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), "database.sqlite"), check_same_thread=False)
            logging.info("Connection to SQLite DB successful.")
        except Error as e:
            logging.error(f"Connection to database failed.")
        return connection

    def __get_cursor(self):
        return self.__connection.cursor()

    def __add_to_que(self, statement: str):
        if self.__lock:
            logging.warning("Concurrency error. Waiting...")
            time.sleep(1)
            self.__add_to_que(statement)
        self.__lock = True
        self.__que.append(statement)
        self.__lock = False

    # interface section:

    def execute_que(self):
        if self.__lock:
            logging.warning("Concurrency error. Waiting...")
            time.sleep(1)
            self.execute_que()
        self.__lock = True
        self.__validate_connection()
        for statement in self.__que:
            self.__cursor.execute(statement)
            self.__connection.commit()
            self.__que.remove(statement)
        self.__que.clear()
        self.__lock = False

    def select(self, table: str, column: str, where: str = None, boolean_needed: bool = False):
        statement = f"SELECT {column} FROM {table}"
        if where:
            statement += where
        fetch = self.__cursor.execute(statement).fetchone()[0]
        if boolean_needed:
            return True if fetch == 1 else False
        return fetch

    def update(self, table: str, column: str, value, boolean_needed: bool = False):
        if boolean_needed:
            value = 1 if value else 0
        statement = f"UPDATE {table} SET {column} = {value}"
        self.__add_to_que(statement)


if __name__ == "__main__":
    database = Database()
    fetch1 = database.select(table='temperature', column="alarm_level")
    print(fetch1)
    fetch2 = database.select(table='temperature', column='alarm', boolean_needed=True)
    print(fetch2)
