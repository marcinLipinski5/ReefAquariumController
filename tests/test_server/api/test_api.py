from tests.test_runner import TestRunner
from database.db import Database
from server.main import Server
from time import time, sleep


class TestApi(TestRunner):

    @classmethod
    def setUpClass(cls):
        super(TestRunner, cls).setUpClass()
        cls.database = Database(':memory:')
        cls.api = Server(cls.database).get_test_instance()
        cls.temps = {}

# General API

    def test_0_01_get_index_html(self):
        answer = self.api.get('/')
        self.assertEqual(answer.status, '200 OK')
        self.assertEqual(answer.content_type, 'text/html; charset=utf-8')

# Fan API section

    def test_fan_01_should_return_status(self):
        answer = self.api.get('/fan/status')
        self.assertEqual(answer.status, '200 OK')
        self.assertEqual(answer.json, {'duty_cycle': 100, 'level': 'alarm'})

    def test_fan_02_should_return_settings(self):
        answer = self.api.get('/fan/settings')
        self.assertEqual(answer.status, '200 OK')
        self.assertEqual(answer.json, {'alarm_level_duty_cycle': 100, 'freeze_level_duty_cycle': 50, 'normal_level_duty_cycle': 80})

    def test_fan_03_should_update_settings(self):
        answer_post = self.api.post('/fan/settings', data={'alarm_level': 101, 'freeze_level': 51, 'normal_level': 81})
        self.assertEqual(answer_post.status, '302 FOUND')
        self.database.execute_que()
        self.assertEqual(self.database.select(table='fan', column='alarm_level_duty_cycle'), 101)
        self.assertEqual(self.database.select(table='fan', column='freeze_level_duty_cycle'), 51)
        self.assertEqual(self.database.select(table='fan', column='normal_level_duty_cycle'), 81)
        answer_get = self.api.get('/fan/settings')
        self.assertEqual(answer_get.status, '200 OK')
        self.assertEqual(answer_get.json, {'alarm_level_duty_cycle': 101, 'freeze_level_duty_cycle': 51, 'normal_level_duty_cycle': 81})

    def test_fan_04_settings_should_return_wrong_method_http_code(self):
        answer = self.api.put('/fan/settings')
        self.assertEqual(answer.status, '405 METHOD NOT ALLOWED')
        answer = self.api.head('/fan/settings')
        self.assertEqual(answer.status, '405 METHOD NOT ALLOWED')
        answer = self.api.delete('/fan/settings')
        self.assertEqual(answer.status, '405 METHOD NOT ALLOWED')

#  Temperature API section

    def test_temperature_01_should_return_status(self):
        answer = self.api.get('temperature/status')
        self.assertEqual(answer.status, '200 OK')
        self.assertEqual(answer.json, {'alarm': False, 'temperature': 0.0})

    def test_temperature_02_should_return_settings(self):
        answer = self.api.get('temperature/settings')
        self.assertEqual(answer.status, '200 OK')
        self.assertEqual(answer.json, {'alarm_level': 26.0})

    def test_temperature_03_should_update_settings(self):
        answer_post = self.api.post('temperature/settings', data={'alarm_level': 21})
        self.assertEqual(answer_post.status, '302 FOUND')
        self.database.execute_que()
        self.assertEqual(self.database.select(table='temperature', column='alarm_level'), 21)
        answer_get = self.api.get('/temperature/settings')
        self.assertEqual(answer_get.status, '200 OK')
        self.assertEqual(answer_get.json, {'alarm_level': 21.0})

    def test_temperature_04_should_return_wrong_method_http_code(self):
        answer = self.api.put('/temperature/settings')
        self.assertEqual(answer.status, '405 METHOD NOT ALLOWED')
        answer = self.api.head('/temperature/settings')
        self.assertEqual(answer.status, '405 METHOD NOT ALLOWED')
        answer = self.api.delete('/temperature/settings')
        self.assertEqual(answer.status, '405 METHOD NOT ALLOWED')

