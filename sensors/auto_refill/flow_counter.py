
import time
from datetime import date

from database.db import Database

from pins.gpio_setup import GPIOSetup
import logging


class FlowCounter:

    def __init__(self, database: Database, gpio_setup: GPIOSetup):
        self.database = database
        self.gpio = gpio_setup
        self.pulse_counter = 0
        self.first_run = True

    def run(self):
        logging.debug(f"COUNTER IN: {self.pulse_counter}")
        if self.first_run:
            self.__reset_counter()
            self.__count()
            self.first_run = False
        elif self.__should_daily_refill_counter_be_reset():
            self.__reset_counter()
        else:
            self.__count()
        print(self.pulse_counter)
        self.pulse_counter = 0

    def __count(self):
        self.gpio.add_event_detect(self.gpio.water_pump_refill_flow_counter.value, 'RISING', self.count_pulse)
        time.sleep(self.__get_refill_max_time_in_seconds())
        self.gpio.remove_event_detect(self.gpio.water_pump_refill_flow_counter.value)
        logging.debug(f"COUNTER OUT: {self.pulse_counter}")
        current_flow = self.database.select(table='auto_refill', column='daily_refill_flow')
        self.database.update(table='auto_refill', column='daily_refill_flow',
                             value=(self.__get_flow_in_milliliters() + current_flow))

    def __get_flow_in_milliliters(self) -> float:
        # TODO some calculations here
        return self.pulse_counter / 7.5

    def count_pulse(self, _):
        self.pulse_counter += 1

    def __should_daily_refill_counter_be_reset(self):
        return self.database.select(table='auto_refill', column='flow_count_date') != self.__get_current_date()

    def __reset_counter(self):
        self.__save_daily_flow()
        self.database.update(table='auto_refill', column='daily_refill_flow', value=0)
        self.database.update(table='auto_refill', column='flow_count_date', value=self.__get_current_date())

    def __save_daily_flow(self):
        flow_count_date = self.__get_current_date()
        flow = self.database.select(table='auto_refill', column='daily_refill_flow') + self.__get_flow_in_milliliters()
        self.database.insert(table='auto_refill_history', columns=['date', 'flow'], values=[flow_count_date, flow])

    @staticmethod
    def __get_current_date():
        return date.today().strftime("%d-%m-%Y")

    def __get_refill_max_time_in_seconds(self):
        return self.database.select(table='auto_refill', column='refill_max_time_in_seconds')


if __name__ == "__main__":
    FlowCounter(Database(':memory:'), GPIOSetup())
