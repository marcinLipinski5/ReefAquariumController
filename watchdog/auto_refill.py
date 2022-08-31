import time
import logging

import RPi.GPIO as GPIO
from tinydb import TinyDB, Query

from pins.IOPins import IOPins


class AutoRefillWatchdog:

    def __init__(self):
        self.database = TinyDB('database/db.json').table("auto_refill")
        self.water_pump_refill_relay = IOPins.WATER_PUMP_REFILL_RELAY.value
        self.max_refill_time = self.database.get(Query().type == 'refill_max_time_in_seconds')['time']
        GPIO.setup(self.water_pump_refill_relay, GPIO.OUT)

    def run(self):
        if self.__is_work_time_exceeded():
            self.__reset_pump_relay()
            logging.warning("WATCHDOG: Auto refill working time exceeded! Resetting refill pump relay to open state.")

    def __is_work_time_exceeded(self) -> bool:
        start_time = self.database.get(Query().type == 'refill_time_start')['time']
        if int(start_time) == 0:
            return False
        else:
            now = time.time()
            return int(now-float(start_time)) > (int(self.max_refill_time) + 3)  # plus 3 seconds as protection against random delays

    def __reset_pump_relay(self):
        GPIO.output(self.water_pump_refill_relay, GPIO.LOW)
        self.database.update({'time': 0}, Query().type == 'refill_time_start')

    def update_refill_max_time_in_seconds(self):
        self.max_refill_time = self.database.get(Query().type == 'refill_max_time_in_seconds')['time']
