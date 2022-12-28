import logging
import time
import traceback

from database.db import Database
from pins.gpio_setup import GPIOSetup
from sensors.auto_refill.flow_counter import FlowCounter


class Controller:

    def __init__(self, database: Database, gpio_setup: GPIOSetup):
        self.database = database
        self.gpio = gpio_setup
        self.alarm = self.__get_alarm()

    def run(self):
        logging.debug("Start main method for AUTO REFILL")
        if self.__check_limit_switch_state():
            return
        if self.__get_calibration_status():
            self.__calibration()
            return
        self.__check_alarm_conditions()
        if self.__should_pump_be_active():
            logging.info("Running auto refill pump")
            try:
                self.database.update(table='auto_refill', column='refill_time_start', value=time.time())
                self.gpio.set(self.gpio.water_pump_refill_relay.value, 1)
                self.database.update(table='auto_refill', column='water_pump_refill_relay_state', value=True, boolean_needed=True)
                self.__run_flow_counter()
            except:
                logging.error("An error occurs during refill pump switching process")
            finally:
                self.gpio.set(self.gpio.water_pump_refill_relay.value, 0)
                self.database.update(table='auto_refill', column='water_pump_refill_relay_state', value=False, boolean_needed=True)
                self.database.update(table='auto_refill', column='refill_time_start', value=0.0)
                logging.info("Auto refill pump successfuly stopped")

    def __run_flow_counter(self):
        logging.debug("Running flow counter")
        FlowCounter(self.database, self.gpio).run()

    def __check_level_sensor_state(self, sensor_pin: int, sensor_description: str) -> bool:  # TODO adjust to NC/NO sensor structure
        state = self.gpio.get(sensor_pin)
        logging.debug(f"Sensor state on pin: {sensor_pin} name: {sensor_description} -> {state}")
        self.database.update(table='auto_refill', column=f'{sensor_description.lower()}_state', value=state, boolean_needed=True)
        return state

    def __check_limit_switch_state(self) -> bool:  # TODO adjust to NC/NO switch structure
        state = self.gpio.get(self.gpio.limit_switch.value)
        self.database.update(table='auto_refill', column='limit_switch_state', value=state, boolean_needed=True)
        if state:
            logging.warning("Limit switch is open. Can not execute auto-refill process.")
        return state

    def __check_alarm_conditions(self) -> None:
        alarm_state = True
        try:
            up_value_sensor = self.__check_level_sensor_state(self.gpio.water_level_sensor_up_value.value,
                                                              self.gpio.water_level_sensor_up_value.name)
            alarm_state = True if (up_value_sensor or self.__is_daily_water_flow_reached()) else False
        except:
            logging.warning(f"Unable to collect info about auto refill state. {traceback.print_exc()}")
        self.__set_alarm(alarm_state)

    def __should_pump_be_active(self) -> bool:
        if self.alarm:
            return False
        main_sensor_state = self.__check_level_sensor_state(self.gpio.water_level_sensor_down_value_main.value,
                                                            self.gpio.water_level_sensor_down_value_main.name)
        backup_sensor_state = self.__check_level_sensor_state(self.gpio.water_level_sensor_down_value_backup.value,
                                                              self.gpio.water_level_sensor_down_value_backup.name)
        is_down_level_reached = main_sensor_state and backup_sensor_state
        if is_down_level_reached:
            return True
        else:
            return False

    def __is_daily_water_flow_reached(self) -> bool:
        return self.database.select(table='auto_refill', column='daily_refill_flow') >= self.database.select(table='auto_refill', column='max_daily_refill_flow')

    def __set_alarm(self, alarm_state: bool):
        self.database.update(table='auto_refill', column='alarm', value=alarm_state, boolean_needed=True)
        self.alarm = alarm_state
        if self.alarm:
            logging.warning(f"Alarm level for auto refill reached. "
                            f"UP_LEVEL_SENSOR_STATUS: {self.__check_level_sensor_state(self.gpio.water_level_sensor_up_value.value, self.gpio.water_level_sensor_up_value.name)}, "
                            f"DAILY_REFILL_FLOW: {self.database.select(table='auto_refill', column='daily_refill_flow')}")

    def __get_alarm(self) -> bool:
        return self.database.select(table='auto_refill', column='alarm', boolean_needed=True)

    def __get_calibration_status(self):
        if not self.database.select(table='auto_refill', column='calibration', boolean_needed=True):
            return False
        elif self.database.select(table='auto_refill', column='calibration', boolean_needed=True) \
                and self.database.select(table='auto_refill', column='calibration_stage') == 'data_collecting':
            return True
        elif self.database.select(table='auto_refill', column='calibration', boolean_needed=True) \
                and self.database.select(table='auto_refill', column='calibration_stage') == 'processing':
            pulses_per_ml = round(self.database.select(table='auto_refill', column='calibration_pulses') / self.database.select(table='auto_refill', column='calibration_flow'), 5)
            self.database.update(table='auto_refill', column='pulses_per_ml', value=pulses_per_ml)
            self.database.update(table='auto_refill', column='calibration_stage', value="done")
            self.database.update(table='auto_refill', column='calibration', value=False, boolean_needed=True)
            return True
        return False

    def __calibration(self):
        logging.info('Starting calibration for flow counter.')
        self.gpio.set(self.gpio.water_pump_refill_relay.value, 1)
        pulses = self.__get_flow_counter_calibration_data()
        self.gpio.set(self.gpio.water_pump_refill_relay.value, 0)
        if pulses == 0:
            logging.error('Unable to collect data for flow calibrations. Break calibration process. Calibration failed.')
            self.database.update(table='auto_refill', column='calibration_stage', value="done")
            self.database.update(table='auto_refill', column='calibration', value=False, boolean_needed=True)
        else:
            self.database.update(table='auto_refill', column='calibration_pulses', value=pulses)
            self.database.update(table='auto_refill', column='calibration', value=False, boolean_needed=True)
        logging.info(f'Stopping calibration for flow counter. Pulse count: {pulses}')

    def __get_flow_counter_calibration_data(self):
        return FlowCounter(self.database, self.gpio).get_calibrations_data()
