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
        self.feeding_light = False

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
        if self.__should_feeding_lights_be_enabled():
            self.feeding_light = True
            self.__set_duty_cycle(1)
        elif self.time_start < now <= self.time_stop and not self.light_active:
            self.feeding_light = False
            self.light_active = True
            self.__set_duty_cycle(self.database.select(table='light', column='power'))
        elif self.__should_all_lamps_be_disabled():
            self.feeding_light = False
            self.light_active = False
            self.__set_duty_cycle(0)

    def __should_all_lamps_be_disabled(self, now) -> bool:
        return self.time_start < now > self.time_stop and (self.light_active or self.feeding_light)

    def __should_feeding_lights_be_enabled(self) -> bool:
        return self.database.select(table='light', column='enable_feeding_light', boolean_needed=True) \
               and self.database.select(table="feeding", column="is_feeding_time", boolean_needed=True) \
               and not self.feeding_light \
               and not self.light_active

    def __set_duty_cycle(self, duty_cycle: int):
        logging.info(f"Setting duty cycle: {duty_cycle} for PWM light controller.")
        self.gpio_setup.change_pwm(self.gpio_setup.pwm_light, duty_cycle)
