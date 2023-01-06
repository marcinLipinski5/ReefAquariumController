import logging

from database.db import Database
from pins.gpio_setup import GPIOSetup


class Fan:

    def __init__(self, database: Database, gpio_setup: GPIOSetup):
        self.database = database
        self.gpio_setup = gpio_setup
        self.level = ''

    def run(self):
        level = self.__get_level()
        if level != '0':
            self.__save_level(level)
            self.__set_duty_cycle(self.database.select(table='fan', column=f'{level}_level_duty_cycle'))

    # TODO adjust with real hardware for noise level
    def __get_level(self) -> str:
        temperature_alarm_level = self.database.select(table='temperature', column='alarm_level')
        current_temperature = self.database.select(table='temperature', column='temperature')
        update = self.database.select(table='fan', column='update_needed', boolean_needed=True)

        if current_temperature >= temperature_alarm_level and (self.level != 'alarm' or update):
            return 'alarm'
        elif (temperature_alarm_level - 2) < current_temperature <= (temperature_alarm_level - 0.1) and (self.level != 'normal' or update):
            return 'normal'
        elif current_temperature <= (temperature_alarm_level - 2) and (self.level != 'freeze' or update):
            return 'freeze'
        return '0'

    def __save_level(self, level: str):
        logging.info(f"Setting {level} level for fan speed.")
        self.level = level
        self.database.update(table='fan', column='current_level', value=level)
        self.database.update(table='fan', column='update_needed', value=False, boolean_needed=True)

    def __set_duty_cycle(self, duty_cycle: int):
        logging.info(f"Setting duty cycle: {duty_cycle} for PWM fans controller.")
        self.gpio_setup.change_pwm(duty_cycle)
