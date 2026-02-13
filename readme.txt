================================================
SKILLSWAP Readme File
================================================

PROJECT OVERVIEW
----------------
SkillSwap is a web application that bridges the generation gap by connecting youth and seniors 
for meaningful skill exchange. Youth can learn traditional skills from seniors while teaching 
them modern technology skills.

================================================
LOGIN CREDENTIALS
================================================

ADMIN LOGIN
-----------
URL: http://localhost:5001/admin/login
Email: admin@email.com
Password: admin@1

How to Create new admin?
-------------------------
Click Create new admin account
Key in details for a privileged admin account
Email: admin@email.com
Password: admin@1
Click sign in

YOUTH LOGIN
-----------
URL: http://localhost:5000/login
Email: Jayden@gmail.com
Password: Jayden@1

SENIOR LOGIN
------------
URL: http://localhost:5000/login
Email: Dickson@gmail.com
Password: Dickson@1

================================================
SETUP INSTRUCTIONS
================================================
1. PREREQUISITES
   - Python 3.x installed
   - Virtual environment (venv)

2. INSTALLATION
   a. Clone/download the project
   b. Create virtual environment:
      python -m venv venv
   
   c. Activate virtual environment:
      Windows: venv\Scripts\activate
      Mac/Linux: source venv/bin/activate
   
   d. Install dependencies:
      pip install -r requirements.txt

3. ENVIRONMENT CONFIGURATION
   - Create a .env file in the root directory
   - Add required environment variables:
     (can refer to the extra file I send)

4. DATABASE SETUP
   - Database file: Class db/skillswap.db
   - Reset database (optional, copy and paste this to reset database):
     venv\Scripts\python.exe "Class db/reset_database.py"
   
   - Reset with seed events:
     venv\Scripts\python.exe "Class db/reset_database.py" --events

================================================
RUNNING THE APPLICATION
================================================
The application runs on two domains:
- Youth/Senior Domain: http://localhost:5000
- Admin Domain: http://localhost:5001

================================================
PROJECT STRUCTURE
================================================
SkillSwap/
├── Main.py                 # Application entry point (multi-process server)
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not in git, need to create for google outh)
│
├── app/
│   ├── __init__.py        # Flask app factory
│   ├── db.py              # Database connection & migrations
│   │
│   ├── Python_Files/      # Backend route handlers
│   │   ├── Admin.py       # Admin panel routes
│   │   ├── Home.py        # Authentication & home
│   │   ├── Dashboard.py   # User dashboards
│   │   ├── Events.py      # Event management
│   │   ├── Schedule.py    # User schedules
│   │   ├── Rewards.py     # Points & rewards system
│   │   ├── Support.py     # Support tickets & live chat
│   │   └── settings.py    # User settings
│   │
│   ├── HTML_Files/        # Jinja2 templates
│   │   ├── admin/         # Admin templates
│   │   ├── youth/         # Youth user templates
│   │   ├── senior/        # Senior user templates
│   │   └── shared/        # all shared templates
│   │
│   └── Styling/           # Static assets
│       ├── css/           # Stylesheets
│       ├── js/            # JavaScript files
│       └── img/           # Image assets
│
└── Class db/
    ├── skillswap.db       # SQLite database
    ├── schema.sql         # Database schema
    └── reset_database.py  # Database reset utility

================================================
CONTRIBUTORS
================================================
Development Team: [Yang,Jayden,Caius,Dickson]

