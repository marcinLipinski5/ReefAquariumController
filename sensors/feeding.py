import logging
import time

# import RPi.GPIO as GPIO
from pins.gpio_setup import GPIOSetup
from database.db import Database
from pins.IOPins import IOPins


class Feeding:

    def __init__(self, database: Database, gpio_setup: GPIOSetup):
        self.gpio = gpio_setup
        self.database = database

    def run(self):
        logging.debug("Start main method for FEEDING")
        if self.__is_work_time_exceeded():
            self.__start_pump()
        elif self.__is_feeding_time():
            self.__stop_pump()

    def __stop_pump(self):
        logging.info('Stopping pump because of feeding process.')
        self.gpio.set(self.gpio.water_pump_relay.value, 1)  # TODO check relay NO/NC
        self.database.update(table='feeding', column='water_pomp_state', value=False, boolean_needed=True) # TODO check true/false

    def __start_pump(self):
        logging.info('Starting water pump.')
        self.gpio.set(self.gpio.water_pump_relay.value, 0)  # TODO check relay NO/NC
        self.database.update(table='feeding', column='water_pomp_state', value=True, boolean_needed=True)
        self.database.update(table='feeding', column='start_time', value=0)
        self.database.update(table='feeding', column='is_feeding_time', value=False, boolean_needed=True)

    def __is_feeding_time(self):
        return self.database.select(table='feeding', column='is_feeding_time')

    def __is_work_time_exceeded(self) -> bool:
        start_time = self.database.select(table='feeding', column='start_time')
        if int(start_time) == 0:
            return False

        calculated_time = round(self.database.select(table='feeding', column='feeding_duration') - (time.time() - start_time))
        if calculated_time <= 0:
            return True
