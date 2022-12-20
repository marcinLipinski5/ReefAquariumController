from main import ReefAquariumController
from tests.test_runner import TestRunner
from database.db import Database
from server.main import Server
from sensors.auto_refill.controller import Controller as AutoRefillController
from sensors.temperature import Temperature as TemperatureController
from sensors.fan import Fan as FanController
from sensors.feeding import Feeding as FeedingController
from watchdog.main import Main as Watchdog


class TestMain(TestRunner):

    def setUp(self) -> None:
        super(TestMain, self).setUp()
        self.main = ReefAquariumController()

    # def test_01_should_create_database_object(self):
    #     self.assertIsInstance(self.main.database, Database)
    #
    # def test_02_should_create_server_object(self):
    #     self.assertIsInstance(self.main.server, Server)
    #
    # def test_03_should_create_auto_refill_object(self):
    #     self.assertIsInstance(self.main.auto_refill, AutoRefillController)
    #
    # def test_04_should_create_temperature_object(self):
    #     self.assertIsInstance(self.main.temperature, TemperatureController)
    #
    # def test_05_should_create_fan_object(self):
    #     self.assertIsInstance(self.main.fan, FanController)
    #
    # def test_06_should_create_feeding_object(self):
    #     self.assertIsInstance(self.main.feeding, FeedingController)
    #
    # def test_07_should_create_watchdog_object(self):
    #     self.assertIsInstance(self.main.watchdog, Watchdog)

    def test_08_should_run_threads(self):
        self.main.run()
        print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')