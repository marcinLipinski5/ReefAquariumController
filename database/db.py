import sqlite3
import time
from sqlite3 import Error
import logging
import os
import pathlib
import threading
from typing import List


class Database:

    def __init__(self, path: str = os.path.join(os.path.dirname(__file__), "database.sqlite")):
        self.__path = path
        self.__connection = self.__get_connection()
        self.__que = []
        self.__retry_counter = 0
        self.__make_migrations()

    def __del__(self):
        self.execute_que()
        self.__connection.close()

    def __make_migrations(self):
        done_migrations = []
        try:
            fetch = self.__connection.cursor().execute("SELECT migration FROM info").fetchall()
            for migration in fetch:
                done_migrations.append(migration[0])
        except:
            pass
        migration_scripts_path = os.path.join(os.path.dirname(__file__), 'migrations')
        for migration in os.listdir(migration_scripts_path):
            if migration.replace(".sql", "") not in done_migrations:
                with open(os.path.join(migration_scripts_path, migration), 'r') as sql_file:
                    sql_script = sql_file.read()
                    self.__connection.cursor().executescript(sql_script)
                    self.__connection.commit()
                    logging.info(f"Database migration: {migration} done!")
            else:
                logging.info(f"Migration {migration} skipped.")

    def __validate_connection(self):
        try:
            self.__connection.cursor().execute("SELECT * FROM info LIMIT 1;")
            self.__retry_counter = 0
        except sqlite3.ProgrammingError:
            self.__retry_counter += self.__retry_counter
            logging.warning(f"Broken connection to database. Attempt to reconnect no: {self.__retry_counter}")
            try:
                self.__connection.close()
            except:
                logging.warning("Unable to close existing database connections.")
            time.sleep(1)
            self.__connection = self.__get_connection()
            if self.__retry_counter < 10:
                self.__validate_connection()
            else:
                logging.error("Unable to connect to database.")

    def __get_connection(self):
        connection = None
        try:
            connection = sqlite3.connect(self.__path, check_same_thread=False)
            logging.info("Connection to SQLite DB successful.")
        except Error as e:
            logging.error(f"Connection to database failed.")
        return connection

    def __add_to_que(self, statement: str):
        lock = threading.Lock()
        try:
            lock.acquire(True)
            self.__que.append(statement)
        finally:
            lock.release()

    # interface section:

    def get_que(self):
        return self.__que

    def execute_que(self):
        if self.__que:
            lock = threading.Lock()
            try:
                lock.acquire(True)
                self.__validate_connection()
                iteration_list = self.__que.copy()
                for statement in iteration_list:
                    logging.debug(f"SQL --> {statement}")
                    self.__connection.cursor().execute(statement)
                    self.__connection.commit()
                    self.__que.remove(statement)
            finally:
                lock.release()

    def select(self, table: str, column: str = "*", where: str = None, boolean_needed: bool = False, single: bool = True):
        statement = f"SELECT {column} FROM {table}"
        if where:
            statement += f' WHERE {where}'
        if single:
            fetch = self.__connection.cursor().execute(statement).fetchone()[0]
        else:
            fetch = self.__connection.cursor().execute(statement).fetchall()
        if boolean_needed:
            return True if fetch == 1 else False
        return fetch

    def update(self, table: str, column: str, value, boolean_needed: bool = False, where: str = None):
        if boolean_needed:
            value = 1 if value else 0
        if type(value) is str:
            value = "'" + value + "'"
        statement = f"UPDATE {table} SET {column} = {value}"
        if where:
            statement += f' WHERE {where}'
        self.__add_to_que(statement)

    def insert(self, table: str, columns: List[str], values: List[str]):
        assert len(columns) == len(values)
        values = map(str, values)
        values = ["'" + value for value in values]
        values = [value + "'" for value in values]
        statement = f'INSERT INTO {table} ({", ".join(columns)}) VALUES ({", ".join(values)})'
        self.__add_to_que(statement)

    def delete(self, table: str, where: str):
        statement = f"DELETE FROM {table} WHERE {where}"
        self.__add_to_que(statement)


if __name__ == "__main__":
    Database(":memory:")