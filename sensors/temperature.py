#  import mock for local (not RPi) development
try:
    import w1thermsensor
except:
    import tests.w1thermsensor_mock as w1thermsensor
from database.db import Database
from datetime import datetime
import logging
from pins.gpio_setup import GPIOSetup


class Temperature:

    def __init__(self, database: Database, gpio: GPIOSetup):
        self.database = database
        self.sensor = w1thermsensor.W1ThermSensor()
        self.gpio = gpio
        self.last_read = 0.00
        self.last_hour = datetime.now().strftime('%H')
        self.alarm = False

    def run(self):
        temperature = round(self.sensor.get_temperature(), 2)
        self.__check_alarm_conditions(temperature)
        self.__save_temperature_to_db(temperature)

    def __save_temperature_to_db(self, temperature: float):
        if (round(abs(self.last_read - temperature), 2) >= 0.2) or (self.last_hour != datetime.now().strftime('%H')):
            logging.debug(f"Current temperature: {temperature}")
            self.last_read = temperature
            self.last_hour = datetime.now().strftime('%H')
            self.database.update(table='temperature', column='temperature', value=temperature)
            self.database.insert(table='temperature_history',
                                 columns=['date_time', 'temperature'],
                                 values=[datetime.now().strftime('%Y-%m-%d %H:%M:%S'), temperature])

    def __check_alarm_conditions(self, temperature: float):
        # casting to int to avoid relay flicking on temp on the end of the range
        max_temperature = self.database.select(table='temperature', column='alarm_level')
        if int(temperature) >= max_temperature and not self.alarm:
            logging.info(f"Setting alarm level for temperature sensor. Current temperature: {temperature}")
            self.__set_alarm(True)
        elif (int(temperature) < max_temperature and self.alarm) or self.last_read == 0.00:
            logging.info(f"Setting normal level for temperature sensor. Current temperature: {temperature}")
            self.__set_alarm(False)

    def __set_alarm(self, state: bool):
        self.database.update(table='temperature', column='alarm', value=state, boolean_needed=True)
        self.database.update(table='temperature', column='heater_state', value=not state, boolean_needed=True)
        self.alarm = state
        if state:
            self.gpio.set(self.gpio.heater_relay.value, 1)
        else:
            self.gpio.set(self.gpio.heater_relay.value, 0)
