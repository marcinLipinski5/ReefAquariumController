import time
from unittest import mock

from database.db import Database
from sensors.auto_refill.controller import Controller
from tests.gpio_mock import GPIOSetup
from tests.test_runner import TestRunner


class TestController(TestRunner):

    def setUp(self) -> None:
        super(TestController, self).setUp()
        self.database = Database(':memory:')
        self.gpio = GPIOSetup()
        self.controller = Controller(self.database, self.gpio)

    def test_01_should_do_nothing_if_limit_switch_is_open(self):
        self.gpio.mock_gpio_status(self.gpio.limit_switch.value, 1)
        self.controller.run()
        self.database.execute_que()
        self.assertTrue(self.database.select(table='auto_refill', column='limit_switch_state', boolean_needed=True))
        with self.assertRaises(KeyError): self.gpio.get(self.gpio.water_pump_refill_relay.value)

    def test_02_should_set_alarm_if_level_sensor_up_value_is_on(self):
        self.assertFalse(self.database.select(table='auto_refill', column='alarm', boolean_needed=True))
        self.gpio.mock_gpio_status(self.gpio.limit_switch.value, 0)
        self.gpio.mock_gpio_status(self.gpio.water_level_sensor_up_value.value, 1)
        self.controller.run()
        self.database.execute_que()
        self.assertTrue(self.database.select(table='auto_refill', column='alarm', boolean_needed=True))

    def test_03_should_set_alarm_if_daily_refill_flow_is_reached(self):
        self.assertFalse(self.database.select(table='auto_refill', column='alarm', boolean_needed=True))
        self.gpio.mock_gpio_status(self.gpio.limit_switch.value, 0)
        self.gpio.mock_gpio_status(self.gpio.water_level_sensor_up_value.value, 0)
        self.database.update(table='auto_refill', column='daily_refill_flow', value=1001)
        self.database.execute_que()
        self.controller.run()
        self.database.execute_que()
        self.assertTrue(self.database.select(table='auto_refill', column='alarm', boolean_needed=True))

    @mock.patch.object(Controller, '_Controller__run_flow_counter')
    def test_04_should_NOT_activate_pump_if_only_main_sensor_is_active(self, run_flow_counter=mock.MagicMock):
        self.gpio.mock_gpio_status(self.gpio.limit_switch.value, 0)
        self.gpio.mock_gpio_status(self.gpio.water_level_sensor_up_value.value, 0)
        self.gpio.mock_gpio_status(self.gpio.water_level_sensor_down_value_main.value, 1)
        self.gpio.mock_gpio_status(self.gpio.water_level_sensor_down_value_backup.value, 0)
        self.controller.run()
        self.database.execute_que()

        self.assertEqual(0.0, self.database.select(table='auto_refill', column='refill_time_start'))
        with self.assertRaises(KeyError): self.gpio.get(self.gpio.water_pump_refill_relay.value)
        self.assertFalse(self.database.select(table='auto_refill', column='alarm', boolean_needed=True))
        run_flow_counter.assert_not_called()

    @mock.patch.object(Controller, '_Controller__run_flow_counter')
    def test_05_should_NOT_activate_pump_if_only_backup_sensor_is_active(self, run_flow_counter=mock.MagicMock):
        self.gpio.mock_gpio_status(self.gpio.limit_switch.value, 0)
        self.gpio.mock_gpio_status(self.gpio.water_level_sensor_up_value.value, 0)
        self.gpio.mock_gpio_status(self.gpio.water_level_sensor_down_value_main.value, 0)
        self.gpio.mock_gpio_status(self.gpio.water_level_sensor_down_value_backup.value, 1)
        self.controller.run()
        self.database.execute_que()

        self.assertEqual(0.0, self.database.select(table='auto_refill', column='refill_time_start'))
        with self.assertRaises(KeyError): self.gpio.get(self.gpio.water_pump_refill_relay.value)
        self.assertFalse(self.database.select(table='auto_refill', column='alarm', boolean_needed=True))
        run_flow_counter.assert_not_called()

    @mock.patch.object(Controller, '_Controller__run_flow_counter')
    def test_06_should_NOT_activate_pump_if_all_level_sensors_are_active_active(self, run_flow_counter=mock.MagicMock):
        self.gpio.mock_gpio_status(self.gpio.limit_switch.value, 0)
        self.gpio.mock_gpio_status(self.gpio.water_level_sensor_up_value.value, 1)
        self.gpio.mock_gpio_status(self.gpio.water_level_sensor_down_value_main.value, 1)
        self.gpio.mock_gpio_status(self.gpio.water_level_sensor_down_value_backup.value, 1)
        self.controller.run()
        self.database.execute_que()

        self.assertEqual(0.0, self.database.select(table='auto_refill', column='refill_time_start'))
        with self.assertRaises(KeyError): self.gpio.get(self.gpio.water_pump_refill_relay.value)
        self.assertTrue(self.database.select(table='auto_refill', column='alarm', boolean_needed=True))
        run_flow_counter.assert_not_called()

    @mock.patch.object(Controller, '_Controller__run_flow_counter')
    def test_07_should_activate_pump_if_main_and_backup_sensors_are_active_active(self, run_flow_counter=mock.MagicMock):
        self.gpio.mock_gpio_status(self.gpio.limit_switch.value, 0)
        self.gpio.mock_gpio_status(self.gpio.water_level_sensor_up_value.value, 0)
        self.gpio.mock_gpio_status(self.gpio.water_level_sensor_down_value_main.value, 1)
        self.gpio.mock_gpio_status(self.gpio.water_level_sensor_down_value_backup.value, 1)
        self.controller.run()
        expected_db_que = ['UPDATE auto_refill SET limit_switch_state = 0',
                           'UPDATE auto_refill SET water_level_sensor_up_value_state = 0',
                           'UPDATE auto_refill SET alarm = 0',
                           'UPDATE auto_refill SET water_level_sensor_down_value_main_state = 1',
                           'UPDATE auto_refill SET water_level_sensor_down_value_backup_state = 1',
                           f'UPDATE auto_refill SET refill_time_start = {time.time()}',
                           'UPDATE auto_refill SET water_pump_refill_relay_state = 1',
                           'UPDATE auto_refill SET water_pump_refill_relay_state = 0',
                           'UPDATE auto_refill SET refill_time_start = 0.0']
        que = self.database.get_que()
        expected_time_start = float(expected_db_que.pop(5).replace("UPDATE auto_refill SET refill_time_start = ", ""))
        received_time_start = float(que.pop(5).replace("UPDATE auto_refill SET refill_time_start = ", ""))
        self.assertAlmostEquals(expected_time_start, received_time_start, delta=0.1)
        self.assertListEqual(expected_db_que, expected_db_que)
        self.database.execute_que()

        self.assertEqual(0.0, self.database.select(table='auto_refill', column='refill_time_start'))
        self.assertEqual(0, self.gpio.get(self.gpio.water_pump_refill_relay.value))
        self.assertFalse(self.database.select(table='auto_refill', column='alarm', boolean_needed=True))
        run_flow_counter.assert_called_once()