#  Feeding API section

    def test_feeding_01_start_should_start_feeding(self):
        answer_post = self.api.post('feeding/start', json={'activate': True})
        self.assertEqual(answer_post.status, '200 OK')
        self.database.execute_que()
        self.assertEqual(self.database.select(table='feeding', column='is_feeding_time', boolean_needed=True), True)
        self.database.update(table='feeding', column='start_time', value=time())

    def test_feeding_02_start_should_do_nothing_when_feeding_is_already_active(self):
        answer_post = self.api.post('feeding/start', json={'activate': True})
        self.assertEqual(answer_post.status, '304 NOT MODIFIED')
        self.database.execute_que()
        self.assertEqual(self.database.select(table='feeding', column='is_feeding_time', boolean_needed=True), True)

    def test_feeding_03_should_return_status_when_feeding_is_active(self):
        answer = self.api.get('feeding/status')
        self.assertEqual(answer.status, '200 OK')
        self.assertEqual(self.database.select(table='feeding', column='is_feeding_time', boolean_needed=True), True)
        self.assertNotEqual(answer.json['remaining_time'], 0.0)

    def test_feeding_04_should_return_error_when_calculation_is_beyond_zero(self):
        self.database.update(table='feeding', column='feeding_duration', value=-100)
        print(self.database.select(table='feeding', column='start_time'))
        self.database.execute_que()
        answer = self.api.get('feeding/status')
        self.database.execute_que()
        self.assertEqual(answer.status, '200 OK')
        self.assertEqual(self.database.select(table='feeding', column='is_feeding_time', boolean_needed=True), False)
        self.assertEqual(answer.json['remaining_time'], -100)

    def test_feeding_05_stop_should_stop_feeding(self):
        self.database.update(table='feeding', column='feeding_duration', value=600)
        self.database.execute_que()
        answer_post = self.api.post('feeding/start', json={'activate': False})
        self.assertEqual(answer_post.status, '200 OK')
        self.database.execute_que()
        self.assertEqual(self.database.select(table='feeding', column='is_feeding_time', boolean_needed=True), False)

    def test_feeding_06_should_return_status_when_feeding_is_inactive(self):
        answer = self.api.get('feeding/status')
        self.assertEqual(answer.status, '200 OK')
        self.assertEqual(answer.json, {'feeding_duration': 600, 'is_feeding_time': False, 'remaining_time': 600})

    def test_feeding_07_should_return_settings(self):
        answer = self.api.get('feeding/settings')
        self.assertEqual(answer.status, '200 OK')
        self.assertEqual(answer.json, {'feeding_duration': 600})

    def test_feeding_08_should_update_settings(self):
        answer_post = self.api.post('feeding/settings', data={'feeding_time': 601})
        self.assertEqual(answer_post.status, '302 FOUND')
        self.database.execute_que()
        self.assertEqual(self.database.select(table='feeding', column='feeding_duration'), 601)

    def test_feeding_09_should_return_wrong_method_http_code(self):
        answer = self.api.put('/feeding/settings')
        self.assertEqual(answer.status, '405 METHOD NOT ALLOWED')
        answer = self.api.head('/feeding/settings')
        self.assertEqual(answer.status, '405 METHOD NOT ALLOWED')
        answer = self.api.delete('/feeding/settings')
        self.assertEqual(answer.status, '405 METHOD NOT ALLOWED')

# Auto Refill API section

    def test_auto_refill_01_should_return_status(self):
        answer = self.api.get('auto_refill/status')
        self.assertEqual(answer.status, '200 OK')
        self.assertEqual(answer.json, {'alarm': False, 'daily_refill_flow': 0.0})

    def test_auto_refill_02_should_return_settings(self):
        answer = self.api.get('auto_refill/settings')
        self.assertEqual(answer.status, '200 OK')
        self.assertEqual(answer.json, {'max_daily_refill_flow': 1000, 'refill_max_time_in_seconds': 10})

    def test_auto_refill_03_should_update_settings(self):
        answer_post = self.api.post('auto_refill/settings', data={'max_daily_refill_flow': 1001, 'refill_max_time_in_seconds': 11})
        self.assertEqual(answer_post.status, '302 FOUND')
        self.database.execute_que()
        self.assertEqual(self.database.select(table='auto_refill', column='max_daily_refill_flow'), 1001)
        self.assertEqual(self.database.select(table='auto_refill', column='refill_max_time_in_seconds'), 11)
        answer_get = self.api.get('auto_refill/settings')
        self.assertEqual(answer_get.status, '200 OK')
        self.assertEqual(answer_get.json, {'max_daily_refill_flow': 1001, 'refill_max_time_in_seconds': 11})

    def test_auto_refill_04_should_return_wrong_method_http_code(self):
        answer = self.api.put('/auto_refill/settings')
        self.assertEqual(answer.status, '405 METHOD NOT ALLOWED')
        answer = self.api.head('/feeding/settings')
        self.assertEqual(answer.status, '405 METHOD NOT ALLOWED')
        answer = self.api.delete('/feeding/settings')
        self.assertEqual(answer.status, '405 METHOD NOT ALLOWED')
