from database.db import Database
from sensors.temperature import Temperature
from tests.gpio_mock import GPIOSetup
from tests.test_runner import TestRunner
from datetime import datetime


class TestTemperature(TestRunner):

    def setUp(self) -> None:
        super(TestTemperature, self).setUp()
        self.database = Database(':memory:')
        self.gpio = GPIOSetup()
        self.temperature = Temperature(self.database, self.gpio)

    def test_01_should_write_at_first_read_temperature_to_db_and_historical_storage_and_run_heater(self):
        self.temperature.sensor.set_temperature(10.0)
        self.temperature.run()
        self.database.execute_que()
        self.assertEqual(10, self.database.select(table='temperature', column='temperature'))
        self.assertEqual(10, self.database.select(table='temperature_history', column='temperature'))
        self.assertIsInstance(datetime.strptime(self.database.select(table='temperature_history', column='date_time'), '%Y-%m-%d %H:%M:%S'), datetime)
        self.assertEqual(0, self.gpio.set_out['level'])
        self.assertTrue(self.database.select(table='temperature', column='heater_state', boolean_needed=True))

    def test_02_should_NOT_write_to_storage_if_delta_is_smaller_than_0_2(self):
        self.temperature.sensor.set_temperature(10.00)
        self.temperature.run()
        self.temperature.sensor.set_temperature(10.10)
        self.temperature.run()
        self.database.execute_que()
        self.assertEqual(10, self.database.select(table='temperature', column='temperature'))
        self.assertEqual(10, self.database.select(table='temperature_history', column='temperature'))
        self.assertIsInstance(datetime.strptime(self.database.select(table='temperature_history', column='date_time'), '%Y-%m-%d %H:%M:%S'), datetime)
        self.assertTrue(self.database.select(table='temperature', column='heater_state', boolean_needed=True))

    def test_03_should_write_to_storage_if_delta_is_equal_0_2(self):
        self.temperature.sensor.set_temperature(10.00)
        self.temperature.run()
        self.temperature.sensor.set_temperature(10.20)
        self.temperature.run()
        self.database.execute_que()
        self.assertEqual(10.2, self.database.select(table='temperature', column='temperature'))
        self.assertEqual(2, len(self.database.select(table='temperature_history', column='*', single=False)))
        self.assertEqual(10.2, self.database.select(table='temperature_history', column='*', single=False)[1][2])
        self.assertTrue(self.database.select(table='temperature', column='heater_state', boolean_needed=True))

    def test_04_should_write_to_storage_if_delta_is_above_0_2(self):
        self.temperature.sensor.set_temperature(10.00)
        self.temperature.run()
        self.temperature.sensor.set_temperature(10.30)
        self.temperature.run()
        self.database.execute_que()
        self.assertEqual(10.3, self.database.select(table='temperature', column='temperature'))
        self.assertEqual(2, len(self.database.select(table='temperature_history', column='*', single=False)))
        self.assertEqual(10.3, self.database.select(table='temperature_history', column='*', single=False)[1][2])
        self.assertTrue(self.database.select(table='temperature', column='heater_state', boolean_needed=True))

    def test_05_should_NOT_trigger_alarm_if_temp_is_below_alarm_level(self):
        self.temperature.sensor.set_temperature(10.0)
        self.temperature.run()
        self.database.execute_que()
        self.assertFalse(self.database.select(table='temperature', column='alarm', boolean_needed=True))
        self.assertTrue(self.database.select(table='temperature', column='heater_state', boolean_needed=True))

    def test_06_should_trigger_alarm_and_disable_heater_if_temp_is_equal_alarm_level(self):
        self.temperature.sensor.set_temperature(26.0)
        self.temperature.run()
        self.database.execute_que()
        self.assertTrue(self.database.select(table='temperature', column='alarm', boolean_needed=True))
        self.assertFalse(self.database.select(table='temperature', column='heater_state', boolean_needed=True))

    def test_07_should_trigger_alarm_and_disable_heater_if_temp_is_above_alarm_level(self):
        self.temperature.sensor.set_temperature(26.1)
        self.temperature.run()
        self.database.execute_que()
        self.assertTrue(self.database.select(table='temperature', column='alarm', boolean_needed=True))
        self.assertFalse(self.database.select(table='temperature', column='heater_state', boolean_needed=True))
        self.assertEqual(1, self.gpio.set_out['level'])

    def test_08_should_disable_alarm_and_run_heater_if_temp_fail_below_alarm_level_again(self):
        self.temperature.sensor.set_temperature(26.0)
        self.temperature.run()
        self.database.execute_que()
        self.assertTrue(self.database.select(table='temperature', column='alarm', boolean_needed=True))
        self.assertEqual(1, self.gpio.set_out['level'])
        self.assertFalse(self.database.select(table='temperature', column='heater_state', boolean_needed=True))
        self.temperature.sensor.set_temperature(25.0)
        self.temperature.run()
        self.database.execute_que()
        self.assertFalse(self.database.select(table='temperature', column='alarm', boolean_needed=True))
        self.assertEqual(0, self.gpio.set_out['level'])
        self.assertTrue(self.database.select(table='temperature', column='heater_state', boolean_needed=True))
