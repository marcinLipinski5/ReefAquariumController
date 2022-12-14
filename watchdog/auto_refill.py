import time
import logging

from pins.gpio_setup import GPIOSetup
from database.db import Database

from pins.IOPins import IOPins


class AutoRefillWatchdog:

    def __init__(self, database: Database, gpio: GPIOSetup):
        self.database = database
        self.gpio = gpio
        self.max_refill_time = self.max_refill_max_time_in_seconds()

    def run(self):
        if self.__is_work_time_exceeded():
            self.__reset_pump_relay()
            logging.warning("WATCHDOG: Auto refill working time exceeded! Resetting refill pump relay to open state.")

    def __is_work_time_exceeded(self) -> bool:
        start_time = self.database.select(table='auto_refill', column='refill_time_start')
        if int(start_time) == 0:
            return False
        else:
            now = time.time()
            return int(now-float(start_time)) > (int(self.max_refill_time) + 3)  # plus 3 seconds as protection against random delays

    def __reset_pump_relay(self):
        self.gpio.set(self.gpio.water_pump_refill_relay.value, 0)
        self.database.update(table='auto_refill', column='refill_time_start', value=0)
        self.database.update(table='auto_refill', column='water_pump_refill_relay_state', value=False, boolean_needed=True)

    def max_refill_max_time_in_seconds(self):
        return self.database.select(table='auto_refill', column='refill_max_time_in_seconds')
