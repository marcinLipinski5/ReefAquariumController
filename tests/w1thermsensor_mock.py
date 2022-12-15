class W1ThermSensor:

    def __init__(self):
        self.temperature = 0.0

    def get_temperature(self):
        return self.temperature

    def set_temperature(self, temperature: float):
        self.temperature = temperature
