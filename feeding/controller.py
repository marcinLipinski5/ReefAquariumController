import logging
import time

import RPi.GPIO as GPIO
from tinydb import TinyDB, Query
from pins.IOPins import IOPins


class Controller:

    def __init__(self):
        self.database = TinyDB('database/db.json').table("feeding")
        self.water_pump_relay = IOPins.WATER_PUMP_RELAY

    def run(self):
        logging.debug("Start main method for FEEDING")
        if self.__is_work_time_exceeded():
            self.__start_pump()
        elif self.__is_feeding_time():
            self.__stop_pump()

    def __stop_pump(self):
        logging.info('Stopping pump because of feeding process.')
        GPIO.output(self.water_pump_relay.value, GPIO.HIGH)  # TODO check relay NO/NC
        self.database.update({'state': True}, Query().type == 'water_pump_state')

    def __start_pump(self):
        logging.info('Starting water pump.')
        GPIO.output(self.water_pump_relay.value, GPIO.LOW)  # TODO check relay NO/NC
        self.database.update({'state': False}, Query().type == 'water_pump_state')
        self.database.update({'timestamp': 0}, Query().type == 'start_time')
        self.database.update({'status': False}, Query().type == 'is_feeding_time')

    def __is_feeding_time(self):
        return self.database.get(Query().type == 'is_feeding_time')['status']

    def __is_work_time_exceeded(self) -> bool:
        start_time = self.database.get(Query().type == 'start_time')['timestamp']
        if int(start_time) == 0:
            return False

        calculated_time = round(self.database.get(Query().type == 'feeding_duration')['seconds'] - (time.time() - start_time))
        if calculated_time <= 0:
            return True