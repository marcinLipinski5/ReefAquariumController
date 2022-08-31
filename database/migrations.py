from tinydb import TinyDB, Query
import logging


class Migrations:

    def __init__(self):
        self.database = TinyDB('database/db.json')
        self.make()

    def make(self):
        self.v1()

    def v1(self):
        migrate = False
        try:
            version = self.database.get(Query().type == 'migration')['version']
            if version == "v1":
                migrate = False
                logging.info("Migration for v1 skipped")
        except:
            self.database.insert({'type': 'migration', 'version': 'v1'})
            migrate = True
        if migrate:
            logging.info("Migration for v1 STARTED")
            auto_refill_table = self.database.table("auto_refill")
            auto_refill_table.insert({'type': 'alarm', 'status': False})
            auto_refill_table.insert({'type': 'daily_refill_flow', 'flow': 0})
            auto_refill_table.insert({'type': 'max_daily_refill_flow', 'flow': 1000})
            auto_refill_table.insert({'type': 'flow_count_date', 'date': ''})
            auto_refill_table.insert({'type': 'refill_time_start', 'time': ''})
            auto_refill_table.insert({'type': 'refill_max_time_in_seconds', 'time': 10})
            logging.info("Migration for v1 DONE")
