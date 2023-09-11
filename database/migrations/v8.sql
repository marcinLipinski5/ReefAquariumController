CREATE TABLE peristaltic_pump_general (
    id INTEGER PRIMARY KEY,
    update_needed INTEGER NOT NULL,
    pumps_amount INTEGER NOT NULL
);

INSERT INTO peristaltic_pump_general (id, update_needed, pumps_amount) VALUES (1, 1, 0);


CREATE TABLE peristaltic_pump (
    id INTEGER PRIMARY KEY,
    pump_number INTEGER NOT NULL,
    scheduler TEXT NOT NULL,
    ml_per_second REAL NOT NULL
);

INSERT INTO peristaltic_pump (pump_number, scheduler, ml_per_second) VALUES (1,
'{"1": {"start": "12:20", "capacity": 35},"2": {"start": "13:30", "capacity": 35},"3": {"start": "14:40", "capacity": 45},"4": {"start": "15:50", "capacity": 55}}',
5
);

INSERT INTO peristaltic_pump (pump_number, scheduler, ml_per_second) VALUES (2,
'{"1": {"start": "16:20", "capacity": 35},"2": {"start": "17:30", "capacity": 35},"3": {"start": "18:40", "capacity": 45},"4": {"start": "19:50", "capacity": 55}}',
10
);

INSERT INTO info (migration, description) VALUES ('v8', 'add peristaltic pump support');