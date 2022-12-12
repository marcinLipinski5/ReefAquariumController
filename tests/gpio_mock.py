class GPIOSetup:

    gpio_status = 0
    change_pwm_out = {}
    add_event_detect_out = {}
    remove_event_detect_out = {}
    set_out = {}

    def change_pwm(self, duty_cycle):
        self.change_pwm_out['duty_cycle'] = duty_cycle

    def add_event_detect(self, gpio_number: int, event: str, callback):
        self.add_event_detect_out['gpio_number'] = gpio_number
        self.add_event_detect_out['event'] = event
        self.add_event_detect_out['callback'] = callback

    def remove_event_detect(self, gpio_number: int):
        self.remove_event_detect_out['gpio_number'] = gpio_number

    def set(self, gpio_number: int, level: int):
        self.set_out['gpio_number'] = gpio_number
        self.set_out['level'] = level

    def get(self, gpio_number: int):
        return self.gpio_status

    def mock_gpio_status(self, status: int):
        assert status in [0, 1]
        self.gpio_status = status
