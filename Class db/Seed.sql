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
(1, 'Mdm Tan',  'senior', 'demo_hash', '1958-01-01', '91234569', 'senior@skillswap.local', 'verified', 100);

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
INSERT INTO event (created_by_user_id, grc_id, title, description, category, led_by, start_datetime, location, status, base_points_teacher, base_points_buddy, base_points_participant) VALUES
(1, 1, 'Tech + Life Swap: WhatsApp Basics', 'WhatsApp basics + simple snack demo - Learn messaging, photos, video calls while enjoying treats', 'tech_digital', 'youth', '2026-01-15 14:00:00', 'Toa Payoh CC', 'open', 30, 20, 10),
(1, 2, 'Photo Memories Workshop', 'Phone camera/editing + seniors storytelling - Capture and edit photos while sharing memories', 'tech_digital', 'youth', '2026-01-17 10:00:00', 'Bishan CC', 'open', 30, 20, 10),
(1, 3, 'Online Safety and Scam Awareness', 'Learn to identify scams and stay safe online - Interactive sharing session', 'tech_digital', 'youth', '2026-01-18 15:00:00', 'Ang Mo Kio CC', 'open', 30, 20, 10),
(1, 4, 'Fitness App Basics', 'Learn to use fitness/health apps + step tracking - Get started with health tracking', 'tech_digital', 'youth', '2026-01-20 09:00:00', 'Tampines Hub', 'open', 30, 20, 10),
(1, 5, 'Beginner Photography Walk', 'Team photos around the neighbourhood - Learn composition and lighting', 'tech_digital', 'youth', '2026-01-22 16:00:00', 'Jurong Lake Gardens', 'open', 30, 20, 10),
(1, 6, 'Coding Unplugged', 'Logic games and puzzles - No heavy computers needed, just fun problem solving', 'tech_digital', 'youth', '2026-01-24 14:00:00', 'Yishun CC', 'open', 30, 20, 10);

-- LIFE SKILLS AND HOME SKILLS (Senior-led)
INSERT INTO event (created_by_user_id, grc_id, title, description, category, led_by, start_datetime, location, status, base_points_teacher, base_points_buddy, base_points_participant) VALUES
(1, 1, 'Traditional Cooking Class', 'Learn classic recipes from experienced home cooks - Youth help setup and document', 'life_skills', 'senior', '2026-01-16 10:00:00', 'Toa Payoh CC Kitchen', 'open', 30, 20, 10),
(1, 2, 'Sewing and Simple Repairs', 'Button fixing, basic stitches, and simple repairs - Practical skills for everyday life', 'life_skills', 'senior', '2026-01-19 14:00:00', 'Bishan CC', 'open', 30, 20, 10),
(1, 7, 'Gardening 101', 'Plant care basics + mini hydroponics starter kit - Green your home', 'life_skills', 'senior', '2026-01-21 09:00:00', 'Punggol Community Garden', 'open', 30, 20, 10),
(1, 8, 'Home Organisation Hacks', 'DIY decluttering and organisation tips - Transform your living space', 'life_skills', 'senior', '2026-01-23 15:00:00', 'Bedok CC', 'open', 30, 20, 10);

-- HEALTH AND WELLNESS (Employee-led)
INSERT INTO event (created_by_user_id, grc_id, title, description, category, led_by, start_datetime, location, status, base_points_teacher, base_points_buddy, base_points_participant) VALUES
(1, 1, 'Gentle Stretching and Tai Chi', 'Relaxing stretches + fitness tracking tips - Suitable for all fitness levels', 'health_wellness', 'employee', '2026-01-15 08:00:00', 'Toa Payoh Stadium', 'open', 30, 20, 10),
(1, 5, 'Light Hiking Adventure', 'Beginner-friendly park walk - Explore nature trails together', 'health_wellness', 'employee', '2026-01-18 07:00:00', 'MacRitchie Reservoir', 'open', 30, 20, 10),
(1, 3, 'Basic First Aid Workshop', 'Essential first aid skills + wellness tips - Everyone learns together', 'health_wellness', 'employee', '2026-01-22 14:00:00', 'Ang Mo Kio CC', 'open', 30, 20, 10),
(1, 4, 'Healthy Meal Planning', 'Nutrition basics + simple meal prep - Eat well on any budget', 'health_wellness', 'employee', '2026-01-25 10:00:00', 'Tampines Hub', 'open', 30, 20, 10);

-- CULTURE, HERITAGE AND CREATIVE (Employee-led)
INSERT INTO event (created_by_user_id, grc_id, title, description, category, led_by, start_datetime, location, status, base_points_teacher, base_points_buddy, base_points_participant) VALUES
(1, 1, 'Heritage Trail Walk', 'Visit heritage sites - Seniors share memories, youth capture photos', 'culture_creative', 'employee', '2026-01-17 09:00:00', 'Chinatown Heritage Centre', 'open', 30, 20, 10),
(1, 2, 'Music Jam Session', 'Percussion, ukulele, and singing - No experience needed', 'culture_creative', 'employee', '2026-01-20 15:00:00', 'Bishan CC Music Room', 'open', 30, 20, 10),
(1, 6, 'Craft Workshop: Origami and Clay', 'Create beautiful origami, clay art, and keychains - All materials provided', 'culture_creative', 'employee', '2026-01-23 14:00:00', 'Yishun CC', 'open', 30, 20, 10),
(1, 7, 'Language Exchange', 'English, Chinese, dialect phrases and etiquette - Learn from each other', 'culture_creative', 'employee', '2026-01-26 10:00:00', 'Punggol CC', 'open', 30, 20, 10);

