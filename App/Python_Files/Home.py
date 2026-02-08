from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.db import get_db_connection
from app import oauth
import json
import os
from datetime import datetime

home_bp = Blueprint("home", __name__)

@home_bp.route("/")
def home():
    """
    Homepage Route - Guest View.
    
    Checks if a user is already logged in:
    - If logged in: Redirects to their dashboard.
    - If guest: Fetches and displays upcoming events to encourage sign-ups.
    
    Returns:
        Rendered HTML template for 'guestview.html' with event data.
    """
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard'))
    
    # Fetch upcoming events for guest view from the database
    conn = get_db_connection()
    events = conn.execute('''
        SELECT title, start_datetime, location 
        FROM event 
        WHERE status = 'open' 
        AND start_datetime >= date('now')
        ORDER BY start_datetime ASC 
        LIMIT 8
    ''').fetchall()
    conn.close()

    # Format events for display (converting SQL datetime to readable format)
    formatted_events = []
    for e in events:
        # Convert DB datetime string (YYYY-MM-DD HH:MM:SS) to display format
        # e.g. "Jan 15, 2025 - 2:00 PM"
        from datetime import datetime
        try:
            dt_obj = datetime.strptime(e['start_datetime'], '%Y-%m-%d %H:%M:%S')
            date_str = dt_obj.strftime('%b %d, %Y - %I:%M %p')
        except:
            # Fallback if parsing fails
            date_str = e['start_datetime']

        formatted_events.append({
            'title': e['title'],
            'datetime': date_str,
            'location': e['location']
        })

    return render_template("shared/guestview.html", events=formatted_events)

@home_bp.route("/login")
def login_page():
    """
    Display the Authentication Page (Login Tab Active).
    
    Returns:
        Rendered HTML for 'auth.html' with 'active_tab' set to 'login'.
    """
    return render_template("shared/auth.html", active_tab='login')

@home_bp.route("/signup")
def signup_page():
    """
    Display the Authentication Page (Signup Tab Active).
    
    Returns:
        Rendered HTML for 'auth.html' with 'active_tab' set to 'signup'.
    """
    return render_template("shared/auth.html", active_tab='signup')

# =====================================================
# AUTHENTICATION (Login/Register/Logout for ALL users)
# =====================================================
@home_bp.route('/check_email', methods=['POST'])
def check_email():
    """
    API Endpoint: Check if an email is already registered.
    Used by frontend for real-time validation during signup.
    
    Request Body:
        JSON object containing 'email'.
        
    Returns:
        JSON: {'exists': boolean}
    """
    data = request.get_json()
    email = data.get('email')
    
    conn = get_db_connection()
    user = conn.execute("SELECT 1 FROM user WHERE email = ?", (email,)).fetchone()
    conn.close()
    
    return jsonify({'exists': user is not None})

@home_bp.route('/check_phone', methods=['POST'])
def check_phone():
    """
    API Endpoint: Check if a phone number is already registered.
    Used by frontend for real-time validation during signup.
    
    Request Body:
        JSON object containing 'phone'.
        
    Returns:
        JSON: {'exists': boolean}
    """
    data = request.get_json()
    phone = data.get('phone')
    
    conn = get_db_connection()
    user = conn.execute("SELECT 1 FROM user WHERE phone = ?", (phone,)).fetchone()
    conn.close()
    
    return jsonify({'exists': user is not None})

@home_bp.route('/login', methods=['POST'])
def login_submit():
    """
    Handle User Login Form Submission.
    
    Validates credentials against the database.
    - If valid: Sets up the user session (id, name, role).
    - If invalid: Flashes error message and redirects back to login.
    
    Returns:
        Redirects to Dashboard on success or Login page on failure.
    """
    email = request.form.get('email')
    password = request.form.get('password')
    
    conn = get_db_connection()
    # Fetch user details securely
    user = conn.execute(
        "SELECT user_id, name, role, password_hash, verification_status FROM user WHERE email = ?",
        (email,)
    ).fetchone()
    conn.close()
    
    if user is None:
        flash("Email not registered.", "error")
        return redirect(url_for('home.login_page'))
    
    # Check password (supports hash verification or a hardcoded demo hash)
    if user['password_hash'] != 'demo_hash' and not check_password_hash(user['password_hash'], password):
        flash("Incorrect password.", "error")
        return redirect(url_for('home.login_page'))
    
    # Note: Verification check is currently disabled as per requirements.
    # if user['verification_status'] != 'verified':
    #     flash("Account verification required. Please check your email or wait for approval.", "warning")
    #     return redirect(url_for('home.login_page'))
    
    # Clear any existing session data (including admin sessions) before setting user session
    session.clear()
    
    # Set User Session
    session['user_id'] = user['user_id']
    session['user_name'] = user['name']
    session['user_role'] = user['role']

    # Handle 'Remember Me' functionality
    if request.form.get('remember'):
        session.permanent = True
    else:
        session.permanent = False
    
    flash(f"Welcome back, {user['name']}!", "success")
    return redirect(url_for('dashboard.dashboard'))

