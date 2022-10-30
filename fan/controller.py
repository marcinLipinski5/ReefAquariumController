import logging
import time

import RPi.GPIO as GPIO

from pins.IOPins import IOPins

# TODO fix me
class Controller:

    def __init__(self):
        self.fan_pwm = IOPins.FAN_PWM.value
        GPIO.setup(self.fan_pwm, GPIO.OUT)
        self.controller = GPIO.PWM(self.fan_pwm, 1024)
        self.controller.start(0)

        self.duty_cycle = 100  # 0 < duty_cycle < 100

    def update_duty_cycle(self, duty_cycle: int):
        self.duty_cycle = duty_cycle

    def __set_duty_cycle(self):
        self.controller.ChangeDutyCycle(self.duty_cycle)

    def run(self):
        for i in [10, 20, 30, 40, 50, 60, 70, 80, 90, 10]:
            logging.info(f"DUTY CYCLE: {i}")
            self.update_duty_cycle(i)
            self.__set_duty_cycle()
            time.sleep(5)