from datetime import date
from tinydb import TinyDB, Query
import RPi.GPIO as GPIO
import time, sys

from pins.IOPins import IOPins


class FlowCounter:

    #  TODO run it as a separete thread on start of Main(). Purpose for this class is only to count flow, save to db and reset state on midnight
    def __init__(self, database=TinyDB('db.json')):
        self.database = database.table("auto_refill")
        self.database.insert({'type': 'flow_count_date', 'date': "29-08-2022"})

        self.pulse_counter = 0

        self.water_pump_refill_flow_counter = IOPins.WATER_PUMP_REFILL_FLOW_COUNTER.value
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.water_pump_refill_flow_counter, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def run(self, time_of_refill: int):
        print(f"COUNTER IN: {self.pulse_counter}")
        if self.__should_daily_refill_counter_be_reset(): self.__reset_counter()
        GPIO.add_event_detect(self.water_pump_refill_flow_counter, GPIO.RISING, callback=self.__count_pulse)
        time.sleep(time_of_refill)
        GPIO.remove_event_detect(self.water_pump_refill_flow_counter)
        print(f"COUNTER OUT: {self.pulse_counter}")
        self.database.update({'flow': self.__get_flow_in_milliliters()}, Query().type == 'daily_refill_flow')

    def __get_flow_in_milliliters(self) -> float:
        # TODO some calculations here
        result = self.pulse_counter * 2
        return result

    def __count_pulse(self):
        self.pulse_counter += 1

    def __should_daily_refill_counter_be_reset(self):
        return self.database.get(Query().type == 'flow_count_date')['date'] != self.__get_current_date()

    def __reset_counter(self):
        self.database.update({'flow': 0}, Query().type == 'daily_refill_flow')
        self.database.update({'date': self.__get_current_date()}, Query().type == 'flow_count_date')

    @staticmethod
    def __get_current_date():
        return date.today().strftime("%d-%m-%Y")

if __name__ == "__main__":
    dupa = FlowCounter()
    print(dupa.__should_daily_refill_counter_be_reset())
    dupa.__run()