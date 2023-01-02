from database.db import Database
from sensors.ph.controller import Controller as Ph
from tests.gpio_mock import GPIOSetup
from tests.test_runner import TestRunner
from datetime import datetime
from unittest import mock


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




