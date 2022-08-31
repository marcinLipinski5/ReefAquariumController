from watchdog.auto_refill import AutoRefillWatchdog


class Watchdog:

    def __init__(self):
        self.auto_refill_watchdog = AutoRefillWatchdog()

    def run(self):
        self.auto_refill_watchdog.run()
