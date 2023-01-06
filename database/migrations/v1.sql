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
    water_level_sensor_down_value_main_state INTEGER NOT NULL,
    water_level_sensor_down_value_backup_state INTEGER NOT NULL,
    water_level_sensor_up_value_state INTEGER NOT NULL,
    calibration INTEGER NOT NULL,
    pulses_per_ml REAL NOT NULL,
    calibration_flow REAL NOT NULL,
    calibration_pulses INTEGER NOT NULL,
    calibration_stage VARCHAR NOT NULL,
    first_run INTEGER NOT NULL);

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
    water_level_sensor_down_value_main_state,
    water_level_sensor_down_value_backup_state,
    water_level_sensor_up_value_state,
    calibration,
    pulses_per_ml,
    calibration_flow,
    calibration_pulses,
    calibration_stage,
    first_run)
    VALUES (1, 0, 0, 1000, '2022-12-10', 0.0, 10, 0, 0, 0, 0, 0, 0, 4.4682539, 100, 500, 'done', 1);

CREATE TABLE temperature (
    id INTEGER PRIMARY KEY,
    temperature REAL NOT NULL,
    alarm_level REAL NOT NULL,
    alarm INTEGER NOT NULL,
    heater_state INTEGER NOT NULL,
    update_needed INTEGER NOT NULL);

INSERT  INTO temperature (id, temperature, alarm_level, alarm, heater_state, update_needed) VALUES (1, 0.0, 26.0, 0, 1, 0);

CREATE TABLE feeding (
    id INTEGER PRIMARY KEY,
    is_feeding_time INTEGER NOT NULL,
    start_time INTEGER NOT NULL,
    feeding_duration INTEGER NOT NULL,
    water_pump_state INTEGER NOT NULL
);

INSERT INTO feeding (id, is_feeding_time, start_time, feeding_duration, water_pump_state) VALUES (1, 0, 0, 600, 1);

CREATE TABLE fan (
    id INTEGER PRIMARY KEY,
    alarm_level_duty_cycle INTEGER NOT NULL,
    normal_level_duty_cycle INTEGER NOT NULL,
    freeze_level_duty_cycle INTEGER NOT NULL,
    current_level TEXT,
    update_needed INTEGER NOT NULL
);

INSERT INTO fan (id, alarm_level_duty_cycle, normal_level_duty_cycle, freeze_level_duty_cycle, current_level, update_needed) VALUES (1, 100, 80, 50, 'alarm', 0);

CREATE TABLE auto_refill_history (
    id INTEGER PRIMARY KEY,
    date DATE,
    flow INTEGER
);

CREATE TABLE temperature_history (
    id INTEGER PRIMARY KEY,
    date_time DATETIME,
    temperature REAL
);

CREATE TABLE ph (
    id INTEGER PRIMARY KEY,
    m REAL NOT NULL,
    b REAL NOT NULL,
    ph REAL NOT NULL,
    process VARCHAR NOT NULL,
    alarm INTEGER NOT NULL,
    alarm_level REAL NOT NULL,
    calibration_time_start REAL NOT NULL,
    calibration_ph VARCHAR NOT NULL,
    calibration_voltage_4_0 REAL NOT NULL,
    calibration_voltage_7_0 REAL NOT NULL
);

INSERT INTO ph (id,
                m,
                b,
                ph,
                process,
                alarm,
                alarm_level,
                calibration_time_start,
                calibration_ph,
                calibration_voltage_4_0,
                calibration_voltage_7_0)
                VALUES (1, 1.0, 2.0, 7.0, 'work', 0, 8.0, 0.0, '7_0', 1.0, 1.0);

CREATE TABLE ph_history (
    id INTEGER PRIMARY KEY,
    date_time DATETIME,
    ph REAL NOT NULL
);

INSERT INTO info (migration, description) VALUES ('v1', 'init_tables_for_all_sensors');


