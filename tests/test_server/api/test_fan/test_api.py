import time
import unittest
from server.main import Server
from database.db import Database


class TestApi(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.database = Database(':memory:')
        cls.api = Server(cls.database).get_test_instance()

    def test_01_should_return_status(self):
        answer = self.api.get('/fan/status')
        self.assertEqual(answer.status, '200 OK')
        self.assertEqual(answer.json, {'duty_cycle': 100, 'level': 'alarm'})

    def test_02_should_return_settings(self):
        answer = self.api.get('/fan/settings')
        self.assertEqual(answer.status, '200 OK')
        self.assertEqual(answer.json, {'alarm_level_duty_cycle': 100, 'freeze_level_duty_cycle': 50, 'normal_level_duty_cycle': 80})

    def test_03_should_update_settings(self):
        answer_post = self.api.post('/fan/settings', data={'alarm_level': 101, 'freeze_level': 51, 'normal_level': 81})
        self.assertEqual(answer_post.status, '302 FOUND')
        self.database.execute_que()
        answer_get = self.api.get('/fan/settings')
        self.assertEqual(answer_get.status, '200 OK')
        self.assertEqual(answer_get.json, {'alarm_level_duty_cycle': 101, 'freeze_level_duty_cycle': 51, 'normal_level_duty_cycle': 81})
