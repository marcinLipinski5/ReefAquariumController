import json
import logging
from datetime import datetime, date

from database.db import Database
from mqtt_publisher import MqttPublisher


# noinspection PyArgumentList
class Controller:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s  [%(threadName)s] [%(levelname)s] %(message)s |",
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler()
        ]
    )

    def __init__(self, database: Database):
        self.database = database
        self.mqtt_publisher = MqttPublisher()
        self.today = self.__get_current_date()
        self.scheduler = self.__create_scheduler()
        self.next_run = {"index": 999, "scheduler": {"start": self.__get_current_time()}}
        self.__check_pending_run()

    def run(self):
        # self.__update_after_user_interaction()
        # self.__update_after_new_scheduler_period_required()
        self.__run_pump_if_needed()

    def __run_pump_if_needed(self):
        if self.next_run["scheduler"]["start"] <= self.__get_current_time():
            logging.debug(f"running scheduler: {self.next_run}")
            self.__activate_pump()
            self.scheduler[self.next_run["index"]]["already_activated"] = True
            self.__check_pending_run()

    def __activate_pump(self):
        message = {"pump_number": self.next_run["scheduler"]["pump_number"]}
        calibration = self.database.select(table="peristaltic_pump", column="ml_per_second", where=f"pump_number = {message['pump_number']}")
        message["duration"] = float(self.next_run["scheduler"]["capacity"]) / float(calibration)
        logging.debug(message)
        # self.mqtt_publisher.send_message(str(message))

    def __update_after_user_interaction(self):
        if self.database.select(table="peristaltic_pump_general", column="update_needed", boolean_needed=True):
            logging.debug("Update peristaltic pump scheduler after user interaction")
            self.scheduler = self.__create_scheduler()
            self.__check_pending_run()
            self.database.update(table="peristaltic_pump_general", column="update_needed", value=False, boolean_needed=True)

    def __update_after_new_scheduler_period_required(self):
        if self.__get_current_date() > self.today:
            logging.debug("Update peristaltic pump scheduler after new period required")
            self.today = self.__get_current_date()
            self.scheduler = self.__create_scheduler()
            self.__check_pending_run()

    @staticmethod
    def __get_current_time():
        return str(datetime.now().strftime("%H:%M"))

    @staticmethod
    def __get_current_date():
        return date.today().strftime("%d-%m-%Y")

    def __check_pending_run(self):
        for index, pending_run in enumerate(self.scheduler):
            try:
                print(self.scheduler[self.next_run["index"]]["already_activated"])
                if self.scheduler[self.next_run["index"]]["already_activated"] is False:
                    logging.debug("Not activated yet.")
                    break
            except IndexError:
                logging.debug("Seems to be first run.")
            if pending_run["start"] > self.next_run["scheduler"]["start"] and pending_run["already_activated"] is not True:
                self.next_run["scheduler"] = pending_run
                self.next_run["index"] = index
                logging.debug(f"Next scheduler for peristaltic pump: {self.next_run}")
                break

    def __create_scheduler(self):
        logging.debug("Getting new scheduler for peristaltic pump")
        raw_pumps_info = self.database.select(table='peristaltic_pump', single=False)
        new_scheduler = []
        for pump_info in raw_pumps_info:
            pump_number = pump_info[1]
            pump_scheduler = list(json.loads(pump_info[2]).values())
            for pump_scheduler_value in pump_scheduler:
                pump_scheduler_value['pump_number'] = pump_number
                pump_scheduler_value['already_activated'] = False
                new_scheduler.append(pump_scheduler_value)
        return new_scheduler

    def __update_scheduler(self, pump_number: int, scheduler: dict):
        logging.info("Updating scheduler for peristaltic pump")
        self.database.update(
            table='peristaltic_pump',
            column="scheduler",
            value=str(scheduler),
            where=f"pump_number = {pump_number}")


if __name__ == "__main__":
    database = Database()
    controller = Controller(database)
    for i in range(0, 10):
        logging.error(f"AAAAAAAAAAAAAAAAAAAAA: i")
        controller.run()
