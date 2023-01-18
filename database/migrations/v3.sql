CREATE TABLE alert(
    id INTEGER PRIMARY KEY,
    type TEXT UNIQUE,
    date_time DATETIME NOT NULL,
    description TEXT NOT NULL,
    status INTEGER NOT NULL,
    action_endpoint TEXT NOT NULL,
    button_text TEXT NOT NULL
);

INSERT INTO alert (type, date_time, description, status, action_endpoint, button_text) VALUES ('flow_sensor_error', '17-01-23 15:00', 'None flow was captured when auto refill pump was active. Check auto refill connections.', 0, '/alert/clear', 'close');
INSERT INTO alert (type, date_time, description, status, action_endpoint, button_text) VALUES ('auto_refill_tank_empty_alert', '17-01-23 16:00', 'Less than 20% water left in auto refill container.', 0, '/auto_refill/reset_refill_tank_state', 'reset');
INSERT INTO alert (type, date_time, description, status, action_endpoint, button_text) VALUES ('auto_refill_watchdog_alert', '17-01-23 17:00', 'Watchdog for auto refill was activated. It is recommended to check all connections and reset application.', 0, '/alert/clear', 'close');

ALTER TABLE auto_refill ADD COLUMN refill_tank_capacity INTEGER DEFAULT 3000 NOT NULL;
ALTER TABLE auto_refill ADD COLUMN refill_tank_water_left INTEGER DEFAULT 3000 NOT NULL;

INSERT INTO info (migration, description) VALUES ('v3', 'init_table_for_alerts');
