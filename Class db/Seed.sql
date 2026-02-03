-- =====================================================
-- SEED DATA FOR SKILLSWAP
-- =====================================================

-- GRC (Grassroots Constituencies)
INSERT INTO grc (name, region) VALUES
('Toa Payoh', 'Central'),
('Bishan', 'Central'),
('Ang Mo Kio', 'North'),
('Tampines', 'East'),
('Jurong', 'West'),
('Yishun', 'North'),
('Punggol', 'North-East'),
('Bedok', 'East');

-- USERS (Youth, Senior only - Admin now in separate table)
INSERT INTO user (grc_id, name, role, password_hash, birth_date, phone, email, verification_status, total_points) VALUES
(1, 'Jayden Yip', 'youth', 'demo_hash', '2009-01-01', '91234568', 'youth@skillswap.local', 'verified', 50),
(1, 'Mdm Tan',  'senior', 'demo_hash', '1958-01-01', '91234569', 'senior@skillswap.local', 'verified', 100),
(2, 'Alice Lim', 'youth', 'demo_hash', '2008-05-15', '91234570', 'alice@skillswap.local', 'verified', 20);

-- ADMIN USERS (Separate table)
INSERT INTO admin (name, email, password_hash, privileged) VALUES
('Super Admin', 'admin@skillswap.local', 'demo_hash', 'Yes');

-- SKILLS (Updated with new categories)
INSERT INTO skill (name, category, description) VALUES
-- Tech and Digital
('WhatsApp Basics', 'Tech and Digital', 'Learn messaging, photos, and video calls'),
('Photo Editing', 'Tech and Digital', 'Phone camera and photo editing skills'),
('Online Safety', 'Tech and Digital', 'Scam awareness and online security'),
('Fitness Apps', 'Tech and Digital', 'Health and fitness tracking apps'),
('Photography', 'Tech and Digital', 'Basic photography techniques'),
('Coding Basics', 'Tech and Digital', 'Introduction to programming logic'),
-- Life Skills
('Traditional Cooking', 'Life Skills', 'Traditional recipes and cooking techniques'),
('Sewing', 'Life Skills', 'Basic sewing and repairs'),
('Gardening', 'Life Skills', 'Plant care and home gardening tips'),
('Home Organisation', 'Life Skills', 'Decluttering and organisation hacks'),
-- Health and Wellness
('Tai Chi', 'Health and Wellness', 'Gentle stretching and tai chi'),
('Hiking', 'Health and Wellness', 'Light hiking and nature walks'),
('First Aid', 'Health and Wellness', 'Basic first aid and wellness'),
('Nutrition', 'Health and Wellness', 'Healthy meal planning basics'),
-- Culture and Creative
('Heritage', 'Culture and Creative', 'Local heritage and history'),
('Music', 'Culture and Creative', 'Singing and musical instruments'),
('Crafts', 'Culture and Creative', 'Origami, clay, and creative crafts'),
('Languages', 'Culture and Creative', 'Language exchange and dialects');

-- USER SKILL OFFERED (Seniors offer skills)
INSERT INTO user_skill_offered (user_id, skill_id) VALUES
(2, 7),
(2, 9);

-- USER SKILL INTEREST (Youth interested in learning)
INSERT INTO user_skill_interest (user_id, skill_id) VALUES
(1, 7),
(1, 9),
(1, 1),
(1, 5);

-- =====================================================
-- EVENTS BY CATEGORY
-- =====================================================

-- TECH AND DIGITAL SKILLS (Youth-led)
INSERT INTO event (created_by_user_id, grc_id, title, description, category, led_by, start_datetime, location, status, base_points_teacher, base_points_participant) VALUES
(1, 1, 'Tech + Life Swap: WhatsApp Basics', 'WhatsApp basics + simple snack demo - Learn messaging, photos, video calls while enjoying treats', 'tech_digital', 'youth', '2026-02-15 14:00:00', 'Toa Payoh CC', 'published', 30, 10),
(1, 2, 'Photo Memories Workshop', 'Phone camera/editing + seniors storytelling - Capture and edit photos while sharing memories', 'tech_digital', 'youth', '2026-02-17 10:00:00', 'Bishan CC', 'published', 30, 10),
(1, 3, 'Online Safety and Scam Awareness', 'Learn to identify scams and stay safe online - Interactive sharing session', 'tech_digital', 'youth', '2026-02-18 15:00:00', 'Ang Mo Kio CC', 'published', 30, 10),
(1, 4, 'Fitness App Basics', 'Learn to use fitness/health apps + step tracking - Get started with health tracking', 'tech_digital', 'youth', '2026-02-20 09:00:00', 'Tampines Hub', 'published', 30, 10),
(1, 5, 'Beginner Photography Walk', 'Team photos around the neighbourhood - Learn composition and lighting', 'tech_digital', 'youth', '2026-02-22 16:00:00', 'Jurong Lake Gardens', 'published', 30, 10),
(1, 6, 'Coding Unplugged', 'Logic games and puzzles - No heavy computers needed, just fun problem solving', 'tech_digital', 'youth', '2026-02-24 14:00:00', 'Yishun CC', 'published', 30, 10);

