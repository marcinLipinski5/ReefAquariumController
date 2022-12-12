
import time
from datetime import date

# import RPi.GPIO as GPIO
from database.db import Database

# from pins.IOPins import IOPins
from pins.gpio_setup import GPIOSetup


class FlowCounter:

    def __init__(self, database: Database, gpio_setup: GPIOSetup):
        self.database = database
        self.gpio = gpio_setup
        self.pulse_counter = 0

        # self.water_pump_refill_flow_counter = IOPins.WATER_PUMP_REFILL_FLOW_COUNTER.value
        # GPIO.setup(self.water_pump_refill_flow_counter, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def run(self, time_of_refill: int):
        print(f"COUNTER IN: {self.pulse_counter}")
        if self.__should_daily_refill_counter_be_reset(): self.__reset_counter()
        self.gpio.add_event_detect(self.gpio.water_pump_refill_flow_counter.value, 'RISING', self.count_pulse)
        # GPIO.add_event_detect(self.water_pump_refill_flow_counter, GPIO.RISING, callback=self.count_pulse)
        time.sleep(time_of_refill)
        self.gpio.remove_event_detect(self.gpio.water_pump_refill_flow_counter.value)
        # GPIO.remove_event_detect(self.water_pump_refill_flow_counter)
        print(f"COUNTER OUT: {self.pulse_counter}")
        current_flow = self.database.select(table='auto_refill', column='daily_refill_flow')
        self.database.update(table='auto_refill', column='daily_refill_flow', value=(self.__get_flow_in_milliliters() + current_flow))

    def __get_flow_in_milliliters(self) -> float:
        # TODO some calculations here
        result = self.pulse_counter * 2
        return result

    def count_pulse(self, _):
        self.pulse_counter += 1

    def __should_daily_refill_counter_be_reset(self):
        return self.database.select(table='auto_refill', column='flow_count_date') != self.__get_current_date()

    def __reset_counter(self):
        self.__save_daily_flow()
        self.database.update(table='auto_refill', column='daily_refill_flow', value=0)
        self.database.update(table='auto_refill', column='flow_count_date', value=self.__get_current_date())

    def __save_daily_flow(self):
        flow_count_date = self.database.select(table='auto_refill', column='flow_count_date')
        flow = self.database.select(table='auto_refill', column='daily_refill_flow')
        self.database.insert(table='auto_refill_history', columns=['date', 'flow'], values=[flow_count_date, flow])

    @staticmethod
    def __get_current_date():
        return date.today().strftime("%d-%m-%Y")

if __name__ == "__main__":
    dupa = FlowCounter()
    while True:
        dupa.run(10)
