import w1thermsensor
from tinydb import TinyDB, Query
from datetime import date
import logging


class Controller:

    def __init__(self):
        self.sensor = w1thermsensor.W1ThermSensor()
        self.database = TinyDB('database/db.json').table('temperature')
        self.database_archive = TinyDB('database/temperature.json').table('temperature')
        self.last_read = 0.0

    def run(self):
        temperature = self.sensor.get_temperature()
        self.__save_temperature_to_db(temperature)

    def __save_temperature_to_db(self, temperature: float):
        if abs(self.last_read - temperature) >= 0.0:
            logging.debug(f"Current temperature: {temperature}")
            self.database.update({'value': temperature}, Query().type == 'temperature')
            self.database_archive.insert({'date': date.today().strftime("%d-%m-%Y"), 'value': temperature})