-- LIFE SKILLS AND HOME SKILLS (Senior-led)
INSERT INTO event (created_by_user_id, grc_id, title, description, category, led_by, start_datetime, location, status, base_points_teacher, base_points_participant) VALUES
(1, 1, 'Traditional Cooking Class', 'Learn classic recipes from experienced home cooks - Youth help setup and document', 'life_skills', 'senior', '2026-02-16 10:00:00', 'Toa Payoh CC Kitchen', 'published', 30, 10),
(1, 2, 'Sewing and Simple Repairs', 'Button fixing, basic stitches, and simple repairs - Practical skills for everyday life', 'life_skills', 'senior', '2026-02-19 14:00:00', 'Bishan CC', 'published', 30, 10),
(1, 7, 'Gardening 101', 'Plant care basics + mini hydroponics starter kit - Green your home', 'life_skills', 'senior', '2026-02-21 09:00:00', 'Punggol Community Garden', 'published', 30, 10),
(1, 8, 'Home Organisation Hacks', 'DIY decluttering and organisation tips - Transform your living space', 'life_skills', 'senior', '2026-02-23 15:00:00', 'Bedok CC', 'published', 30, 10);

-- HEALTH AND WELLNESS (Employee-led)
INSERT INTO event (created_by_user_id, grc_id, title, description, category, led_by, start_datetime, location, status, base_points_teacher, base_points_participant) VALUES
(1, 1, 'Gentle Stretching and Tai Chi', 'Relaxing stretches + fitness tracking tips - Suitable for all fitness levels', 'health_wellness', 'employee', '2026-02-15 08:00:00', 'Toa Payoh Stadium', 'published', 30, 10),
(1, 5, 'Light Hiking Adventure', 'Beginner-friendly park walk - Explore nature trails together', 'health_wellness', 'employee', '2026-02-18 07:00:00', 'MacRitchie Reservoir', 'published', 30, 10),
(1, 3, 'Basic First Aid Workshop', 'Essential first aid skills + wellness tips - Everyone learns together', 'health_wellness', 'employee', '2026-02-22 14:00:00', 'Ang Mo Kio CC', 'published', 30, 10),
(1, 4, 'Healthy Meal Planning', 'Nutrition basics + simple meal prep - Eat well on any budget', 'health_wellness', 'employee', '2026-02-25 10:00:00', 'Tampines Hub', 'published', 30, 10);

-- CULTURE, HERITAGE AND CREATIVE (Employee-led)
INSERT INTO event (created_by_user_id, grc_id, title, description, category, led_by, start_datetime, location, status, base_points_teacher, base_points_participant) VALUES
(1, 1, 'Heritage Trail Walk', 'Visit heritage sites - Seniors share memories, youth capture photos', 'culture_creative', 'employee', '2026-02-17 09:00:00', 'Chinatown Heritage Centre', 'published', 30, 10),
(1, 2, 'Music Jam Session', 'Percussion, ukulele, and singing - No experience needed', 'culture_creative', 'employee', '2026-02-20 15:00:00', 'Bishan CC Music Room', 'published', 30, 10),
(1, 6, 'Craft Workshop: Origami and Clay', 'Create beautiful origami, clay art, and keychains - All materials provided', 'culture_creative', 'employee', '2026-02-23 14:00:00', 'Yishun CC', 'published', 30, 10),
(1, 7, 'Language Exchange', 'English, Chinese, dialect phrases and etiquette - Learn from each other', 'culture_creative', 'employee', '2026-02-26 10:00:00', 'Punggol CC', 'published', 30, 10);

-- SOCIAL AND GAMES - Classic Games (Senior-led)
INSERT INTO event (created_by_user_id, grc_id, title, description, category, led_by, start_datetime, location, status, base_points_teacher, base_points_participant) VALUES
(1, 1, 'Five Stones Tournament', 'Learn the classic kampong game - Fun for all ages', 'social_games', 'senior', '2026-02-16 15:00:00', 'Toa Payoh CC', 'published', 20, 10),
(1, 2, 'Chapteh Challenge', 'Kick shuttlecock competition - Test your skills', 'social_games', 'senior', '2026-02-18 16:00:00', 'Bishan Sports Hall', 'published', 20, 10),
(1, 3, 'Zero Point / O-Sum Games', 'Rubber band and string games - Relive childhood memories', 'social_games', 'senior', '2026-02-20 14:00:00', 'Ang Mo Kio CC', 'published', 20, 10);

-- SOCIAL AND GAMES - Modern Games (Youth-led)
INSERT INTO event (created_by_user_id, grc_id, title, description, category, led_by, start_datetime, location, status, base_points_teacher, base_points_participant) VALUES
(1, 1, 'UNO and DOS Game Night', 'Card game showdown - Easy to learn, hard to master', 'social_games', 'youth', '2026-02-17 19:00:00', 'Toa Payoh CC', 'published', 20, 10),
(1, 2, 'Dobble and Spot It Challenge', 'Fast-paced matching games - Test your reflexes', 'social_games', 'youth', '2026-02-19 15:00:00', 'Bishan CC', 'published', 20, 10),
(1, 3, 'Jenga Tower Challenge', 'How high can you go? - Steady hands competition', 'social_games', 'youth', '2026-02-21 16:00:00', 'Ang Mo Kio CC', 'published', 20, 10);

