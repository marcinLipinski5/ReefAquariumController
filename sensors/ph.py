"""
Inspired by https://www.andrewgrabbs.com/interests/hydroponics/cheap-ph-meter-for-raspberry-pi-with-ads1115-and-ph4502c/
"""

import logging
import statistics
import time
from datetime import datetime

import adafruit_ads1x15.ads1115 as ADS
import board
import busio
from adafruit_ads1x15.analog_in import AnalogIn

from database.db import Database


class Ph:

    def __init__(self, database: Database):
        logging.debug("Starting Ph sensor main method")
        self.database = database
        i2c = busio.I2C(board.SCL, board.SDA)
        ads = ADS.ADS1115(i2c)
        self.channel = AnalogIn(ads, ADS.P0)
        self.m = self.database.select(table='ph', column='m')
        self.b = self.database.select(table='ph', column='b')
        self.ph = self.database.select(table='ph', column='ph')

        self.calibration_samples = []
        self.alarm = False
        self.statistic_samples = []
        self.last_hour = datetime.now().strftime('%H')

    def run(self):
        process = self.database.select(table='ph', column='process')
        if process == 'calibration':
            logging.info(f"Collecting calibration data for pH={self.database.select(table='ph', column='calibration_ph')} in progress.")
            self.__collect_calibration_samples()
            self.__check_if_calibration_ended()
        if process == 'processing':
            logging.info(f"Processing calibration data for pH={self.database.select(table='ph', column='calibration_ph')} sensor.")
            self.__process_calibration_samples()
            self.database.update(table='ph', column='process', value='calculating')
        elif process == 'calculating':
            self.__update_algorithm()
            self.database.update(table='ph', column='process', value='work')
        elif process == 'manual_calibration':
            self.__manual_algorithm_update()
            self.database.update(table='ph', column='process', value='work')
        elif process == 'work':
            logging.debug("Starting standard procedure for pH sensor.")
            self.statistic_samples.append(self.__get_voltage())
            voltage_statistic_mean = self.__calculate_voltage_statistic_mean()
            if voltage_statistic_mean is not None:
                self.__update_data(voltage_statistic_mean)
            self.__check_alarm_condition()

    def __update_data(self, voltage_statistic_mean: float):
        ph = self.__get_ph_value(voltage_statistic_mean)
        if (round(abs(self.ph - ph), 3) >= 0.1) or (self.last_hour != datetime.now().strftime('%H')):
            self.ph = ph
            self.last_hour = datetime.now().strftime('%H')
            self.database.update(table='ph', column='ph', value=ph)
            self.database.update(table='ph', column='last_voltage', value=voltage_statistic_mean)
            self.database.insert(table='ph_history', columns=['date_time', 'ph'], values=[datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ph])

    def __get_ph_value(self, voltage):
        return self.m * voltage + self.b

    def __update_algorithm(self):
        voltage_ph_6_86 = self.database.select(table='ph', column='calibration_voltage_6_86')
        voltage_ph_9_18 = self.database.select(table='ph', column='calibration_voltage_9_18')
        linear_equation_values = self.__solve_equations(ph_6_86=6.86,
                                                        ph_9_18=9.18,
                                                        voltage_ph_6_86=voltage_ph_6_86,
                                                        voltage_ph_9_18=voltage_ph_9_18)
        self.database.update(table='ph', column='m', value=linear_equation_values['m'])
        self.database.update(table='ph', column='b', value=linear_equation_values['b'])
        self.m = linear_equation_values['m']
        self.b = linear_equation_values['b']

    @staticmethod
    def __solve_equations(ph_6_86, ph_9_18, voltage_ph_6_86, voltage_ph_9_18):
        m = (ph_6_86 - ph_9_18) / (voltage_ph_6_86 - voltage_ph_9_18)
        b = ph_9_18 - voltage_ph_9_18 * m
        return {'m': m, 'b': b}

    def __get_voltage(self):
        samples = []
        for _ in range(0, 10):
            sample = self.channel.voltage
            samples.append(sample)
        logging.debug(f'pH samples: {samples}')
        samples.sort()
        samples = samples[2:-2]
        return statistics.mean(samples)

    def __check_if_calibration_ended(self):
        duration = time.time() - self.database.select(table='ph', column='calibration_time_start')
        if duration >= 240:
            logging.info('pH calibration ended')
            self.database.update(table='ph', column='process', value='processing')
            self.database.update(table='ph', column='calibration_time_start', value=0.0)

    def __collect_calibration_samples(self):
        self.calibration_samples.append(self.__get_voltage())

    def __process_calibration_samples(self):
        self.calibration_samples.sort()
        self.calibration_samples = self.calibration_samples[5:-5]
        voltage = statistics.mean(self.calibration_samples)
        self.calibration_samples = []
        ph = self.database.select(table='ph', column='calibration_ph')
        self.database.update(table='ph', column=f'calibration_voltage_{ph}', value=voltage)
        logging.info(f'Calculated calibration voltage for pH= {ph} voltage: {voltage}')

    def __check_alarm_condition(self):
        if (self.ph >= self.database.select(table='ph', column='alarm_level_up') or self.ph <= self.database.select(table='ph', column='alarm_level_down')) and not self.alarm:
            self.database.update(table='ph', column='alarm', value=True, boolean_needed=True)
            self.alarm = True
        elif (self.ph < self.database.select(table='ph', column='alarm_level_up') or self.ph > self.database.select(table='ph', column='alarm_level_down')) and self.alarm:
            self.database.update(table='ph', column='alarm', value=False, boolean_needed=True)
            self.alarm = False

    def __calculate_voltage_statistic_mean(self):
        if len(self.statistic_samples) >= 60: # 1 sample every 10s -> 60 samples = 10 minutes. Long calc period to avoid random peaks on plot.
            self.statistic_samples.sort()
            self.statistic_samples = self.statistic_samples[20:-20]  # Get rid of max/min values
            result = statistics.mean(self.statistic_samples)
            self.statistic_samples = []
            return result
        return None

    def __manual_algorithm_update(self):
        self.m = self.database.select(table='ph', column='m')
        self.b = self.database.select(table='ph', column='b')
        logging.info(f'Manual calibration done. New values: m={self.m}; b={self.b}')



