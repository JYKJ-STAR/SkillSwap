-- =====================================================
-- SEED DATA FOR SKILLSWAP
-- =====================================================

-- GRC (Grassroots Constituencies)
INSERT INTO grc (name, region) VALUES
('Toa Payoh', 'Central'),
('Bishan', 'Central'),
('Ang Mo Kio', 'North'),
('Tampines', 'East'),
('Jurong', 'West');

-- USERS (Admin, Youth, Senior)
INSERT INTO user (grc_id, name, role, password_hash, age, phone, email, verification_status, total_points) VALUES
(1, 'Admin User',  'admin','demo_hash', 30, '91234567', 'admin@skillswap.local', 'verified', 0),
(1, 'Jayden Yip', 'youth', 'demo_hash', 17, '91234568', 'youth@skillswap.local', 'verified', 50),
(1, 'Mdm Tan',  'senior', 'demo_hash', 68, '91234569', 'senior@skillswap.local', 'verified', 100);

-- SKILLS
INSERT INTO skill (name, category, description) VALUES
('WhatsApp Basics', 'Digital Skills', 'Learn messaging, photos, and video calls'),
('Traditional Cooking', 'Life Skills', 'Traditional recipes and cooking techniques'),
('Basic Computer', 'Digital Skills', 'Mouse, keyboard, and file management'),
('Gardening', 'Life Skills', 'Plant care and home gardening tips');

-- USER SKILL OFFERED (Seniors offer skills)
INSERT INTO user_skill_offered (user_id, skill_id) VALUES
(3, 2), -- Mdm Tan offers Traditional Cooking
(3, 4); -- Mdm Tan offers Gardening

-- USER SKILL INTEREST (Youth interested in learning)
INSERT INTO user_skill_interest (user_id, skill_id) VALUES
(2, 2), -- Jayden interested in Traditional Cooking
(2, 4); -- Jayden interested in Gardening

-- EVENTS
INSERT INTO event (created_by_user_id, grc_id, title, description, start_datetime, location, status, base_points_teacher, base_points_buddy, base_points_participant) VALUES
(1, 1, 'WhatsApp Basics for Seniors', 'Learn how to message, send photos, and avoid scams', '2026-01-10 14:00:00', 'Toa Payoh CC', 'open', 30, 20, 10),
(1, 2, 'Traditional Cooking Share', 'Seniors teach simple traditional recipes', '2026-01-12 10:00:00', 'Bishan CC', 'open', 30, 20, 10);

-- EVENT ROLE REQUIREMENTS
INSERT INTO event_role_requirement (event_id, role_type, required_count) VALUES
(1, 'teacher', 1),
(1, 'buddy', 2),
(1, 'participant', 10),
(2, 'teacher', 1),
(2, 'buddy', 2),
(2, 'participant', 8);

-- REWARDS
INSERT INTO reward (name, description, points_required, is_active, total_quantity) VALUES
('NTUC $5 Voucher', 'Redeemable at any NTUC FairPrice outlet', 50, 1, 100),
('Grab $10 Voucher', 'Redeemable for Grab rides or food', 100, 1, 50),
('Movie Ticket', 'One free movie ticket at Golden Village', 80, 1, 30);

-- FAQ ARTICLES
INSERT INTO faq_article (question, answer, category, is_active) VALUES
('How do I earn points?', 'You earn points by attending events as a teacher, buddy, or participant.', 'Points', 1),
('How do I redeem rewards?', 'Go to the Rewards page and select a reward you have enough points for.', 'Rewards', 1),
('How do I report a safety concern?', 'Use the Safety Report feature in the app to submit a report.', 'Safety', 1);