-- HANDS-ON / COMMUNITY PROJECTS (Employee-led)
-- (Removed unpublished events)



-- EVENT ROLE REQUIREMENTS (Mentor=5, Participant=15 per event)
INSERT INTO event_role_requirement (event_id, role_type, required_count) VALUES
-- Event 1
(1, 'teacher', 5), (1, 'participant', 15),
-- Event 2
(2, 'teacher', 5), (2, 'participant', 15),
-- Event 3
(3, 'teacher', 5), (3, 'participant', 15),
-- Event 4
(4, 'teacher', 5), (4, 'participant', 15),
-- Event 5
(5, 'teacher', 5), (5, 'participant', 15),
-- Event 6
(6, 'teacher', 5), (6, 'participant', 15),
-- Event 7
(7, 'teacher', 5), (7, 'participant', 15),
-- Event 8
(8, 'teacher', 5), (8, 'participant', 15),
-- Event 9
(9, 'teacher', 5), (9, 'participant', 15),
-- Event 10
(10, 'teacher', 5), (10, 'participant', 15),
-- Event 11
(11, 'teacher', 5), (11, 'participant', 15),
-- Event 12
(12, 'teacher', 5), (12, 'participant', 15),
-- Event 13
(13, 'teacher', 5), (13, 'participant', 15),
-- Event 14
(14, 'teacher', 5), (14, 'participant', 15),
-- Event 15
(15, 'teacher', 5), (15, 'participant', 15),
-- Event 16
(16, 'teacher', 5), (16, 'participant', 15),
-- Event 17
(17, 'teacher', 5), (17, 'participant', 15),
-- Event 18
(18, 'teacher', 5), (18, 'participant', 15),
-- Event 19
(19, 'teacher', 5), (19, 'participant', 15),
-- Event 20
(20, 'teacher', 5), (20, 'participant', 15),
-- Event 21
(21, 'teacher', 5), (21, 'participant', 15);

-- EVENT BOOKINGS (Sample data for counts)
-- No initial bookings requested

-- REWARDS
INSERT INTO reward (name, description, points_required, is_active, total_quantity) VALUES
('NTUC $5 Voucher', 'Redeemable at any NTUC FairPrice outlet', 50, 1, 100),
('Grab $10 Voucher', 'Redeemable for Grab rides or food', 100, 1, 50),
('Movie Ticket', 'One free movie ticket at Golden Village', 80, 1, 30),
('Starbucks $5 Voucher', 'Enjoy a coffee on us', 40, 1, 80),
('Popular $10 Voucher', 'Books and stationery at Popular', 70, 1, 40);

-- FAQ ARTICLES
INSERT INTO faq_article (question, answer, category, is_active) VALUES
('How do I earn points?', 'You earn points by attending events as a teacher, buddy, or participant. Teachers earn the most points!', 'Points', 1),
('How do I redeem rewards?', 'Go to the Rewards page and select a reward you have enough points for. Your voucher code will be generated instantly.', 'Rewards', 1),
('How do I report a safety concern?', 'Use the Safety Report feature in the Support page to submit a report. Our team will review it within 24 hours.', 'Safety', 1),
('What are the different event categories?', 'We have 6 categories: Tech and Digital, Life Skills, Health and Wellness, Culture and Creative, Social Games, and Community Projects.', 'Events', 1),
('Can I suggest a new event?', 'Yes! Contact us through the Support page with your event idea and we will consider adding it to our calendar.', 'Events', 1);


-- CHALLENGES SEED DATA (Current Month)
INSERT INTO challenge (title, description, start_date, end_date, bonus_points, target_count, status, created_by, published_at) VALUES
('Monthly Step Challenge', 'Walk 10,000 steps daily for 30 days - Track your progress and compete with friends', '2026-02-01', '2026-02-28', 50, 10, 'published', 1, '2025-01-01 12:00:00'),
('Digital Detox Weekend', 'Reduce screen time to 2 hours/day for one weekend - Share your offline activities', '2026-02-08', '2026-02-09', 30, 2, 'published', 1, '2025-01-01 12:00:00'),
('Community Garden Project', 'Plant and maintain a community garden plot - Harvest fresh vegetables together', '2026-02-15', '2026-04-15', 75, 8, 'published', 1, '2025-01-01 12:00:00'),
('Learn a New Skill', 'Master a new skill and teach it to others - Document your learning journey', '2026-02-01', '2026-03-01', 60, 3, 'published', 1, '2025-01-01 12:00:00'),
('Zero Waste Challenge', 'Reduce household waste by 50% - Share your eco-friendly tips and tricks', '2026-02-10', '2026-03-10', 40, 5, 'published', 1, '2025-01-01 12:00:00');



