from enum import Enum, unique


@unique
class IOPins(Enum):
    WATER_LEVEL_SENSOR_DOWN_VALUE_MAIN = 17
    WATER_LEVEL_SENSOR_DOWN_VALUE_BACKUP = 27
    WATER_LEVEL_SENSOR_UP_VALUE = 22
    WATER_PUMP_REFILL_RELAY = 5
    WATER_PUMP_REFILL_FLOW_COUNTER = 26
    TEMPERATURE_SENSOR = 4
    FAN_PWM = 12
    WATER_PUMP_RELAY = 2137
    LIMIT_SWITCH = 2138
    HEATER_RELAY = 2139
    # 7
    # 8
    # 9
    # 10
    # 11
    # 12
    # 13
    # 14
    # 15
    # 16
    # 17
    # 18
    # 19
    # 20
    # 21
    # 22
    # 23
    # 24
    # 25
    # 27
    # 28
