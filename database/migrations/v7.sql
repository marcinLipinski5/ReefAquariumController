ALTER TABLE light ADD COLUMN enable_feeding_light INTEGER DEFAULT 0 NOT NULL;

INSERT INTO info (migration, description) VALUES ('v7', 'add feeding light mode');
