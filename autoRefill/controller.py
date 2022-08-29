import time
import traceback

from pins.IOPins import IOPins
import logging
from tinydb import TinyDB, Query


# import RPi.GPIO as GPIO


class Controller:

    def __init__(self, database=TinyDB('db.json')):
        self.database = database.table("auto_refill")
        # self.database.insert({'type': 'alarm', 'status': False})
        # self.database.insert({'type': 'daily_refill_flow', 'flow': 0})
        # self.database.insert({'type': 'max_daily_refill_flow', 'flow': 1000})

        self.water_level_sensor_down_value_main = IOPins.WATER_LEVEL_SENSOR_DOWN_VALUE_MAIN.value
        self.water_level_sensor_down_value_backup = IOPins.WATER_LEVEL_SENSOR_DOWN_VALUE_BACKUP.value
        self.water_level_sensor_up_value = IOPins.WATER_LEVEL_SENSOR_UP_VALUE.value
        self.water_pump_refill_relay = IOPins.WATER_PUMP_REFILL_RELAY.value
        self.water_pump_refill_flow_control = IOPins.WATER_PUMP_REFILL_FLOW_COUNTER.value

        self.alarm = self.get_alarm()

    def run(self):
        time_counter = 1  #  max time for pump to run in single iteration
        self.check_alarm_conditions()
        if self.should_pump_be_active():
            # GPIO.output(self.water_pump_refill_relay, GPIO.HIGH)
            time.sleep(time_counter)
            # GPIO.output(self.water_pump_refill_relay, GPIO.LOW)

    @staticmethod
    def check_level_sensor_state(sensor_pin: int) -> bool:  # TODO adjust to NC/NO sensor structure
        # return True if GPIO.input(sensor_pin) == 1 else False
        return False

    def check_alarm_conditions(self) -> None:
        alarm_state = True
        try:
            up_value_sensor = self.check_level_sensor_state(self.water_level_sensor_up_value)
            alarm_state = True if (up_value_sensor or self.is_daily_water_flow_reached()) else False
        except:
            logging.warning(f"Unable to collect info about auto refill state. {traceback.print_exc()}")
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

if __name__ == "__main__":
    dupa = Controller()
    # dupa.set_alarm(False)
    dupa.run()
    print(dupa.get_alarm())
    # dupa.set_alarm(False)
    # print(dupa.get_alarm())
    # print(dupa.is_daily_water_flow_reached())