@home_bp.route('/verify_reset_email', methods=['POST'])
def verify_reset_email():
    """
    API Endpoint: Verify if an email exists for Password Reset.
    
    Request Body:
        JSON: {'email': string}
        
    Returns:
        JSON: {'exists': boolean}
    """
    data = request.get_json()
    email = data.get('email')
    
    conn = get_db_connection()
    user = conn.execute("SELECT 1 FROM user WHERE email = ?", (email,)).fetchone()
    conn.close()
    
    if user:
        return jsonify({'exists': True})
    else:
        return jsonify({'exists': False, 'error': 'Email not found.'}), 404

@home_bp.route('/reset_password_submit', methods=['POST'])
def reset_password_submit():
    """
    API Endpoint: Process Password Reset.
    
    Updates the password for the given email to the new provided password.
    
    Request Body:
        JSON: {'email': string, 'password': string}
        
    Returns:
        JSON: Success or Error message.
    """
    data = request.get_json()
    email = data.get('email')
    new_password = data.get('password')
    
    if not email or not new_password:
        return jsonify({'error': 'Email and new password are required.'}), 400
        
    # Security Note: In a production app, we would verify a secure token here.
    # For this system, we rely on the flow logic as there is no email service for tokens.
    
    password_hash = generate_password_hash(new_password)
    
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE user SET password_hash = ? WHERE email = ?", (password_hash, email))
        if cur.rowcount == 0:
             conn.close()
             return jsonify({'error': 'User not found.'}), 404
        conn.commit()
        conn.close()
        return jsonify({'message': 'Password reset successful'})
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@home_bp.route('/logout')
def logout():
    """
    Handle User Logout.
    
    Clears the session data relative to the user and redirects to the homepage.
    """
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home.home'))

