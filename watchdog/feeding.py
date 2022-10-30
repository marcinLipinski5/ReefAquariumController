import time
import logging

import RPi.GPIO as GPIO
from tinydb import TinyDB, Query

from pins.IOPins import IOPins


class FeedingWatchdog:

    def __init__(self):
        self.database = TinyDB('database/db.json').table("feeding")
        self.water_pump_relay = IOPins.WATER_PUMP_RELAY.value

    def run(self):
        if self.__is_work_time_exceeded():
            self.__reset_pump_relay()
            logging.warning("WATCHDOG: Auto feeding time exceeded! Resetting pump relay to close state.")

    def __is_work_time_exceeded(self) -> bool:
        start_time = self.database.get(Query().type == 'start_time')['timestamp']
        calculated_time = round(self.database.get(Query().type == 'feeding_duration')['seconds'] - (time.time() - start_time))
        if calculated_time < -10:  # ten seconds delay as protection against random alarm
            return True

    def __reset_pump_relay(self):
        GPIO.output(self.water_pump_relay, GPIO.LOW)  # TODO check relays NO/NC status
        self.database.update({'state': False}, Query().type == 'water_pump_state')
        self.database.update({'timestamp': 0}, Query().type == 'start_time')
        self.database.update({'status': False}, Query().type == 'is_feeding_time')

