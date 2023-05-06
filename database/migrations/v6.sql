CREATE TABLE light (
    id INTEGER PRIMARY KEY,
    start_time TEXT NOT NULL,
    stop_time TEXT NOT NULL,
    power INTEGER NOT NULL,
    update_needed INTEGER NOT NULL
);

INSERT INTO light (id, start_time, stop_time, power, update_needed) VALUES (1, "08:00", "20:00", 50, 0);

INSERT INTO info (migration, description) VALUES ('v6', 'init_table_for_lights_pwm_control');