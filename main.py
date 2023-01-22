import logging
import threading
import time
import traceback
import os
import requests

from sensors.auto_refill.controller import Controller as AutoRefillController
from sensors.temperature import Temperature as TemperatureController
from sensors.fan import Fan as FanController
from sensors.feeding import Feeding as FeedingController
from sensors.ph import Ph as PhController
from watchdog.main import Main as Watchdog
from server.main import Server
from database.db import Database
from pins.gpio_setup import GPIOSetup
from send_email import SendEmail


# noinspection PyArgumentList
class ReefAquariumController:

    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s  [%(threadName)s] [%(levelname)s] %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.FileHandler(os.path.join(os.path.dirname(__file__), "aquarium_log.log")),
                logging.StreamHandler()
            ]
        )

        gpio = GPIOSetup()
        self.database = Database()
        self.auto_refill = AutoRefillController(self.database, gpio)
        self.temperature = TemperatureController(self.database, gpio)
        self.fan = FanController(self.database, gpio)
        self.feeding = FeedingController(self.database, gpio)
        self.ph = PhController(self.database)
        self.watchdog = Watchdog(self.database, gpio)
        self.server = Server(self.database)

        self.database_thread = threading.Thread(target=self.update_database, args=(), daemon=True, name='database_thread')
        self.sensors_thread = threading.Thread(target=self.run_sensors, args=(), daemon=True, name='sensors_thread')
        self.watchdog_thread = threading.Thread(target=self.run_watchdog, args=(), daemon=True, name='watchdog_thread')
        self.server_thread = threading.Thread(target=self.run_server, args=(), daemon=True, name='server_thread')

    def run(self):
        try:
            self.get_ngrok()
            self.database_thread.start()
            self.sensors_thread.start()
            self.watchdog_thread.start()
            self.server_thread.start()
            while True:
                active_threads = []
                for thread in threading.enumerate():
                    active_threads.append(thread.name)
                try:
                    assert 'database_thread' in active_threads
                    assert 'sensors_thread' in active_threads
                    assert 'watchdog_thread' in active_threads
                    assert 'server_thread' in active_threads
                except AssertionError:
                    logging.error(f"Some threads are missing in {threading.enumerate()}. Restarting...")
                    break
                time.sleep(1)
        except:
            logging.error("Critical error. Closing down application")
        finally:
            GPIOSetup.get_gpio_instance().cleanup()
            pass

    def run_sensors(self):
        fail_counter = 0
        logging.info("Starting sensors thread")
        while fail_counter < 10:
            try:
                logging.debug('############ SENSOR ITERATION ############')
                self.temperature.run()
                self.auto_refill.run()
                self.fan.run()
                self.feeding.run()
                self.ph.run()
                time.sleep(10)
                fail_counter = 0
            except:
                fail_counter += 1
                logging.error(f"Sensor thread failed! Attempt no: {fail_counter}\n{traceback.print_exc()}")
                if fail_counter == 10:
                    logging.error("Unable to run sensor thread")
                    raise

    def run_watchdog(self):
        logging.info("Starting watchdog thread")
        try:
            while True:
                self.watchdog.run()
                time.sleep(5)
        except:
            logging.error("Unable to run watchdog!")
            raise

    def update_database(self):
        while True:
            self.database.execute_que()
            time.sleep(0.5)

    def run_server(self):
        logging.info("Starting server thread")
        try:
            self.server.run()
        except:
            logging.error("Unable to run server")
            raise

    @staticmethod
    def get_ngrok():
        counter = 10
        while counter > 0:
            try:
                logging.info("Collecting new ngrok url.")
                answer = requests.get("http://localhost:4040/api/tunnels")
                assert answer.status_code == 200
                url = answer.json()['tunnels'][0]['public_url']
                logging.info(f"Ngrok url successfully collected. New url: {url}")
                SendEmail(subject='Ngrok new url', body=f'Ngrok new url: {url}')
                break
            except AssertionError:
                logging.warning(f'Unable to collect new ngrok url. The process will be repeated: {counter} times.')
                time.sleep(2)
                counter -= 1


if __name__ == "__main__":
    ReefAquariumController().run()

