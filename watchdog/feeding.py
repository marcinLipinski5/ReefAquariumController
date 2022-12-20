import time
import logging

from pins.gpio_setup import GPIOSetup
from database.db import Database

from pins.IOPins import IOPins


class FeedingWatchdog:

    def __init__(self, database: Database, gpio: GPIOSetup):
        self.database = database
        self.gpio = gpio

    def run(self):
        if self.__is_work_time_exceeded():
            logging.warning("WATCHDOG: Feeding time exceeded! Resetting pump relay to close state.")
            self.__reset_pump_relay()

    def __is_work_time_exceeded(self) -> bool:
        start_time = self.database.select(table="feeding", column="start_time")
        if start_time in [0, 0.0]:
            return False
        calculated_time = round(self.database.select(table="feeding", column="feeding_duration") - (time.time() - start_time))
        if calculated_time < -10:  # ten seconds delay as protection against random alarm
            return True

    def __reset_pump_relay(self):
        self.gpio.set(self.gpio.water_pump_relay.value, 0)  # TODO check relays NO/NC status
        self.database.update(table="feeding", column="water_pump_state", value=False, boolean_needed=True)
        self.database.update(table="feeding", column="start_time", value=0)
        self.database.update(table="feeding", column="is_feeding_time", value=False, boolean_needed=True)

