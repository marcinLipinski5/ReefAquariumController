import w1thermsensor
from database.db import Database
from datetime import datetime
import logging


class Controller:

    def __init__(self, database: Database):
        self.database = database
        self.sensor = w1thermsensor.W1ThermSensor()
        self.last_read = 0.0
        self.alarm = False

    def run(self):
        temperature = self.sensor.get_temperature()
        self.__check_alarm_conditions(temperature)
        self.__save_temperature_to_db(temperature)

    def __save_temperature_to_db(self, temperature: float):
        ts = datetime.timestamp(datetime.now())
        if abs(self.last_read - temperature) >= 0.2:
            logging.debug(f"Current temperature: {temperature}")
            self.database.update(table='temperature', column='temperature', value=temperature)
            self.database.insert(table='temperature_history', columns=['date_time', 'temperature'], values=[datetime.now().strftime('%Y-%m-%d %H:%M:%S'), temperature])

    def __check_alarm_conditions(self, temperature: float):
        max_temperature = self.database.select(table='temperature', column='alarm_level')
        if temperature >= max_temperature and not self.alarm:
            self.__set_alarm(True)
        elif temperature < max_temperature and self.alarm:
            self.__set_alarm(False)

    def __set_alarm(self, state: bool):
        self.database.update(table='temperature', column='alarm', value=state, boolean_needed=True)
