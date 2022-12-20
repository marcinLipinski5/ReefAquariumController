import datetime
import time

from database.db import Database
from sensors.auto_refill.flow_counter import FlowCounter
from tests.gpio_mock import GPIOSetup
from tests.test_runner import TestRunner


class TestFlowCounter(TestRunner):

    def setUp(self) -> None:
        super(TestFlowCounter, self).setUp()
        self.database = Database(':memory:')
        self.gpio = GPIOSetup()
        self.flow_counter = FlowCounter(self.database, self.gpio)
        self.database.update(table="auto_refill", column="refill_max_time_in_seconds", value=0.1)
        self.database.update(table="auto_refill", column="pulses_per_ml", value=0.5)
        self.database.execute_que()

    def test_01_should_add_and_delete_event_detect(self):
        self.flow_counter.run()
        self.database.execute_que()

        self.assertEqual(26, self.gpio.add_event_detect_out['gpio_number'])
        self.assertEqual('RISING', self.gpio.add_event_detect_out['event'])
        self.assertIn('FlowCounter.count_pulse', self.gpio.add_event_detect_out['callback'].__str__())
        self.assertEqual(26, self.gpio.remove_event_detect_out['gpio_number'])

    def test_02_on_first_run_should_update_database_historic_data(self):
        self.flow_counter.pulse_counter = 10
        self.flow_counter.run()
        self.database.execute_que()

        self.assertEqual(1, len(self.database.select(table='auto_refill_history', single=False)))
        self.assertEqual(self.database.select(table='auto_refill', column='flow_count_date'),
                         self.database.select(table='auto_refill_history', column='date'))
        self.assertEqual(20, self.database.select(table='auto_refill_history', column='flow')) # TODO change when real sensor support will be implemented

    def test_03_should_sum_flow_from_different_runs(self):
        self.flow_counter.pulse_counter = 10
        self.flow_counter.run()
        self.database.execute_que()
        self.assertEqual(20, self.database.select(table='auto_refill', column="daily_refill_flow"))

        self.flow_counter.pulse_counter = 10
        self.flow_counter.run()
        self.database.execute_que()
        self.assertEqual(40, self.database.select(table='auto_refill', column="daily_refill_flow"))
        self.assertEqual(1, len(self.database.select(table='auto_refill_history', single=False)))

    def test_04_should_save_historic_data_and_reset_flow_counter_if_next_day_appears(self):
        self.flow_counter.pulse_counter = 10
        self.flow_counter.run()
        self.database.execute_que()
        self.assertEqual(20, self.database.select(table='auto_refill', column="daily_refill_flow"))

        self.flow_counter.pulse_counter = 10
        self.flow_counter.run()
        self.database.execute_que()
        self.assertEqual(40, self.database.select(table='auto_refill', column="daily_refill_flow"))

        self.database.update(table='auto_refill',
                             column='flow_count_date',
                             value=(datetime.date.today() + datetime.timedelta(days=1)).strftime("%d-%m-%Y"))
        self.database.execute_que()
        self.flow_counter.pulse_counter = 10
        self.flow_counter.run()
        self.database.execute_que()
        self.assertEqual(0, self.database.select(table='auto_refill', column='daily_refill_flow'))
        self.assertEqual(datetime.date.today().strftime("%d-%m-%Y"),
                         self.database.select(table='auto_refill', column='flow_count_date'))
        self.assertEqual(2, len(self.database.select(table='auto_refill_history', single=False)))
        self.assertEqual(datetime.date.today().strftime("%d-%m-%Y"),
                         self.database.select(table='auto_refill_history', column='date', where='id = 2'))
        self.assertEqual(60, self.database.select(table='auto_refill_history', column='flow', where='id = 2'))

    def test_05_refill_time_should_follow_value_predefined_in_a_settings(self):
        self.database.update(table="auto_refill", column="refill_max_time_in_seconds", value=0.5)
        self.database.execute_que()
        time_start = time.time()
        self.flow_counter.run()
        time_stop = time.time()
        self.assertAlmostEquals(0.5, time_stop-time_start, delta=0.1)

    def test_06_should_use_event_record_callback_for_calculations(self):
        self.gpio.event_record_active_mode = True
        self.flow_counter.run()
        self.database.execute_que()
        self.assertEqual(2, self.database.select(table='auto_refill', column="daily_refill_flow"))

        self.flow_counter.run()
        self.database.execute_que()
        self.assertEqual(4, self.database.select(table='auto_refill', column="daily_refill_flow"))
