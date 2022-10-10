from auto_refill import AutoRefillWatchdog
from feeding import FeedingWatchdog


class Watchdog:

    def __init__(self):
        self.auto_refill_watchdog = AutoRefillWatchdog()
        self.feeding_watchdog = FeedingWatchdog()

    def run(self):
        self.auto_refill_watchdog.run()
        self.feeding_watchdog.run()
