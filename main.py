import logging
import threading
import RPi.GPIO as GPIO
import time
import traceback

from autoRefill.controller import Controller as AutoRefillController
from database.migrations import Migrations
from watchdog.watchdog import Watchdog


# noinspection PyArgumentList
class ReefAquariumController:

    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler("aquarium_log.log"),
                logging.StreamHandler()
            ]
        )

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        Migrations()
        self.auto_refill = AutoRefillController()
        self.watchdog = Watchdog()

        self.sensors_thread = threading.Thread(target=self.run_sensors, args=(), daemon=True)
        self.watchdog_thread = threading.Thread(target=self.run_watchdog, args=(), daemon=True)

    def run(self):
        self.sensors_thread.start()
        self.watchdog_thread.start()
        while True:
            time.sleep(100)

    def run_sensors(self):
        fail_counter = 0
        logging.info("Starting sensors thread")
        while fail_counter < 10:
            try:
                self.run_auto_refill()
                time.sleep(10)
                fail_counter = 0
            except:
                fail_counter += 1
                logging.error(f"Sensor thread failed! Attempt no: {fail_counter}\n{traceback.print_exc()}")
                if fail_counter == 10:
                    logging.error("Unable to run sensor thread")
                    raise

    def run_auto_refill(self):
        self.auto_refill.run()

    def run_watchdog(self):
        try:
            while True:
                self.watchdog.run()
                time.sleep(1)
        except:
            logging.error("Unable to run watchdog!")
            raise


if __name__ == "__main__":
    ReefAquariumController().run()