"""
Inspired by https://www.andrewgrabbs.com/interests/hydroponics/cheap-ph-meter-for-raspberry-pi-with-ads1115-and-ph4502c/
"""

import board
import busio
import time
import sys
import statistics
import numpy
from typing import List
import logging
from datetime import datetime

import Adafruit_ADS1x15.ads1115 as ADS
from Adafruit_ADS1x15.analog_in import AnalogIn
from database.db import Database


class Controller:

    def __init__(self, database: Database):
        logging.debug("Starting Ph sensor main method")
        self.database = database
        i2c = busio.I2C(board.SCL, board.SDA)
        ads = ADS.ADS1115(i2c)
        self.channel = AnalogIn(ads, ADS.P0)
        self.m = self.database.select(table='ph', column='m')
        self.b = self.database.select(table='ph', column='b')
        self.ph = self.database.select(table='ph', column='ph')

    def run(self):
        process = self.database.select(table='ph', column='process')
        if process == 'calibration':
            logging.info("Starting calibration process for Ph sensor.")
            self.__calibration()
        elif process == 'work':
            logging.debug("Starting standard procedure for Ph sensor.")
            ph = self.__get_ph_value()
            self.__update_historical_data(ph)

    def __update_historical_data(self, ph: float):
        if round(abs(self.ph - ph), 3) >= 0.1:
            self.ph = ph
            self.database.insert(table='ph_history', columns=['date_time', 'ph'], values=[datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ph])

    def __get_ph_value(self):
        voltage = self.__get_voltage()
        ph = self.m * voltage + self.b
        self.database.update(table='ph', column='ph', value=ph)
        return ph

    def __calibration(self):
        voltage_ph_7_0 = self.database.select(table='ph', column='calibration_voltage_7_0')
        voltage_ph_4_0 = self.database.select(table='ph', column='calibration_voltage_4_0')
        linear_equation_values = self.__solve_equations(ph_7_0=7.0,
                                                        ph_4_0=4.01,
                                                        voltage_ph_7_0=voltage_ph_7_0,
                                                        voltage_ph_4_0=voltage_ph_4_0)
        self.database.update(table='ph', column='m', value=linear_equation_values['m'])
        self.database.update(table='ph', column='b', value=linear_equation_values['b'])
        self.m = linear_equation_values['m']
        self.b = linear_equation_values['b']
        self.database.update(table='ph', column='process', value='work')

    @staticmethod
    def __solve_equations(ph_7_0, ph_4_0, voltage_ph_7_0, voltage_ph_4_0):
        m = (ph_7_0 - ph_4_0) / (voltage_ph_7_0 - voltage_ph_4_0)
        b = ph_4_0 / m * voltage_ph_4_0
        return {'m': m, 'b': b}

    def __get_voltage(self):
        samples = []
        for _ in range(0, 10):
            samples.append(self.channel.voltage)
        samples = samples.sort()[2:-2]
        return statistics.mean(samples)
