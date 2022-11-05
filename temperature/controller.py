import w1thermsensor
from tinydb import TinyDB, Query
from datetime import date
import logging


class Controller:

    def __init__(self):
        self.sensor = w1thermsensor.W1ThermSensor()
        self.database = TinyDB('database/db.json', indent=4).table('temperature')
        self.database_archive = TinyDB('database/temperature.json', indent=4).table('temperature')
        self.last_read = 0.0
        self.alarm = False

    def run(self):
        temperature = self.sensor.get_temperature()
        self.__check_alarm_conditions(temperature)
        self.__save_temperature_to_db(temperature)

    def __save_temperature_to_db(self, temperature: float):
        if abs(self.last_read - temperature) >= 0.2:
            logging.debug(f"Current temperature: {temperature}")
            self.database.update({'value': temperature}, Query().type == 'temperature')
            self.database_archive.insert({'date': date.today().strftime("%d-%m-%Y-%H:%M:%S"), 'value': temperature})

    def __check_alarm_conditions(self, temperature: float):
        max_temperature = self.database.get(Query().type == 'alarm_level')['value']
        if temperature >= max_temperature and not self.alarm:
            self.__set_alarm(True)
        elif temperature < max_temperature and self.alarm:
            self.__set_alarm(False)

    def __set_alarm(self, state: bool):
        self.database.update({'alarm': state})
