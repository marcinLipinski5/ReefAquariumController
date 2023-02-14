CREATE TABLE water_quality(
    id INTEGER PRIMARY KEY,
    date DATETIME NOT NULL,
    salinity REAL,
    kh REAL,
    no3 REAL,
    po4 REAL,
    mg REAL,
    ca REAL,
    comment TEXT
);

INSERT INTO water_quality(date, salinity, kh, no3, po4, mg, ca, comment) VALUES ('1', 1.025, 1.1, 1.2, 1.3, 1.4, 1.5, "aaaa");
INSERT INTO water_quality(date, salinity, kh, no3, po4, mg, ca, comment) VALUES ('2', 1.025, 2.1, 2.2, 2.3, 2.4, 2.5, "bbbb");

ALTER TABLE ph RENAME COLUMN calibration_voltage_4_0 to calibration_voltage_9_18;
ALTER TABLE ph RENAME COLUMN calibration_voltage_7_0 to calibration_voltage_6_89;
ALTER TABLE ph ADD COLUMN last_voltage REAL DEFAULT 0.0 NOT NULL;
ALTER TABLE ph RENAME COLUMN alarm_level to alarm_level_up;
ALTER TABLE ph ADD COLUMN alarm_level_down REAL DEFAULT 7.0 NOT NULL;

INSERT INTO info (migration, description) VALUES ('v5', 'init_table_for_water_quality. Update pH logic');