@home_bp.route('/register', methods=['POST'])
def register():
    """
    Handle New User Registration.
    
    Supports:
    - JSON requests (standard API).
    - FormData requests (includes file upload for verification).
    
    Processes:
    1. Parsing input data (skills, personal info).
    2. Validating required fields.
    3. Handling Verification Photo Upload (if provided).
    4. Creating the User record in the database.
    5. Linking selected Skills (Teach/Learn).
    6. Automatically logging the user in upon success.
    
    Returns:
        JSON response with redirect URL on success or error message.
    """
    
    # Handle both JSON request and Form Data structure
    if request.is_json:
        data = request.get_json()
        teach_skills = data.get('teachSkills', [])
        learn_skills = data.get('learnSkills', [])
    else:
        data = request.form
        # Parse skills if they come as JSON strings from FormData
        try:
            teach_skills = json.loads(data.get('teachSkills', '[]'))
        except:
            teach_skills = []
            
        try:
            learn_skills = json.loads(data.get('learnSkills', '[]'))
        except:
            learn_skills = []

    # Extract User Details
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'youth')
    first_name = data.get('firstName', '')
    last_name = data.get('lastName', '')
    name = f"{first_name} {last_name}".strip() or email.split('@')[0]
    birth_date = data.get('birthDate')
    phone = data.get('phone')
    language = data.get('language', 'English')
    profession = data.get('schoolProfession')
    
    # Basic Validation
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    # Handle File Upload (Verification Photo) for identity verification
    verification_photo = None
    if not request.is_json and 'verificationPhoto' in request.files:
        photo = request.files['verificationPhoto']
        if photo and photo.filename:
            filename = secure_filename(photo.filename)
            # Define specific verified folder path
            upload_folder = os.path.join(current_app.static_folder, 'img', 'users', 'verification')
            os.makedirs(upload_folder, exist_ok=True)
            
            # Timestamp filename to prevent overwrites
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            final_filename = f"{timestamp}_{filename}"
            photo.save(os.path.join(upload_folder, final_filename))
            verification_photo = final_filename

    # Hash Password for security
    password_hash = generate_password_hash(password)
    
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        # Determine initial verification status
        initial_status = 'pending' if verification_photo else 'unverified'

        # Insert User Record
        cur.execute(
            """INSERT INTO user (name, email, password_hash, role, birth_date, phone, language_pref, profession, verification_status, verification_photo)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, email, password_hash, role, birth_date, phone, language, profession, initial_status, verification_photo)
        )
        user_id = cur.lastrowid
        
        # Helper function to process and link skills
        def process_skills(skills, table_name):
            for skill_name in skills:
                if not skill_name: continue
                # Find existing Skill ID or create new Skill
                skill_row = cur.execute("SELECT skill_id FROM skill WHERE name = ?", (skill_name,)).fetchone()
                if skill_row:
                    skill_id = skill_row['skill_id']
                else:
                    cur.execute("INSERT INTO skill (name, category) VALUES (?, 'General')", (skill_name,))
                    skill_id = cur.lastrowid
                
                # Link User to Skill in the respective table (offered vs interested)
                cur.execute(f"INSERT OR IGNORE INTO {table_name} (user_id, skill_id) VALUES (?, ?)", (user_id, skill_id))

        # Process Skills
        if teach_skills:
            process_skills(teach_skills, 'user_skill_offered')
        if learn_skills:
            process_skills(learn_skills, 'user_skill_interest')

        conn.commit()
        
        # Auto-login the new user
        session['user_id'] = user_id
        session['user_name'] = name
        session['user_role'] = role
        session.permanent = True  # Prevent logout on navigation
        
        return jsonify({'message': 'Registration successful', 'redirect': url_for('dashboard.dashboard')})

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()




# Temporary route to simulate login for testing purposes


# =====================================================
# GOOGLE OAUTH
# =====================================================
@home_bp.route('/google/login')
def google_login():
    """
    Initiate Google OAuth Login Flow.
    Redirects user to Google's consent screen.
    """
    redirect_uri = url_for('home.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri, prompt='select_account')

@home_bp.route('/google/callback')
def google_callback():
    """
    Handle Google OAuth Callback.
    
    1. Retrieves access token from Google.
    2. Fetches user info (Email, Name).
    3. Checks if user exists in DB:
       - YES: Logs them in directly.
       - NO: Redirects to 'Google Signup' page to complete profile (Role, Skills, etc).
    """
    try:
        token = oauth.google.authorize_access_token()
        user_info = oauth.google.userinfo()
        
        email = user_info.get('email')
        
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM user WHERE email = ?", (email,)).fetchone()
        
        if user:
            # User exists - Direct Login
            session['user_id'] = user['user_id']
            session['user_name'] = user['name']
            session['user_role'] = user['role']
            session.permanent = True # Default to perma session for OAuth
            conn.close()
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for('dashboard.dashboard'))
        else:
            # User is New - Redirect to completion page
            # Store google info in session to use in the next step
            session['google_info'] = user_info
            conn.close()
            return redirect(url_for('home.google_signup'))
            
    except Exception as e:
        flash(f"Google Login failed: {str(e)}", "error")
        return redirect(url_for('home.login_page'))

@home_bp.route('/google/signup')
def google_signup():
    """
    Display Google Signup Completion Page.
    
    Shown to users logging in with Google for the first time.
    Prefills name from Google info and asks for additonal details (Role, Skills).
    """
    if 'google_info' not in session:
        return redirect(url_for('home.home'))
    
    google_info = session['google_info']
    full_name = google_info.get('name', '')
    # Basic Name Splitting for form pre-fill
    parts = full_name.split(' ', 1)
    first_name = parts[0]
    last_name = parts[1] if len(parts) > 1 else ''

    return render_template('shared/google_signup.html', 
                          google_name=full_name,
                          google_first_name=first_name,
                          google_last_name=last_name)

@home_bp.route('/google/complete', methods=['POST'])
def complete_google_signup():
    """
    Complete Registration for Google User.
    
    Creates the user account in the database using Google email and provided details.
    """
    if 'google_info' not in session:
        return jsonify({'error': 'Session expired. Please login again.'}), 401
        
    google_info = session['google_info']
    data = request.get_json()
    
    role = data.get('role')
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    birth_date = data.get('birthDate')
    phone = data.get('phone')
    language = data.get('language')
    profession = data.get('schoolProfession')
    teach_skills = data.get('teachSkills', [])
    learn_skills = data.get('learnSkills', [])
    
    # Construct full name from form if provided, otherwise fallback to Google name
    name = f"{first_name} {last_name}".strip()
    if not name:
        name = google_info['name']

    if role not in ['youth', 'senior']:
         return jsonify({'error': 'Invalid role selected'}), 400
    
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        
        # Insert User with all details
        # Note: hash is set to 'google_oauth' as they don't have a password
        cur.execute(
            """INSERT INTO user (name, email, role, verification_status, password_hash, language_pref, birth_date, phone, profession)
               VALUES (?, ?, ?, 'unverified', 'google_oauth', ?, ?, ?, ?)""",
            (name, google_info['email'], role, language, birth_date, phone, profession)
        )
        user_id = cur.lastrowid
        
        # Helper to process skills (duplicated locally to ensure self-contained logic)
        def process_skills_local(skills, table_name):
            for skill_name in skills:
                if not skill_name: continue
                # Find or Insert Skill
                skill_row = cur.execute("SELECT skill_id FROM skill WHERE name = ?", (skill_name,)).fetchone()
                if skill_row:
                    skill_id = skill_row['skill_id']
                else:
                    cur.execute("INSERT INTO skill (name, category) VALUES (?, 'General')", (skill_name,))
                    skill_id = cur.lastrowid
                
                # Link User to Skill
                cur.execute(f"INSERT OR IGNORE INTO {table_name} (user_id, skill_id) VALUES (?, ?)", (user_id, skill_id))

        if teach_skills:
            process_skills_local(teach_skills, 'user_skill_offered')
        if learn_skills:
            process_skills_local(learn_skills, 'user_skill_interest')

        conn.commit()
        
        # Login
        session['user_id'] = user_id
        session['user_name'] = name
        session['user_role'] = role
        session.permanent = True
        
        # Cleanup session
        session.pop('google_info', None)
        
        flash("Account created successfully via Google!", "success")
        return jsonify({'message': 'Success', 'redirect': url_for('dashboard.dashboard')})
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

