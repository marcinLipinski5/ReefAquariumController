
INSERT INTO info (migration, description) VALUES ('v2', 'init_table_for_notes');

create TABLE notes(
    id INTEGER PRIMARY KEY,
    date_time DATETIME,
    note TEXT
);



