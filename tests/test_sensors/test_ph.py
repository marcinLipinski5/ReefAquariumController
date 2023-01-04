from database.db import Database

from tests.gpio_mock import GPIOSetup
from tests.test_runner import TestRunner
from unittest import mock
import sys
from unittest.mock import MagicMock

sys.modules['board'] = MagicMock()
sys.modules['busio'] = MagicMock()
from sensors.ph import Ph


class TestTemperature(TestRunner):

    def setUp(self) -> None:
        super(TestTemperature, self).setUp()
        self.database = Database(':memory:')
        self.gpio = GPIOSetup()
        self.ph = Ph(self.database)

    @mock.patch.object(Ph, '_Ph__get_ph_value')
    def test_01_should_read_and_store_ph_value(self, get_ph_value=mock.MagicMock):
        get_ph_value.return_value = 123.456
        self.ph.run()
        self.database.execute_que()

        self.assertEqual(123.456, self.database.select(table='ph', column='ph'))
        self.assertEqual(1, len(self.database.select(table='ph_history', single=False)))
        self.assertEqual(123.456, self.database.select(table='ph_history', column='ph'))

    @mock.patch.object(Ph, '_Ph__get_ph_value')
    def test_02_should_NOT_store_new_ph_value_if_delta_is_less_than_0_1(self, get_ph_value=mock.MagicMock):
        get_ph_value.return_value = 123.456
        self.ph.run()
        self.database.execute_que()

        get_ph_value.return_value = 123.457
        self.ph.run()
        self.database.execute_que()

        self.assertEqual(123.456, self.database.select(table='ph', column='ph'))
        self.assertEqual(1, len(self.database.select(table='ph_history', single=False)))
        self.assertEqual(123.456, self.database.select(table='ph_history', column='ph'))

    @mock.patch.object(Ph, '_Ph__get_ph_value')
    def test_03_should_store_new_ph_value_if_delta_is_less_than_0_1(self, get_ph_value=mock.MagicMock):
        get_ph_value.return_value = 123.456
        self.ph.run()
        self.database.execute_que()

        get_ph_value.return_value = 123.567
        self.ph.run()
        self.database.execute_que()

        self.assertEqual(123.567, self.database.select(table='ph', column='ph'))
        self.assertEqual(2, len(self.database.select(table='ph_history', single=False)))
        self.assertEqual(123.567, self.database.select(table='ph_history', column='ph', single=False)[1][0])

