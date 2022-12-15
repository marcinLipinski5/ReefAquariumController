from database.db import Database
from sensors.feeding import Feeding
from tests.gpio_mock import GPIOSetup
from tests.test_runner import TestRunner
import time


class TestFeeding(TestRunner):

    def setUp(self) -> None:
        super(TestFeeding, self).setUp()
        self.database = Database(':memory:')
        self.mock = GPIOSetup()
        self.feeding = Feeding(self.database, self.mock)

    def test_01_should_stop_pump_if_it_is_feeding_time(self):
        self.database.update(table='feeding', column='water_pump_state', value=True, boolean_needed=True)
        self.database.update(table='feeding', column='is_feeding_time', value=True, boolean_needed=True)
        self.database.execute_que()
        self.feeding.run()
        self.database.execute_que()
        self.assertEqual(False, self.database.select(table='feeding', column='water_pump_state', boolean_needed=True))
        self.assertAlmostEqual(first=self.database.select(table='feeding', column='start_time'),
                               second=time.time(),
                               delta=0.9)
        self.assertEqual(1, self.mock.set_out['level'])

    def test_02_should_not_stop_pump_again_if_it_is_feeding_time_and_the_pump_is_already_stopped(self):
        self.database.update(table='feeding', column='water_pump_state', value=False, boolean_needed=True)
        self.database.update(table='feeding', column='is_feeding_time', value=True, boolean_needed=True)
        self.database.execute_que()
        self.feeding.run()
        self.database.execute_que()
        self.assertEqual('value not set', self.mock.set_out['level'])

    def test_03_should_start_pump_if_it_is_NOT_feeding_time_and_pump_is_stopped(self):
        self.database.update(table='feeding', column='water_pump_state', value=True, boolean_needed=True)
        self.database.update(table='feeding', column='is_feeding_time', value=True, boolean_needed=True)
        self.database.execute_que()
        self.feeding.run()
        self.database.execute_que()
        self.assertEqual(False, self.database.select(table='feeding', column='water_pump_state', boolean_needed=True))
        self.assertEqual(1, self.mock.set_out['level'])
        self.assertAlmostEqual(first=self.database.select(table='feeding', column='start_time'),
                               second=time.time(),
                               delta=0.9)
        self.database.update(table='feeding', column='is_feeding_time', value=False, boolean_needed=True)
        self.database.execute_que()
        self.feeding.run()
        self.database.execute_que()
        self.assertEqual(True, self.database.select(table='feeding', column='water_pump_state', boolean_needed=True))
        self.assertEqual(0, self.database.select(table='feeding', column='start_time'))
        self.assertEqual(0, self.mock.set_out['level'])

    def test_04_should_start_pump_if_time_is_exceeded(self):
        self.database.update(table='feeding', column='water_pump_state', value=True, boolean_needed=True)
        self.database.update(table='feeding', column='is_feeding_time', value=True, boolean_needed=True)
        self.database.update(table='feeding', column='feeding_duration', value=0.1)
        self.database.execute_que()
        self.feeding.run()
        self.database.execute_que()
        self.assertEqual(False, self.database.select(table='feeding', column='water_pump_state', boolean_needed=True))
        self.assertEqual(1, self.mock.set_out['level'])
        time.sleep(0.2)
        self.feeding.run()
        self.database.execute_que()
        self.assertEqual(True, self.database.select(table='feeding', column='water_pump_state', boolean_needed=True))
        self.assertEqual(0, self.mock.set_out['level'])

    def test_05_should_NOT_start_pump_if_time_is_NOT_exceeded(self):
        self.database.update(table='feeding', column='water_pump_state', value=True, boolean_needed=True)
        self.database.update(table='feeding', column='is_feeding_time', value=True, boolean_needed=True)
        self.database.execute_que()
        self.feeding.run()
        self.database.execute_que()
        self.assertEqual(False, self.database.select(table='feeding', column='water_pump_state', boolean_needed=True))
        self.assertEqual(1, self.mock.set_out['level'])
        self.feeding.run()
        self.database.execute_que()
        self.assertEqual(False, self.database.select(table='feeding', column='water_pump_state', boolean_needed=True))
        self.assertEqual(1, self.mock.set_out['level'])