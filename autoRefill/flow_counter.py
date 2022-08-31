
import time
from datetime import date

import RPi.GPIO as GPIO
from tinydb import TinyDB, Query

from pins.IOPins import IOPins


class FlowCounter:

    def __init__(self):
        self.database = TinyDB('database/db.json').table("auto_refill")

        self.pulse_counter = 0

        self.water_pump_refill_flow_counter = IOPins.WATER_PUMP_REFILL_FLOW_COUNTER.value
        GPIO.setup(self.water_pump_refill_flow_counter, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def run(self, time_of_refill: int):
        print(f"COUNTER IN: {self.pulse_counter}")
        if self.__should_daily_refill_counter_be_reset(): self.__reset_counter()
        GPIO.add_event_detect(self.water_pump_refill_flow_counter, GPIO.RISING, callback=self.count_pulse)
        time.sleep(time_of_refill)
        GPIO.remove_event_detect(self.water_pump_refill_flow_counter)
        print(f"COUNTER OUT: {self.pulse_counter}")
        self.database.update({'flow': self.database.get(Query().type == 'daily_refill_flow')['flow'] +
                                      self.__get_flow_in_milliliters()}, Query().type == 'daily_refill_flow')

    def __get_flow_in_milliliters(self) -> float:
        # TODO some calculations here
        result = self.pulse_counter * 2
        return result

    def count_pulse(self, _):
        self.pulse_counter += 1

    def __should_daily_refill_counter_be_reset(self):
        return self.database.get(Query().type == 'flow_count_date')['date'] != self.__get_current_date()

    def __reset_counter(self):
        self.__save_daily_flow()
        self.database.update({'flow': 0}, Query().type == 'daily_refill_flow')
        self.database.update({'date': self.__get_current_date()}, Query().type == 'flow_count_date')

    def __save_daily_flow(self):
        database = TinyDB('database/daily_flow.json').table("daily_flow")
        date = self.database.get(Query().type == 'flow_count_date')['date']
        flow = self.database.get(Query().type == 'daily_refill_flow')['flow']
        database.insert({'date': date, 'flow': flow})

    @staticmethod
    def __get_current_date():
        return date.today().strftime("%d-%m-%Y")

if __name__ == "__main__":
    dupa = FlowCounter()
    while True:
        dupa.run(10)
