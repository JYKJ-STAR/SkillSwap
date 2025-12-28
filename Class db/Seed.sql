-- Admin account
INSERT INTO users (role, full_name, email, password_hash, age, grc, verification_status)
VALUES ('admin','Admin User','admin@skillswap.local','demo_hash',30,'Central','verified');

-- Sample youth + senior
INSERT INTO users (role, full_name, email, password_hash, age, grc, verification_status)
VALUES
('youth','Jayden Yip','youth@skillswap.local','demo_hash',17,'Central','verified'),
('senior','Mdm Tan','senior@skillswap.local','demo_hash',68,'Central','verified');

-- Sample events
INSERT INTO events (title, description, event_datetime, location, language, category, status, created_by)
VALUES
('WhatsApp Basics for Seniors','Learn how to message, send photos, and avoid scams','2026-01-10 14:00:00','Toa Payoh CC','English','Digital Skills','open',1),
('Traditional Cooking Share','Seniors teach simple traditional recipes','2026-01-12 10:00:00','Bishan CC','English','Life Skills','open',1);
