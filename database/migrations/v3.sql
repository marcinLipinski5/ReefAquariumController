create TABLE alert(
    id INTEGER PRIMARY KEY,
    type TEXT UNIQUE,
    date_time DATETIME NOT NULL,
    description TEXT NOT NULL,
    status INTEGER NOT NULL,
    action_endpoint TEXT NOT NULL,
    button_text TEXT NOT NULL
);

INSERT INTO alert (type, date_time, description, status, action_endpoint, button_text) VALUES ('a', '17-01-23 15:00', 'None flow was calculated when auto refill pump was active.', 1, '/test1', 'reset');
INSERT INTO alert (type, date_time, description, status, action_endpoint, button_text) VALUES ('b', '17-01-23 16:00', 'Less than 20% water left in auto refill container.', 1, '/test2', 'dismiss');
INSERT INTO alert (type, date_time, description, status, action_endpoint, button_text) VALUES ('c', '17-01-23 17:00', 'Watchdog for auto refill was activated.', 1, '/test3', 'dupa');

INSERT INTO info (migration, description) VALUES ('v3', 'init_table_for_alerts');