User Management: Yang
Events & Dashboard Management: Jayden
Activities & Rewards Management: Caius
Customer Support Management: Dickson
================================================
COMPLETED FEATURES & CREDITS
================================================
USER MANAGEMENT
--------------------------------
Yang
    User Registration (Youth/Senior)
    - Multi-step signup form with validation
    - Email & phone number verification
    - Skills and interests selection
    - ID verification upload

    Google OAuth Integration
    - Sign in with Google
    - Complete profile after OAuth
    
    User Login/Logout
    - Role-based authentication
    - Session management (Remember me)
    - Password reset functionality
    
    Admin Authentication
    - Separate admin login system
    - Privileged admin roles
    - Admin account creation (privileged only)

    User Management
    - View all users (with filters)
    - Name search functionality
    - User verification approval/rejection
    - Edit user details
    - Delete users

    User Settings
    - Edit profile information
    - Update profile photo
    - Update verification photo
    - Change password
    - Manage skills and interests
    - Language preference
    - View verification status (Verified/Pending/Unverified)

    Verification Function
    - Unverified user cannot sign up for events

    Technical Features
    - Responsive Design
    - Mobile-friendly layouts
    - Tablet optimization
    - Desktop optimized views

----------------------------------------------------------------
Dashboard & Event Management (YOUTH & SENIOR)
--------------------------------
Jayden Yip
    Dashboard View
    - Personalized user dashboard for youth and senior
    - Seamless navigation across all pages
    - Notifications display
    - Active challenges display
    - Quick stats (points, events, reflections)
    - Recommendation
    
    Event View
    - Browse available events & challenges
    - Filter by category and locations
    - Search Bar
    - View event details
    - Booking of events (as mentor or participant)

    Challenges
    - View active challenges
    - View challenge details
    - Receive challenge notifications

    Notification System
    - Event cancellations
    - Challenge updates
    - Admin messages
    - Real-time notifications

    Admin Dashboard
    - User statistics overview
    - Pending verifications
    - System metrics

    Admin Event & Challenges Management
    - Create/edit/delete events
    - Create/edit/delete challenges
    - Event approval workflow (Pending → Approved → Published)
    - Event categorization (6 categories)
    - Dynamic role capacities (teacher/participant)
    - View all event stages(Approved, Ended, Voided)
    - Set base points per role
    - View event participants
    - Cancel events with user notifications
    - Archive old events
    - Challenge approval workflow
    - Publish/unpublish challenges
    - Void/end challenges
    - User notifications for challenge changes

    Database SETUP
    - Setup database
    - Reset database
    - Reset users
    - Reset admins
    - Reset events

----------------------------------------------------------------
Rewards & Activities Management
--------------------------------
Caius Chan
    Schedule
    - View upcoming events
    - View waiting for feedback events
      - Action required (upload proof)
      - Pending review
    - View completed events
    - Upload attendance proof
    - Rate events (star rating + reflection)
    - Withdrawal from events
    - Award points after completing event

    Rewards System
    - Browse available rewards
    - Redeem rewards with points
    - View "My Rewards" (pending approval)
    - Claim approved rewards
    - View reward history (used/expired/dismissed)

    Points System
    - Automatic points calculation
    - Base points per role (teacher/participant)
    - Bonus points for challenges
    - Points transaction logging
    - Admin manual point adjustment

    Admin Rewards Management
    - Create/edit/delete rewards
    - Set points required
    - Approve/reject reward redemptions
    - Track reward claims
    - Filter Redeemed Rewards

    
    Admin Challenegs & Activites Validation
    - Validate attendance proof
    - Award points after completing event
    - Reject attendance proof
    - Reject rewards

    Role-Based Access Control
    - User roles (Youth/Senior)
    - Admin privileges (Privileged/Normal)
    - Route protection decorators

----------------------------------------------------------------
Customer Support Management
--------------------------------
Dickson Lim
    Customer Support Get help Page
    - FAQ
    - Contact Info

    Safety Reporting Center
    - Create support tickets
    - Submit reports
    - Attach event to ticket
    - Upload files with ticket

    My tickets
    - View all ongoing tickets
    - View ticket history

    Live chat
    - Start Live chat with admin
    - View ongoing live chats

    Admin Support Ticket
    - View all support tickets progress
    - Filter by status (Open/In Progress/Resolved)
    - Reply user tickets

    Admin Live Chat
    - View all ongoing Live chat with users


-------------------------------


================================================
LAST UPDATED: February 13, 2026
================================================
