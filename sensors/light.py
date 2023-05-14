import logging

from database.db import Database
from pins.gpio_setup import GPIOSetup
from datetime import datetime


class Light:

    def __init__(self, database: Database, gpio_setup: GPIOSetup):
        logging.info("Starting main method for light control.")
        self.database = database
        self.gpio_setup = gpio_setup
        self.__set_duty_cycle(self.database.select(table='light', column='power'))
        self.time_start = self.str_to_time(self.database.select(table='light', column='start_time'))
        self.time_stop = self.str_to_time(self.database.select(table='light', column='stop_time'))
        self.light_active = False

    @staticmethod
    def str_to_time(string_time: str):
        return datetime.strptime(string_time, '%H:%M')

    def run(self):
        now = self.str_to_time(datetime.now().strftime("%H:%M"))
        if self.database.select(table='light', column='update_needed', boolean_needed=True):
            self.__set_duty_cycle(self.database.select(table='light', column='power'))
            self.time_start = self.str_to_time(self.database.select(table='light', column='start_time'))
            self.time_stop = self.str_to_time(self.database.select(table='light', column='stop_time'))
            self.database.update(table='light', column='update_needed', value=False, boolean_needed=True)
        if self.time_start >= now <= self.time_stop and not self.light_active:
            self.light_active = True
            self.__set_duty_cycle(self.database.select(table='light', column='power'))
        elif self.time_start < now > self.time_stop and self.light_active:
            self.light_active = False
            self.__set_duty_cycle(0)

    def __set_duty_cycle(self, duty_cycle: int):
        logging.info(f"Setting duty cycle: {duty_cycle} for PWM light controller.")
        self.gpio_setup.change_pwm(self.gpio_setup.pwm_light, duty_cycle)