
from tinydb import TinyDB, Query
import logging


class Migrations:

    def __init__(self):
        # self.database = TinyDB('database/db.json', indent=4)
        self.database = TinyDB('C:\\Users\\Dell\\PycharmProjects\\reefAquariumController\\database\\db.json', indent=4)
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
            auto_refill_table.insert({'type': 'refill_time_start', 'time': 0.0})
            auto_refill_table.insert({'type': 'refill_max_time_in_seconds', 'time': 10})
            auto_refill_table.insert({'type': 'water_pump_refill_relay_state', 'state': False})
            auto_refill_table.insert({'type': 'limit_switch_state', 'state': False})
            auto_refill_table.insert({'type': 'water_level_sensor_down_value_main', 'state': False})
            auto_refill_table.insert({'type': 'water_level_sensor_down_value_backup', 'state': False})
            auto_refill_table.insert({'type': 'water_level_sensor_up_value', 'state': False})

            temperature_table = self.database.table('temperature')
            temperature_table.insert({'type': 'temperature', 'value': 0.0})

            pump_table = self.database.table('feeding')
            pump_table.insert({'type': 'is_feeding_time', 'status': False})
            pump_table.insert({'type': 'start_time', 'timestamp': 0})
            pump_table.insert({'type': 'feeding_duration', 'seconds': 600})
            pump_table.insert({'type': 'water_pump_state', 'state': False})
            logging.info("Migration for v1 DONE")


if __name__ == "__main__":
    Migrations()