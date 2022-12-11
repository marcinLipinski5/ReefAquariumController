create TABLE info(
    migration TEXT,
    description TEXT);

CREATE TABLE auto_refill(
    id INTEGER PRIMARY KEY,
    alarm INTEGER NOT NULL,
    daily_refill_flow INTEGER NOT NULL,
    max_daily_refill_flow INTEGER NOT NULL,
    flow_count_date DATE,
    refill_time_start REAL NOT NULL,
    refill_max_time_in_seconds INTEGER NOT NULL,
    water_pump_refill_relay_state INTEGER NOT NULL,
    limit_switch_state INTEGER NOT NULL,
    water_level_sensor_down_value_main INTEGER NOT NULL,
    water_level_sensor_down_value_backup INTEGER NOT NULL,
    water_level_sensor_up_value INTEGER NOT NULL);

INSERT INTO auto_refill (
    id,
    alarm,
    daily_refill_flow,
    max_daily_refill_flow,
    flow_count_date,
    refill_time_start,
    refill_max_time_in_seconds,
    water_pump_refill_relay_state,
    limit_switch_state,
    water_level_sensor_down_value_main,
    water_level_sensor_down_value_backup,
    water_level_sensor_up_value)
    VALUES (1, 0, 0, 1000, '2022-12-10', 0.0, 10, 0, 0, 0, 0, 0);

CREATE TABLE temperature (
    id INTEGER PRIMARY KEY,
    temperature REAL NOT NULL,
    alarm_level REAL NOT NULL,
    alarm INTEGER NOT NULL);

INSERT  INTO temperature (id, temperature, alarm_level, alarm) VALUES (1, 0.0, 26.0, 0);

CREATE TABLE feeding (
    id INTEGER PRIMARY KEY,
    is_feeding_time INTEGER NOT NULL,
    start_time INTEGER NOT NULL,
    feeding_duration INTEGER NOT NULL,
    water_pump_state INTEGER NOT NULL
);

INSERT INTO feeding (id, is_feeding_time, start_time, feeding_duration, water_pump_state) VALUES (1, 0, 0, 600, 0);

CREATE TABLE fan (
    id INTEGER PRIMARY KEY,
    alarm_level_duty_cycle INTEGER NOT NULL,
    normal_level_duty_cycle INTEGER NOT NULL,
    freeze_level_duty_cycle INTEGER NOT NULL,
    current_level TEXT
);

INSERT INTO fan (id, alarm_level_duty_cycle, normal_level_duty_cycle, freeze_level_duty_cycle, current_level) VALUES (1, 100, 80, 50, 'alarm');

CREATE TABLE auto_refill_history (
    id INTEGER PRIMARY KEY,
    flow_count_date DATE,
    flow INTEGER
);

CREATE TABLE temperature_history (
    id INTEGER PRIMARY KEY,
    date_time DATETIME,
    temperature REAL
);

INSERT INTO info (migration, description) VALUES ('v1', 'init_tables_for_all_sensors');