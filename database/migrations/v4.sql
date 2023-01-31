ALTER TABLE alert ADD COLUMN email_status INTEGER DEFAULT 0 NOT NULL;

INSERT INTO info (migration, description) VALUES ('v4', 'extend_alerts_table_for_email_notification');
