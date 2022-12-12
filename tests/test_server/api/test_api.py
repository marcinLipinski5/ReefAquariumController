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

# Fan API section

    def test_01_fan_should_return_status(self):
        answer = self.api.get('/fan/status')
        self.assertEqual(answer.status, '200 OK')
        self.assertEqual(answer.json, {'duty_cycle': 100, 'level': 'alarm'})

    def test_02_fan_should_return_settings(self):
        answer = self.api.get('/fan/settings')
        self.assertEqual(answer.status, '200 OK')
        self.assertEqual(answer.json, {'alarm_level_duty_cycle': 100, 'freeze_level_duty_cycle': 50, 'normal_level_duty_cycle': 80})

    def test_03_fan_should_update_settings(self):
        answer_post = self.api.post('/fan/settings', data={'alarm_level': 101, 'freeze_level': 51, 'normal_level': 81})
        self.assertEqual(answer_post.status, '302 FOUND')
        self.database.execute_que()
        self.assertEqual(self.database.select(table='fan', column='alarm_level_duty_cycle'), 101)
        self.assertEqual(self.database.select(table='fan', column='freeze_level_duty_cycle'), 51)
        self.assertEqual(self.database.select(table='fan', column='normal_level_duty_cycle'), 81)
        answer_get = self.api.get('/fan/settings')
        self.assertEqual(answer_get.status, '200 OK')
        self.assertEqual(answer_get.json, {'alarm_level_duty_cycle': 101, 'freeze_level_duty_cycle': 51, 'normal_level_duty_cycle': 81})

#  Temperature API section

    def test_04_temperature_should_return_status(self):
        answer = self.api.get('temperature/status')
        self.assertEqual(answer.status, '200 OK')
        self.assertEqual(answer.json, {'alarm': False, 'temperature': 0.0})

    def test_05_temperature_should_return_settings(self):
        answer = self.api.get('temperature/settings')
        self.assertEqual(answer.status, '200 OK')
        self.assertEqual(answer.json, {'alarm_level': 26.0})

    def test_06_temperature_should_update_settings(self):
        answer_post = self.api.post('temperature/settings', data={'alarm_level': 21})
        self.assertEqual(answer_post.status, '302 FOUND')
        self.database.execute_que()
        self.assertEqual(self.database.select(table='temperature', column='alarm_level'), 21)
        answer_get = self.api.get('/temperature/settings')
        self.assertEqual(answer_get.status, '200 OK')
        self.assertEqual(answer_get.json, {'alarm_level': 21.0})

#  Feeding API section

    def test_07_feeding_start_should_start_feeding(self):
        answer_post = self.api.post('feeding/start', json={'activate': True})
        self.assertEqual(answer_post.status, '200 OK')
        self.database.execute_que()
        self.assertEqual(self.database.select(table='feeding', column='is_feeding_time', boolean_needed=True), True)
        self.temps['feeding_time_started'] = self.database.select(table='feeding', column='start_time')
        self.assertAlmostEqual(first=self.temps['feeding_time_started'],
                               second=time(),
                               delta=0.9)

    def test_08_feeding_start_should_do_nothing_when_feeding_is_already_active(self):
        answer_post = self.api.post('feeding/start', json={'activate': True})
        self.assertEqual(answer_post.status, '304 NOT MODIFIED')
        self.database.execute_que()
        self.assertEqual(self.database.select(table='feeding', column='is_feeding_time', boolean_needed=True), True)
        self.assertEqual(self.database.select(table='feeding', column='start_time'), self.temps['feeding_time_started'])

    def test_09_should_return_status_when_feeding_is_active(self):
        answer = self.api.get('feeding/status')
        self.assertEqual(answer.status, '200 OK')
        self.assertEqual(self.database.select(table='feeding', column='is_feeding_time', boolean_needed=True), True)
        self.assertNotEqual(answer.json['remaining_time'], 0.0)
        self.assertAlmostEqual(first=answer.json['remaining_time'],
                               second=round(self.database.select(table='feeding', column='feeding_duration')
                                            - (time() - self.database.select(table='feeding', column='start_time'))),
                               places=5)

    def test_10_feeding_stop_should_stop_feeding(self):
        answer_post = self.api.post('feeding/start', json={'activate': False})
        self.assertEqual(answer_post.status, '200 OK')
        self.database.execute_que()
        self.assertEqual(self.database.select(table='feeding', column='is_feeding_time', boolean_needed=True), False)
        self.assertEqual(self.database.select(table='feeding', column='start_time'), 0.0)

    def test_11_feeding_should_return_status_when_feeding_is_inactive(self):
        answer = self.api.get('feeding/status')
        self.assertEqual(answer.status, '200 OK')
        self.assertEqual(answer.json, {'feeding_duration': 600, 'is_feeding_time': False, 'remaining_time': 600})

    def test_11_feeding_should_return_settings(self):
        answer = self.api.get('feeding/settings')
        self.assertEqual(answer.status, '200 OK')
        self.assertEqual(answer.json, {'feeding_duration': 600})

    def test_12_feeding_should_update_settings(self):
        answer_post = self.api.post('feeding/settings', data={'feeding_time': 601})
        self.assertEqual(answer_post.status, '302 FOUND')
        self.database.execute_que()
        self.assertEqual(self.database.select(table='feeding', column='feeding_duration'), 601)


