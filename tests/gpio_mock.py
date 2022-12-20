from pins.IOPins import IOPins
import logging


class GPIOSetup:

    def __init__(self):
        logging.info('Starting GPIO mock.')
        # fan section
        self.pwm = IOPins.FAN_PWM

        # auto refill section
        self.water_level_sensor_down_value_main = IOPins.WATER_LEVEL_SENSOR_DOWN_VALUE_MAIN
        self.water_level_sensor_down_value_backup = IOPins.WATER_LEVEL_SENSOR_DOWN_VALUE_BACKUP
        self.water_level_sensor_up_value = IOPins.WATER_LEVEL_SENSOR_UP_VALUE
        self.water_pump_refill_relay = IOPins.WATER_PUMP_REFILL_RELAY
        self.limit_switch = IOPins.LIMIT_SWITCH

        # auto refill / flow counter
        self.water_pump_refill_flow_counter = IOPins.WATER_PUMP_REFILL_FLOW_COUNTER

        # feeding
        self.water_pump_relay = IOPins.WATER_PUMP_RELAY

        # temperature
        self.heater_relay = IOPins.HEATER_RELAY

        # output capture
        self.event_record_active_mode = False
        self.gpio_status = {}
        self.change_pwm_out = {'duty_cycle': 'value not set'}
        self.add_event_detect_out = {'gpio_number': 'value not set', 'event': 'value not set', 'callback': 'value not set'}
        self.remove_event_detect_out = {'gpio_number': 'value not set'}
        self.set_out = {'gpio_number': 'value not set', 'level': 'value not set'}

    def change_pwm(self, duty_cycle):
        self.change_pwm_out['duty_cycle'] = duty_cycle

    def add_event_detect(self, gpio_number: int, event: str, callback):
        self.add_event_detect_out['gpio_number'] = gpio_number
        self.add_event_detect_out['event'] = event
        self.add_event_detect_out['callback'] = callback
        if self.event_record_active_mode:
            callback(None)

    def remove_event_detect(self, gpio_number: int):
        self.remove_event_detect_out['gpio_number'] = gpio_number

    def set(self, gpio_number: int, level: int):
        self.mock_gpio_status(gpio_number, level)
        self.set_out['gpio_number'] = gpio_number
        self.set_out['level'] = level

    def get(self, gpio_number: int):
        return self.gpio_status[gpio_number]

    def mock_gpio_status(self, pin_number: int, status: int):
        assert status in [0, 1]
        self.gpio_status[pin_number] = status
