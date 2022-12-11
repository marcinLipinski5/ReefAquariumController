import logging
import time
import traceback

import RPi.GPIO as GPIO
from database.db import Database

from auto_refill.flow_counter import FlowCounter
from pins.IOPins import IOPins


class Controller:

    def __init__(self, database: Database):
        self.database = database

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

        self.max_refill_time = self.get_refill_max_time_in_seconds()
        self.alarm = self.get_alarm()

    def run(self):
        logging.debug("Start main method for AUTO REFILL")
        if self.check_limit_switch_state():
            return
        self.check_alarm_conditions()
        if self.should_pump_be_active():
            logging.info("Running auto refill pump")
            try:
                self.database.update(table='auto_refill', column='refill_time_start', value=time.time())
                GPIO.output(self.water_pump_refill_relay.value, GPIO.HIGH)
                self.database.update(table='auto_refill', column='water_pump_refill_relay_state', value=True, boolean_needed=True)
                FlowCounter().run(self.max_refill_time)
            except:
                logging.error("An error occurs during refill pump switching process")
                raise
            finally:
                GPIO.output(self.water_pump_refill_relay.value, GPIO.LOW)
                self.database.update(table='auto_refill', column='water_pump_refill_relay_state', value=False, boolean_needed=True)
                self.database.update(table='auto_refill', column='refill_time_start', value=0.0)
                logging.info("Auto refill pump successfuly stopped")

    def check_level_sensor_state(self, sensor_pin: int, sensor_description: str) -> bool:  # TODO adjust to NC/NO sensor structure
        state = True if GPIO.input(sensor_pin) == 1 else False
        logging.debug(f"Sensor state on pin: {sensor_pin} -> {state}")
        self.database.update(table='auto_refill', column=f'{sensor_description.lower()}_state', value=state)
        return state

    def check_limit_switch_state(self) -> bool:  # TODO adjust to NC/NO switch structure
        state = True if GPIO.input(self.limit_switch.value) == 1 else False
        self.database.update(table='auto_refill', column='limit_switch_state', value=state)
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
        return self.database.select(table='auto_refill', column='daily_refill_flow') >= self.database.select(table='auto_refill', column='max_daily_refill_flow')

    def set_alarm(self, alarm_state: bool):
        self.database.update(table='auto_refill', column='alarm', value=alarm_state)
        self.alarm = alarm_state
        if self.alarm:
            logging.warning(f"Alarm level for auto refill reached. "
                            f"UP_LEVEL_SENSOR_STATUS: {self.check_level_sensor_state(self.water_level_sensor_up_value.value, self.water_level_sensor_up_value.name)}, "
                            f"DAILY_REFILL_FLOW: {self.database.select(table='auto_refill', column='daily_refill_flow')}")

    def get_alarm(self) -> bool:
        return self.database.select(table='auto_refill', column='alarm', boolean_needed=True)

    def get_refill_max_time_in_seconds(self):
        return self.database.select(table='auto_refill', column='refill_max_time_in_seconds')


if __name__ == "__main__":
    dupa = Controller()
    while True:
        dupa.run()
        print("-------------------------")
        time.sleep(5)
        