-- SOCIAL AND GAMES - Classic Games (Senior-led)
INSERT INTO event (created_by_user_id, grc_id, title, description, category, led_by, start_datetime, location, status, base_points_teacher, base_points_buddy, base_points_participant) VALUES
(1, 1, 'Five Stones Tournament', 'Learn the classic kampong game - Fun for all ages', 'social_games', 'senior', '2026-01-16 15:00:00', 'Toa Payoh CC', 'open', 20, 15, 10),
(1, 2, 'Chapteh Challenge', 'Kick shuttlecock competition - Test your skills', 'social_games', 'senior', '2026-01-18 16:00:00', 'Bishan Sports Hall', 'open', 20, 15, 10),
(1, 3, 'Zero Point / O-Sum Games', 'Rubber band and string games - Relive childhood memories', 'social_games', 'senior', '2026-01-20 14:00:00', 'Ang Mo Kio CC', 'open', 20, 15, 10),
(1, 4, 'Pick-up Sticks and Marbles', 'Classic Mikado and guli games - Steady hands win', 'social_games', 'senior', '2026-01-22 15:00:00', 'Tampines CC', 'open', 20, 15, 10),
(1, 5, 'Carrom Championship', 'Team carrom tournament - Flick your way to victory', 'social_games', 'senior', '2026-01-24 14:00:00', 'Jurong CC', 'open', 20, 15, 10),
(1, 6, 'Chinese Chess (Xiangqi)', 'Learn or play Chinese chess - All skill levels welcome', 'social_games', 'senior', '2026-01-26 10:00:00', 'Yishun CC', 'open', 20, 15, 10),
(1, 8, 'Old School Card Games', 'Old Maid, Snap, Happy Families - Card game afternoon', 'social_games', 'senior', '2026-01-28 15:00:00', 'Bedok CC', 'open', 20, 15, 10);

-- SOCIAL AND GAMES - Modern Games (Youth-led)
INSERT INTO event (created_by_user_id, grc_id, title, description, category, led_by, start_datetime, location, status, base_points_teacher, base_points_buddy, base_points_participant) VALUES
(1, 1, 'UNO and DOS Game Night', 'Card game showdown - Easy to learn, hard to master', 'social_games', 'youth', '2026-01-17 19:00:00', 'Toa Payoh CC', 'open', 20, 15, 10),
(1, 2, 'Dobble and Spot It Challenge', 'Fast-paced matching games - Test your reflexes', 'social_games', 'youth', '2026-01-19 15:00:00', 'Bishan CC', 'open', 20, 15, 10),
(1, 3, 'Jenga Tower Challenge', 'How high can you go? - Steady hands competition', 'social_games', 'youth', '2026-01-21 16:00:00', 'Ang Mo Kio CC', 'open', 20, 15, 10),
(1, 4, 'Singapore Bingo Night', 'Themed bingo: SG food, old slang, school life - Fun prizes', 'social_games', 'youth', '2026-01-23 19:00:00', 'Tampines Hub', 'open', 20, 15, 10),
(1, 5, 'Word Games Party', 'Charades, Taboo, Boggle - Laugh and learn together', 'social_games', 'youth', '2026-01-25 15:00:00', 'Jurong CC', 'open', 20, 15, 10),
(1, 7, 'LEGO Build Challenge', 'Team-based puzzle and building challenge - Creativity wins', 'social_games', 'youth', '2026-01-27 14:00:00', 'Punggol CC', 'open', 20, 15, 10);

-- HANDS-ON / COMMUNITY PROJECTS (Employee-led)
INSERT INTO event (created_by_user_id, grc_id, title, description, category, led_by, start_datetime, location, status, base_points_teacher, base_points_buddy, base_points_participant) VALUES
(1, 1, 'Woodwork: Build a Planter Box', 'Simple woodwork project - Take home your creation', 'community_projects', 'employee', '2026-01-18 09:00:00', 'Toa Payoh CC Workshop', 'open', 30, 20, 15),
(1, 7, 'Community Garden Day', 'Planting, watering, labelling plots - Get your hands dirty', 'community_projects', 'employee', '2026-01-21 08:00:00', 'Punggol Community Garden', 'open', 30, 20, 15),
(1, 3, 'Volunteering: Care Bundle Packing', 'Pack care bundles for the needy - Give back together', 'community_projects', 'employee', '2026-01-24 10:00:00', 'Ang Mo Kio CC', 'open', 30, 20, 15),
(1, 4, 'Potluck Cook and Share', 'Community potluck event - Bring a dish, share a story', 'community_projects', 'employee', '2026-01-27 12:00:00', 'Tampines Hub', 'open', 30, 20, 15);

-- EVENT ROLE REQUIREMENTS (for first few events as examples)
INSERT INTO event_role_requirement (event_id, role_type, required_count) VALUES
(1, 'teacher', 2),
(1, 'buddy', 3),
(1, 'participant', 15),
(2, 'teacher', 2),
(2, 'buddy', 3),
(2, 'participant', 12),
(3, 'teacher', 1),
(3, 'buddy', 2),
(3, 'participant', 20);

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
