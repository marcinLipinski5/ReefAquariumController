import logging

from database.db import Database
from pins.gpio_setup import GPIOSetup


class Controller:

    def __init__(self, database: Database, gpio_setup: GPIOSetup):
        self.database = database
        self.gpio_setup = gpio_setup
        self.level = ''

    def run(self):
        duty_cycle = self.__get_duty_cycle()
        if duty_cycle is not 0:
            self.__set_duty_cycle(duty_cycle)

    # TODO adjust with real hardware for noise level
    def __get_duty_cycle(self) -> int:
        temperature_alarm_level = self.database.select(table='temperature', column='alarm_level')
        current_temperature = self.database.select(table='temperature', column='temperature')

        if current_temperature >= temperature_alarm_level and self.level is not 'alarm':
            return self.__save_duty_cycle(level='alarm')
        elif current_temperature < (temperature_alarm_level - 1) and self.level is not 'normal':
            return self.__save_duty_cycle(level='normal')
        elif current_temperature < (temperature_alarm_level - 2) and self.level is not 'freeze':
            return self.__save_duty_cycle(level='freeze')
        return 0  # zero as a code of no changes required

    def __save_duty_cycle(self, level: str) -> int:
        logging.info(f"Setting {level} level for fan speed.")
        self.level = level
        self.database.update(table='fan', column='current_level', value=level)
        return self.database.select(table='fan', column=f'{level}_level_duty_cycle')

    def __set_duty_cycle(self, duty_cycle: int):
        logging.info(f"Setting duty cycle: {duty_cycle} for PWM fans controller.")
        self.gpio_setup.change_pwm(duty_cycle)
