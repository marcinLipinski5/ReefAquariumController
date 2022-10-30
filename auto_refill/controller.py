import logging
import time
import traceback

import RPi.GPIO as GPIO
from tinydb import TinyDB, Query

from auto_refill.flow_counter import FlowCounter
from pins.IOPins import IOPins


class Controller:

    def __init__(self):
        self.database = TinyDB('./database/db.json').table("auto_refill")

        self.water_level_sensor_down_value_main = IOPins.WATER_LEVEL_SENSOR_DOWN_VALUE_MAIN
        self.water_level_sensor_down_value_backup = IOPins.WATER_LEVEL_SENSOR_DOWN_VALUE_BACKUP
        self.water_level_sensor_up_value = IOPins.WATER_LEVEL_SENSOR_UP_VALUE
        self.water_pump_refill_relay = IOPins.WATER_PUMP_REFILL_RELAY
        self.limit_switch = IOPins.LIMIT_SWITCH

        GPIO.setup(self.water_level_sensor_down_value_main.value, GPIO.IN)
        GPIO.setup(self.water_level_sensor_down_value_backup.value, GPIO.IN)
        GPIO.setup(self.water_level_sensor_up_value.value, GPIO.IN)
        GPIO.setup(self.water_pump_refill_relay.value, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.limit_switch.value, GPIO.IN)

        self.max_refill_time = self.database.get(Query().type == 'refill_max_time_in_seconds')['time']
        self.alarm = self.get_alarm()

    def run(self):
        logging.debug("Start main method for AUTO REFILL")
        if self.check_limit_switch_state():
            return
        self.check_alarm_conditions()
        if self.should_pump_be_active():
            logging.info("Running auto refill pump")
            try:
                self.database.update({'time': time.time()}, Query().type == 'refill_time_start')
                GPIO.output(self.water_pump_refill_relay.value, GPIO.HIGH)
                self.database.update({'state': True}, Query().type == 'water_pump_refill_relay_state')
                FlowCounter().run(self.max_refill_time)
            except:
                logging.error("An error occurs during refill pump switching process")
                raise
            finally:
                GPIO.output(self.water_pump_refill_relay.value, GPIO.LOW)
                self.database.update({'state': False}, Query().type == 'water_pump_refill_relay_state')
                self.database.update({'time': 0.0}, Query().type == 'refill_time_start')
                logging.info("Auto refill pump successfuly stopped")

    def check_level_sensor_state(self, sensor_pin: int, sensor_description: str) -> bool:  # TODO adjust to NC/NO sensor structure
        state = True if GPIO.input(sensor_pin) == 1 else False
        logging.debug(f"Sensor state on pin: {sensor_pin} -> {state}")
        self.database.update({'state': state}, Query().type == f'{sensor_description.lower()}_state')
        return state

    def check_limit_switch_state(self) -> bool:  # TODO adjust to NC/NO switch structure
        state = True if GPIO.input(self.limit_switch.value) == 1 else False
        self.database.update({'state': state}, Query().type == 'limit_switch_state')
        if state:
            logging.warning("Limit switch is open. Can not execute auto-refill process.")
        return state

    def check_alarm_conditions(self) -> None:
        alarm_state = True
        try:
            up_value_sensor = self.check_level_sensor_state(self.water_level_sensor_up_value.value,
                                                            self.water_level_sensor_up_value.name)
            alarm_state = True if (up_value_sensor or self.is_daily_water_flow_reached()) else False
        except:
            logging.warning(f"Unable to collect info about auto refill state. {traceback.print_exc()}")
            raise
        self.set_alarm(alarm_state)

    def should_pump_be_active(self) -> bool:
        main_sensor_state = self.check_level_sensor_state(self.water_level_sensor_down_value_main.value,
                                                          self.water_level_sensor_down_value_main.name)
        backup_sensor_state = self.check_level_sensor_state(self.water_level_sensor_down_value_backup.value,
                                                            self.water_level_sensor_down_value_backup.name)
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
                            f"UP_LEVEL_SENSOR_STATUS: {self.check_level_sensor_state(self.water_level_sensor_up_value.value, self.water_level_sensor_up_value.name)}, "
                            f"DAILY_REFILL_FLOW: {self.database.get(Query().type == 'daily_refill_flow')['flow']}")

    def get_alarm(self) -> bool:
        return self.database.get(Query().type == 'alarm')['status']

    def update_refill_max_time_in_seconds(self):
        self.max_refill_time = self.database.get(Query().type == 'refill_max_time_in_seconds')['time']


if __name__ == "__main__":
    dupa = Controller()
    while True:
        dupa.run()
        print("-------------------------")
        time.sleep(5)
        

