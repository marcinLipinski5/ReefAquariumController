from watchdog.auto_refill import AutoRefillWatchdog
from watchdog.feeding import FeedingWatchdog
from database.db import Database
from pins.gpio_setup import GPIOSetup


class Main:

    def __init__(self, database: Database, gpio: GPIOSetup ):
        self.auto_refill_watchdog = AutoRefillWatchdog(database, gpio)
        self.feeding_watchdog = FeedingWatchdog(database, gpio)

    def run(self):
        self.auto_refill_watchdog.run()
        self.feeding_watchdog.run()
