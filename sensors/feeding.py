import logging
import time

from database.db import Database
from pins.gpio_setup import GPIOSetup


class Feeding:

    def __init__(self, database: Database, gpio_setup: GPIOSetup):
        self.gpio = gpio_setup
        self.database = database

    def run(self):
        logging.debug("Start main method for FEEDING")
        if self.__should_start_action_be_executed():
            self.__start_pump()
        elif self.__is_feeding_time():
            self.__stop_pump()

    def __stop_pump(self):
        logging.info('Stopping pump because of feeding process.')
        self.gpio.set(self.gpio.water_pump_relay.value, 1)  # TODO check relay NO/NC
        self.database.update(table='feeding', column='water_pump_state', value=False, boolean_needed=True) # TODO check true/false
        self.database.update(table='feeding', column='start_time', value=time.time())

    def __start_pump(self):
        logging.info('Starting water pump.')
        self.gpio.set(self.gpio.water_pump_relay.value, 0)  # TODO check relay NO/NC
        self.database.update(table='feeding', column='water_pump_state', value=True, boolean_needed=True)
        self.database.update(table='feeding', column='start_time', value=0)
        self.database.update(table='feeding', column='is_feeding_time', value=False, boolean_needed=True)

    def __is_feeding_time(self):
        water_pump_state = self.database.select(table='feeding', column='water_pump_state', boolean_needed=True)
        is_feeding_time = self.database.select(table='feeding', column='is_feeding_time', boolean_needed=True)
        return is_feeding_time is True and water_pump_state is True

    def __should_start_action_be_executed(self) -> bool:
        start_time = self.database.select(table='feeding', column='start_time')
        if int(start_time) == 0:
            return False
        else:
            return self.__is_feeding_time_ended(start_time)

    def __is_feeding_time_ended(self, start_time) -> bool:
        water_pump_state = self.database.select(table='feeding', column='water_pump_state', boolean_needed=True)
        is_feeding_time = self.database.select(table='feeding', column='is_feeding_time', boolean_needed=True)
        calculated_time = round(self.database.select(table='feeding', column='feeding_duration') - (time.time() - start_time))
        if (is_feeding_time is False and water_pump_state is False) or (calculated_time <= 0):
            return True
        return False
