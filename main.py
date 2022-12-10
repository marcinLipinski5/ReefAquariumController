import logging
import threading
# import RPi.GPIO as GPIO
import time
# import traceback
#
# from auto_refill.controller import Controller as AutoRefillController
# from temperature.controller import Controller as TemperatureController
# from fan.controller import Controller as FanController
# from feeding.controller import Controller as FeedingController
from database.migrations import Migrations
# from watchdog.watchdog import Watchdog
from server.main import Server


# noinspection PyArgumentList
class ReefAquariumController:

    def __init__(self):
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.FileHandler("aquarium_log.log"),
                logging.StreamHandler()
            ]
        )

        # GPIO.setmode(GPIO.BCM)
        # GPIO.setwarnings(False)
        #
        # Migrations()
        # self.auto_refill = AutoRefillController()
        # self.temperature = TemperatureController()
        # self.fan = FanController()
        # self.feeding = FeedingController()
        # self.watchdog = Watchdog()
        self.server = Server()
        #
        # self.sensors_thread = threading.Thread(target=self.run_sensors, args=(), daemon=True)
        # self.watchdog_thread = threading.Thread(target=self.run_watchdog, args=(), daemon=True)
        self.server_thread = threading.Thread(target=self.run_server, args=(), daemon=True)

    def run(self):
        # self.sensors_thread.start()
        # self.watchdog_thread.start()
        self.server_thread.start()
        while True:
            time.sleep(100)

    # def run_sensors(self):
    #     fail_counter = 0
    #     logging.info("Starting sensors thread")
    #     while fail_counter < 10:
    #         try:
    #             self.run_temperature()
    #             self.run_auto_refill()
    #             self.run_fan()
    #             self.run_feeding()
    #             time.sleep(10)
    #             fail_counter = 0
    #         except:
    #             fail_counter += 1
    #             logging.error(f"Sensor thread failed! Attempt no: {fail_counter}\n{traceback.print_exc()}")
    #             if fail_counter == 10:
    #                 logging.error("Unable to run sensor thread")
    #                 raise
    #
    # def run_fan(self):
    #     self.fan.run()
    #
    # def run_temperature(self):
    #     self.temperature.run()
    #
    # def run_auto_refill(self):
    #     self.auto_refill.run()
    #
    # def run_feeding(self):
    #     self.feeding.run()
    #
    # def run_watchdog(self):
    #     logging.info("Starting watchdog thread")
    #     try:
    #         while True:
    #             self.watchdog.run()
    #             time.sleep(5)
    #     except:
    #         logging.error("Unable to run watchdog!")
    #         raise

    def run_server(self):
        logging.info("Starting server thread")
        try:
            self.server.run()
        except:
            logging.error("Unable to run server")
            raise

#
#
if __name__ == "__main__":
    # Migrations()
    ReefAquariumController().run()


def socket_():
    return None