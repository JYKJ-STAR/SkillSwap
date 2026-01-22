-- =====================================================
-- DATABASE RESET SCRIPT
-- =====================================================
-- This script deletes all users and creates only an Admin user
-- 
-- Admin Credentials:
--   Email: Admin
--   Password: Admin1
--   Role: admin
-- =====================================================

-- Delete all existing users
DELETE FROM user;

-- Insert Admin user
-- Email: Admin@gmail.com
-- Password: Admin@1
INSERT INTO user (name, email, password_hash, role, verification_status)
VALUES (
    'Admin',
    'Admin@gmail.com',
    'scrypt:32768:8:1$DepeFVKqKWeZe7de4eea1b84dbc58398ae3440d41e',
    'admin',
    'verified'
);

-- Insert JaydenYip (Youth)
-- Email: Jayden@gmail.com
-- Password: Jayden@1
INSERT INTO user (name, email, password_hash, role, verification_status)
VALUES (
    'JaydenYip',
    'Jayden@gmail.com',
    'scrypt:32768:8:1$28EkWQlfwcE78c2f7b3ea23406b19b860779191048',
    'youth',
    'verified'
);

-- Insert Dickson (Senior)
-- Email: Dickson@gmail.com
-- Password: Dickson@1
INSERT INTO user (name, email, password_hash, role, verification_status)
VALUES (
    'Dickson',
    'Dickson@gmail.com',
    'scrypt:32768:8:1$xwM3TAU24fzY34d323845fbd1e94ae8c8490aad683',
    'senior',
    'verified'
);

-- Verify the reset
SELECT 
    user_id,
    name,
    email,
    role,
    verification_status
FROM user;
