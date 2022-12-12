import time

from tests.test_runner import TestRunner
from tests.gpio_mock import GPIOSetup
from database.db import Database
from sensors.fan import Fan


class TestFan(TestRunner):

    def setUp(self) -> None:
        super(TestFan, self).setUp()
        self.database = Database(':memory:')
        self.mock = GPIOSetup()
        self.fan = Fan(self.database, self.mock)

    def test_01_should_return_freeze_for_22_degree(self):
        self.execute_sequence_for_level_check(temperature=22.0, expected_level='freeze', expected_duty_cycle=50)

    def test_02_should_return_freeze_for_23_5_degree(self):
        self.execute_sequence_for_level_check(temperature=23.5, expected_level='freeze', expected_duty_cycle=50)

    def test_03_should_return_freeze_for_24_5_degree(self):
        self.execute_sequence_for_level_check(temperature=24.5, expected_level='normal', expected_duty_cycle=80)

    def test_04_should_return_normal_for_25_degree(self):
        self.execute_sequence_for_level_check(temperature=25.0, expected_level='normal', expected_duty_cycle=80)

    def test_05_should_return_normal_for_25_5_degree(self):
        self.execute_sequence_for_level_check(temperature=25.5, expected_level='normal', expected_duty_cycle=80)

    def test_05_should_return_normal_for_25_9_degree(self):
        self.execute_sequence_for_level_check(temperature=25.9, expected_level='normal', expected_duty_cycle=80)

    def test_05_should_return_alarm_for_26_degree(self):
        self.execute_sequence_for_level_check(temperature=26.0, expected_level='alarm', expected_duty_cycle=100)

    def test_06_should_return_alarm_for_27_degree(self):
        self.execute_sequence_for_level_check(temperature=27.0, expected_level='alarm', expected_duty_cycle=100)

    def execute_sequence_for_level_check(self, temperature: float, expected_level: str, expected_duty_cycle: int):
        self.database.update(table='temperature', column='temperature', value=temperature)
        self.database.execute_que()
        self.fan.run()
        self.database.execute_que()
        self.assertEqual(expected_level, self.database.select(table='fan', column='current_level'))
        self.assertEqual(expected_duty_cycle, self.mock.change_pwm_out['duty_cycle'])
