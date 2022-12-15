from database.db import Database
from sensors.auto_refill.controller import Controller
from tests.gpio_mock import GPIOSetup
from tests.test_runner import TestRunner
from datetime import datetime


class TestController(TestRunner):

    def setUp(self) -> None:
        super(TestController, self).setUp()
        self.database = Database(':memory:')
        self.gpio = GPIOSetup()
        self.temperature = Controller(self.database, self.gpio)

    def test_01_should_do_nothing_if_limit_switch_is_open(self):
        self.gpio.mock_gpio_status(self.gpio.limit_switch.value, 1)
        self.temperature.run()
        self.database.execute_que()
        self.assertTrue(self.database.select(table='auto_refill', column='limit_switch_state', boolean_needed=True))

    def test_02_should_set_alarm_if_level_sensor_up_value_is_on(self):
        self.assertFalse(self.database.select(table='auto_refill', column='alarm', boolean_needed=True))
        self.gpio.mock_gpio_status(self.gpio.limit_switch.value, 0)
        self.gpio.mock_gpio_status(self.gpio.water_level_sensor_up_value.value, 1)
        self.temperature.run()
        self.database.execute_que()
        self.assertTrue(self.database.select(table='auto_refill', column='alarm', boolean_needed=True))

    def test_03_should_set_alarm_if_daily_refill_flow_is_reached(self):
        self.assertFalse(self.database.select(table='auto_refill', column='alarm', boolean_needed=True))
        self.gpio.mock_gpio_status(self.gpio.limit_switch.value, 0)
        self.gpio.mock_gpio_status(self.gpio.water_level_sensor_up_value.value, 0)
        self.database.update(table='auto_refill', column='daily_refill_flow', value=1001)
        self.database.execute_que()
        self.temperature.run()
        self.database.execute_que()
        self.assertTrue(self.database.select(table='auto_refill', column='alarm', boolean_needed=True))
