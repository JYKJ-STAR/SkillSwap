-- Enable Foreign Keys (Required for SQLite)
PRAGMA foreign_keys = ON;

-- =====================================================
-- 1. USER & CORE
-- =====================================================
CREATE TABLE IF NOT EXISTS grc (
  grc_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  region TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user (
  user_id INTEGER PRIMARY KEY AUTOINCREMENT,
  grc_id INTEGER,
  name TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  birth_date TEXT,
  phone TEXT UNIQUE,
  email TEXT UNIQUE,
  
  -- Added verification_token based on your ERD
  verification_token TEXT,
  
  -- New photo columns
  profile_photo TEXT,
  verification_photo TEXT,
  
  role TEXT NOT NULL CHECK (role IN ('youth','senior','admin','employee')),
  display_name TEXT GENERATED ALWAYS AS (name || ' (' || role || ')') VIRTUAL,
  verification_status TEXT NOT NULL DEFAULT 'unverified' CHECK (verification_status IN ('unverified','pending','verified')),
  language_pref TEXT DEFAULT 'English',
  profession TEXT,
  bio TEXT,
  total_points INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (grc_id) REFERENCES grc(grc_id) ON DELETE SET NULL
);

-- ADMIN TABLE (Simplified)
CREATE TABLE IF NOT EXISTS admin (
  admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  photo TEXT,
  privileged TEXT NOT NULL DEFAULT 'No' CHECK (privileged IN ('Yes', 'No')),
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- =====================================================
-- 2. SKILLS + MATCHING
-- =====================================================
CREATE TABLE IF NOT EXISTS skill (
  skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  description TEXT
);

CREATE TABLE IF NOT EXISTS user_skill_offered (
  user_id INTEGER NOT NULL,
  skill_id INTEGER NOT NULL,
  PRIMARY KEY (user_id, skill_id),
  FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE,
  FOREIGN KEY (skill_id) REFERENCES skill(skill_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_skill_interest (
  user_id INTEGER NOT NULL,
  skill_id INTEGER NOT NULL,
  PRIMARY KEY (user_id, skill_id),
  FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE,
  FOREIGN KEY (skill_id) REFERENCES skill(skill_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS match (
  youth_id INTEGER NOT NULL,
  senior_id INTEGER NOT NULL,
  skill_id INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','closed','blocked')),
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  PRIMARY KEY (youth_id, senior_id, skill_id),
  FOREIGN KEY (youth_id) REFERENCES user(user_id) ON DELETE CASCADE,
  FOREIGN KEY (senior_id) REFERENCES user(user_id) ON DELETE CASCADE,
  FOREIGN KEY (skill_id) REFERENCES skill(skill_id) ON DELETE CASCADE
);

-- NEW: Help Request (One-off requests)
CREATE TABLE IF NOT EXISTS help_request (
  help_request_id INTEGER PRIMARY KEY AUTOINCREMENT,
  requester_id INTEGER NOT NULL,
  skill_id INTEGER NOT NULL,
  preferred_time TEXT,
  status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open','matched','closed','cancelled','pending','approved','voided','ended')),
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (requester_id) REFERENCES user(user_id) ON DELETE CASCADE,
  FOREIGN KEY (skill_id) REFERENCES skill(skill_id) ON DELETE CASCADE
);

-- =====================================================
-- 3. EVENTS & BOOKINGS
-- =====================================================
CREATE TABLE IF NOT EXISTS event (
  event_id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_by_user_id INTEGER NOT NULL,
  grc_id INTEGER,
  title TEXT NOT NULL,
  description TEXT,
  category TEXT NOT NULL DEFAULT 'social_games' CHECK (category IN ('tech_digital','life_skills','health_wellness','culture_creative','social_games','community_projects')),
  led_by TEXT NOT NULL DEFAULT 'employee' CHECK (led_by IN ('youth','senior','employee')),
  start_datetime TEXT NOT NULL,
  end_datetime TEXT,
  location TEXT,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('open','closed','cancelled','pending','approved','published','voided','ended')),
  void_reason TEXT,
  max_capacity INTEGER,
  base_points_teacher INTEGER DEFAULT 0,

  base_points_participant INTEGER DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  published_at TEXT,
  FOREIGN KEY (created_by_user_id) REFERENCES user(user_id) ON DELETE RESTRICT,
  FOREIGN KEY (grc_id) REFERENCES grc(grc_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS event_role_requirement (
  event_id INTEGER NOT NULL,
  role_type TEXT NOT NULL CHECK (role_type IN ('teacher','buddy','participant')),
  required_count INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (event_id, role_type),
  FOREIGN KEY (event_id) REFERENCES event(event_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS event_booking (
  user_id INTEGER NOT NULL,
  event_id INTEGER NOT NULL,
  role_type TEXT NOT NULL CHECK (role_type IN ('teacher','buddy','participant')),
  status TEXT NOT NULL DEFAULT 'booked' CHECK (status IN ('booked','cancelled','completed','no_show')),
  booked_at TEXT NOT NULL DEFAULT (datetime('now')),
  proof_media_url TEXT,
  proof_description TEXT,  -- User feedback/description for event proof
  hours_earned REAL,
  PRIMARY KEY (user_id, event_id),
  FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE,
  FOREIGN KEY (event_id) REFERENCES event(event_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS verification_log (
  log_id INTEGER PRIMARY KEY AUTOINCREMENT,
  admin_id INTEGER, 
  booking_user_id INTEGER NOT NULL,
  booking_event_id INTEGER NOT NULL,
  previous_status TEXT,
  new_status TEXT NOT NULL,
  comments TEXT,
  verified_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (admin_id) REFERENCES user(user_id) ON DELETE SET NULL,
  FOREIGN KEY (booking_user_id, booking_event_id) REFERENCES event_booking(user_id, event_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS review (
  review_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  event_id INTEGER NOT NULL,
  rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
  comment TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (user_id, event_id) REFERENCES event_booking(user_id, event_id) ON DELETE CASCADE
);

-- =====================================================
-- 4. REWARDS & POINTS
-- =====================================================
CREATE TABLE IF NOT EXISTS reward (
  reward_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  description TEXT,
  points_required INTEGER NOT NULL,
  is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0,1)),
  total_quantity INTEGER
);

CREATE TABLE IF NOT EXISTS reward_redemption (
  redemption_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  reward_id INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'requested' CHECK (status IN ('requested','approved','rejected','redeemed','cancelled')),
  voucher_code TEXT UNIQUE,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE,
  FOREIGN KEY (reward_id) REFERENCES reward(reward_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS points_transaction (
  transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  event_id INTEGER,
  redemption_id INTEGER,
  points_change INTEGER NOT NULL,
  remarks TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE,
  FOREIGN KEY (event_id) REFERENCES event(event_id) ON DELETE SET NULL,
  FOREIGN KEY (redemption_id) REFERENCES reward_redemption(redemption_id) ON DELETE SET NULL
);

-- =====================================================
-- 5. SUPPORT, SAFETY & NOTIFICATIONS
-- =====================================================
-- NEW: FAQ Article
CREATE TABLE IF NOT EXISTS faq_article (
  faq_id INTEGER PRIMARY KEY AUTOINCREMENT,
  question TEXT NOT NULL,
  answer TEXT NOT NULL,
  category TEXT,
  is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0,1))
);

CREATE TABLE IF NOT EXISTS support_ticket (
    ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    subject TEXT NOT NULL,       -- This will store the "Issue Type"
    description TEXT NOT NULL,   -- This stores "Description" + "Event Name"
    status TEXT DEFAULT 'open',  -- 'open', 'resolved', 'voided'
    reply TEXT,                  -- Admin reply to the ticket
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (user_id)
);


-- Live Chat Tables
CREATE TABLE IF NOT EXISTS live_chat_session (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    admin_connected INTEGER DEFAULT 0 CHECK (admin_connected IN (0, 1)),
    connected_admin_id INTEGER,  -- Track which admin is connected
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'closed')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_message_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (user_id) ON DELETE CASCADE,
    FOREIGN KEY (connected_admin_id) REFERENCES admin (admin_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS live_chat_message (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    sender_type TEXT NOT NULL CHECK (sender_type IN ('user', 'admin', 'system')),
    sender_id INTEGER,  -- user_id or admin_id (NULL for system messages)
    message_text TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES live_chat_session (session_id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_chat_session_user ON live_chat_session(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_session_status ON live_chat_session(status);
CREATE INDEX IF NOT EXISTS idx_chat_message_session ON live_chat_message(session_id);


CREATE TABLE IF NOT EXISTS notification (
  notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  event_id INTEGER,
  challenge_id INTEGER,
  message TEXT NOT NULL,
  is_read INTEGER DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (user_id) REFERENCES user(user_id),
  FOREIGN KEY (event_id) REFERENCES event(event_id) ON DELETE CASCADE,
  FOREIGN KEY (challenge_id) REFERENCES challenge(challenge_id) ON DELETE CASCADE
);

-- NEW: Safety Report (Reporting users)
CREATE TABLE IF NOT EXISTS safety_report (
  report_id INTEGER PRIMARY KEY AUTOINCREMENT,
  reported_user_id INTEGER NOT NULL,
  reported_by_user_id INTEGER NOT NULL,
  event_id INTEGER,
  handled_by_admin_id INTEGER,
  description TEXT,
  status TEXT NOT NULL DEFAULT 'submitted' CHECK (status IN ('submitted','reviewing','resolved','dismissed')),
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (reported_user_id) REFERENCES user(user_id) ON DELETE CASCADE,
  FOREIGN KEY (reported_by_user_id) REFERENCES user(user_id) ON DELETE CASCADE,
  FOREIGN KEY (event_id) REFERENCES event(event_id) ON DELETE SET NULL,
  FOREIGN KEY (handled_by_admin_id) REFERENCES user(user_id) ON DELETE SET NULL
);

-- =====================================================
-- 6. CHALLENGES
-- =====================================================
CREATE TABLE IF NOT EXISTS challenge (
  challenge_id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  description TEXT,
  start_date TEXT NOT NULL, -- YYYY-MM-DD
  end_date TEXT NOT NULL,   -- YYYY-MM-DD
  bonus_points INTEGER DEFAULT 0,
  target_count INTEGER DEFAULT 1,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'inactive', 'published', 'voided', 'ended')),
  void_reason TEXT,
  created_by INTEGER,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  published_at TEXT,
  voided_at TEXT,
  ended_at TEXT,
  FOREIGN KEY (created_by) REFERENCES admin(admin_id) ON DELETE SET NULL
);

-- Track user challenge completions with proof submissions
CREATE TABLE IF NOT EXISTS challenge_completion (
  completion_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  challenge_id INTEGER NOT NULL,
  proof_photo TEXT,  -- Stored in img/users/challenges_proof/
  submitted_at TEXT NOT NULL DEFAULT (datetime('now')),
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
  verified_at TEXT,
  verified_by_admin_id INTEGER,
  rejection_reason TEXT,
  FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE,
  FOREIGN KEY (challenge_id) REFERENCES challenge(challenge_id) ON DELETE CASCADE,
  FOREIGN KEY (verified_by_admin_id) REFERENCES admin(admin_id) ON DELETE SET NULL,
  UNIQUE(user_id, challenge_id)  -- One submission per user per challenge
);


