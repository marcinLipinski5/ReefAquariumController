import logging

try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    import Mock.GPIO as GPIO
from pins.IOPins import IOPins


class GPIOSetup:

    def __init__(self):
        # general
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # # fan section
        self.pwm = IOPins.FAN_PWM
        GPIO.setup(self.pwm.value, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pwm.value, 1024)
        self.pwm.start(0)

        # auto refill section
        self.water_level_sensor_down_value_main = IOPins.WATER_LEVEL_SENSOR_DOWN_VALUE_MAIN
        self.water_level_sensor_down_value_backup = IOPins.WATER_LEVEL_SENSOR_DOWN_VALUE_BACKUP
        self.water_level_sensor_up_value = IOPins.WATER_LEVEL_SENSOR_UP_VALUE
        self.water_pump_refill_relay = IOPins.WATER_PUMP_REFILL_RELAY
        self.limit_switch = IOPins.LIMIT_SWITCH
        GPIO.setup(self.water_level_sensor_down_value_main.value, GPIO.IN)
        GPIO.setup(self.water_level_sensor_down_value_backup.value, GPIO.IN)
        GPIO.setup(self.water_level_sensor_up_value.value, GPIO.IN)
        GPIO.setup(self.water_pump_refill_relay.value, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.limit_switch.value, GPIO.IN)

        # auto refill / flow counter
        self.water_pump_refill_flow_counter = IOPins.WATER_PUMP_REFILL_FLOW_COUNTER
        GPIO.setup(self.water_pump_refill_flow_counter.value, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # # feeding
        self.water_pump_relay = IOPins.WATER_PUMP_RELAY

        # # temperature
        self.heater_relay = IOPins.HEATER_RELAY

    # # fan
    def change_pwm(self, duty_cycle):
        self.pwm.ChangeDutyCycle(duty_cycle)

    # pulse counter
    @staticmethod
    def add_event_detect(gpio_number: int, event: str, callback):
        assert event in ['RISING']
        event = GPIO.RISING if event == 'RISING' else 'ERROR'
        GPIO.add_event_detect(gpio_number, event, callback=callback, bouncetime=10)

    @staticmethod
    def remove_event_detect(gpio_number: int):
        GPIO.remove_event_detect(gpio_number)

    # general
    @staticmethod
    def set(gpio_number: int, level: int):
        assert level in [0, 1]
        level = GPIO.LOW if level == 0 else GPIO.HIGH
        logging.debug(f"GPIO --> Setting state: {level} for GPIO: {IOPins(gpio_number).name}")
        GPIO.output(gpio_number, level)

    @staticmethod
    def get(gpio_number: int):
        return True if GPIO.input(gpio_number) == 1 else False

    @staticmethod
    def get_gpio_instance():
        return GPIO
