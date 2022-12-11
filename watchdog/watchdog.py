from auto_refill import AutoRefillWatchdog
from feeding import FeedingWatchdog


class Watchdog:

    def __init__(self, database):
        self.auto_refill_watchdog = AutoRefillWatchdog(database)
        self.feeding_watchdog = FeedingWatchdog(database)

    def run(self):
        self.auto_refill_watchdog.run()
        self.feeding_watchdog.run()
