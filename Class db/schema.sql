-- USERS
CREATE TABLE IF NOT EXISTS users (
  user_id INTEGER PRIMARY KEY AUTOINCREMENT,
  role TEXT NOT NULL CHECK(role IN ('youth','senior','admin')),
  full_name VARCHAR(100) NOT NULL,
  email VARCHAR(120) UNIQUE,
  phone VARCHAR(30) UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  age INTEGER,
  grc VARCHAR(80),
  verification_status TEXT DEFAULT 'unverified' CHECK(verification_status IN ('unverified','pending','verified')),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- EVENTS
CREATE TABLE IF NOT EXISTS events (
  event_id INTEGER PRIMARY KEY AUTOINCREMENT,
  title VARCHAR(150) NOT NULL,
  description TEXT,
  event_datetime TEXT NOT NULL,
  location VARCHAR(150) NOT NULL,
  language VARCHAR(50) DEFAULT 'English',
  category VARCHAR(80),
  status TEXT DEFAULT 'open' CHECK(status IN ('open','closed','cancelled')),
  created_by INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (created_by) REFERENCES users(user_id)
    ON UPDATE CASCADE
    ON DELETE SET NULL
);

-- BOOKINGS
CREATE TABLE IF NOT EXISTS bookings (
  booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  role_chosen TEXT NOT NULL CHECK(role_chosen IN ('teacher','buddy','participant')),
  status TEXT DEFAULT 'booked' CHECK(status IN ('booked','cancelled','completed')),
  booked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(event_id, user_id),
  FOREIGN KEY (event_id) REFERENCES events(event_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

-- NOTIFICATIONS
CREATE TABLE IF NOT EXISTS notifications (
  notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  event_id INTEGER,
  message VARCHAR(255) NOT NULL,
  is_read INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  FOREIGN KEY (event_id) REFERENCES events(event_id)
    ON UPDATE CASCADE
    ON DELETE SET NULL
);

-- SUPPORT TICKETS
CREATE TABLE IF NOT EXISTS support_tickets (
  ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  subject VARCHAR(150) NOT NULL,
  message TEXT NOT NULL,
  status TEXT DEFAULT 'open' CHECK(status IN ('open','in_progress','resolved')),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
    ON UPDATE CASCADE
    ON DELETE SET NULL
);
