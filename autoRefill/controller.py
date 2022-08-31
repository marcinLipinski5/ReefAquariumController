import logging
import time
import traceback

import RPi.GPIO as GPIO
from tinydb import TinyDB, Query

from autoRefill.flow_counter import FlowCounter
from pins.IOPins import IOPins


class Controller:

    def __init__(self):
        self.database = TinyDB('database/db.json').table("auto_refill")

        self.water_level_sensor_down_value_main = IOPins.WATER_LEVEL_SENSOR_DOWN_VALUE_MAIN.value
        self.water_level_sensor_down_value_backup = IOPins.WATER_LEVEL_SENSOR_DOWN_VALUE_BACKUP.value
        self.water_level_sensor_up_value = IOPins.WATER_LEVEL_SENSOR_UP_VALUE.value
        self.water_pump_refill_relay = IOPins.WATER_PUMP_REFILL_RELAY.value

        GPIO.setup(self.water_level_sensor_down_value_main, GPIO.IN)
        GPIO.setup(self.water_level_sensor_down_value_backup, GPIO.IN)
        GPIO.setup(self.water_level_sensor_up_value, GPIO.IN)
        GPIO.setup(self.water_pump_refill_relay, GPIO.OUT, initial=GPIO.LOW)

        self.max_refill_time = self.database.get(Query().type == 'refill_max_time')['time']
        self.alarm = self.get_alarm()

    def run(self):
        self.check_alarm_conditions()
        if self.should_pump_be_active():
            logging.info("Running auto refill pump")
            try:
                self.database.update({'time': time.time()}, Query().type == 'refill_time_start')
                GPIO.output(self.water_pump_refill_relay, GPIO.HIGH)
                FlowCounter().run(self.max_refill_time)
            except:
                logging.error("An error occurs during refill pump switching process")
                raise
            finally:
                GPIO.output(self.water_pump_refill_relay, GPIO.LOW)
                self.database.update({'time': 0}, Query().type == 'refill_time_start')

    @staticmethod
    def check_level_sensor_state(sensor_pin: int) -> bool:  # TODO adjust to NC/NO sensor structure
        state = True if GPIO.input(sensor_pin) == 1 else False
        print(f"Sensor state on pin: {sensor_pin} -> {state}")
        return state

    def check_alarm_conditions(self) -> None:
        alarm_state = True
        try:
            up_value_sensor = self.check_level_sensor_state(self.water_level_sensor_up_value)
            alarm_state = True if (up_value_sensor or self.is_daily_water_flow_reached()) else False
        except:
            logging.warning(f"Unable to collect info about auto refill state. {traceback.print_exc()}")
            raise
        self.set_alarm(alarm_state)

    def should_pump_be_active(self) -> bool:
        main_sensor_state = self.check_level_sensor_state(self.water_level_sensor_down_value_main)
        backup_sensor_state = self.check_level_sensor_state(self.water_level_sensor_down_value_backup)
        is_down_level_reached = main_sensor_state and backup_sensor_state

        if self.alarm:
            return False
        elif is_down_level_reached:
            return True
        else:
            return False

    def is_daily_water_flow_reached(self) -> bool:
        return self.database.get(Query().type == 'daily_refill_flow')['flow'] >= self.database.get(Query().type == 'max_daily_refill_flow')['flow']

    def set_alarm(self, alarm_state: bool):
        self.database.update({'status': alarm_state}, Query().type == 'alarm')
        self.alarm = alarm_state
        if self.alarm:
            logging.warning(f"Alarm level for auto refill reached. "
                            f"UP_LEVEL_SENSOR_STATUS: {self.check_level_sensor_state(self.water_level_sensor_up_value)}, "
                            f"DAILY_REFILL_FLOW: {self.database.get(Query().type == 'daily_refill_flow')['flow']}")

    def get_alarm(self) -> bool:
        return self.database.get(Query().type == 'alarm')['status']

    def update_refill_max_time_in_seconds(self):
        self.max_working_time = self.database.get(Query().type == 'refill_max_time_in_seconds')['time']


if __name__ == "__main__":
    dupa = Controller()
    while True:
        dupa.run()
        print("-------------------------")
        time.sleep(5)
        

