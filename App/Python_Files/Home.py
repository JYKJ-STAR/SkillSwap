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
    """Homepage - guest view. Redirect to dashboard if logged in.
       Display upcoming events for guests."""
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard'))
    
    # Fetch upcoming events for guest view
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

    # Format events for display
    formatted_events = []
    for e in events:
        # Convert DB datetime string (YYYY-MM-DD HH:MM:SS) to display format
        # e.g. "Jan 15, 2025 - 2:00 PM"
        # Note: In a real app, use datetime objects. Here strictly string manipulation for simplicity/speed or use Python's datetime if needed.
        # Let's import datetime to be safe if not available
        from datetime import datetime
        try:
            dt_obj = datetime.strptime(e['start_datetime'], '%Y-%m-%d %H:%M:%S')
            date_str = dt_obj.strftime('%b %d, %Y - %I:%M %p')
        except:
            date_str = e['start_datetime']

        formatted_events.append({
            'title': e['title'],
            'datetime': date_str,
            'location': e['location']
        })

    return render_template("shared/guestview.html", events=formatted_events)

@home_bp.route("/login")
def login_page():
    """Display authentication page with login tab active."""
    return render_template("shared/auth.html", active_tab='login')

@home_bp.route("/signup")
def signup_page():
    """Display authentication page with signup tab active."""
    return render_template("shared/auth.html", active_tab='signup')

# =====================================================
# AUTHENTICATION (Login/Register/Logout for ALL users)
# =====================================================
@home_bp.route('/check_email', methods=['POST'])
def check_email():
    """Check if email already exists."""
    data = request.get_json()
    email = data.get('email')
    
    conn = get_db_connection()
    user = conn.execute("SELECT 1 FROM user WHERE email = ?", (email,)).fetchone()
    conn.close()
    
    return jsonify({'exists': user is not None})

@home_bp.route('/check_phone', methods=['POST'])
def check_phone():
    """Check if phone number already exists."""
    data = request.get_json()
    phone = data.get('phone')
    
    conn = get_db_connection()
    user = conn.execute("SELECT 1 FROM user WHERE phone = ?", (phone,)).fetchone()
    conn.close()
    
    return jsonify({'exists': user is not None})

@home_bp.route('/login', methods=['POST'])
def login_submit():
    """Handle user login."""
    email = request.form.get('email')
    password = request.form.get('password')
    
    conn = get_db_connection()
    user = conn.execute(
        "SELECT user_id, name, role, password_hash, verification_status FROM user WHERE email = ?",
        (email,)
    ).fetchone()
    conn.close()
    
    if user is None:
        flash("Email not registered.", "error")
        return redirect(url_for('home.login_page'))
    
    # For demo: accept 'demo_hash' as valid password
    if user['password_hash'] != 'demo_hash' and not check_password_hash(user['password_hash'], password):
        flash("Incorrect password.", "error")
        return redirect(url_for('home.login_page'))
    
    # Verification check temporarily disabled by user request
    # if user['verification_status'] != 'verified':
    #     flash("Account verification required. Please check your email or wait for approval.", "warning")
    #     return redirect(url_for('home.login_page'))
    
    # Set session
    session['user_id'] = user['user_id']
    session['user_name'] = user['name']
    session['user_role'] = user['role']

    # Remember Me
    if request.form.get('remember'):
        session.permanent = True
    else:
        session.permanent = False
    
    flash(f"Welcome back, {user['name']}!", "success")
    return redirect(url_for('dashboard.dashboard'))

@home_bp.route('/logout')
def logout():
    """Clear session and log out."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home.home'))

@home_bp.route('/register', methods=['POST'])
def register():
    """Handle user registration with support for FormData (file upload) and JSON."""
    
    # Handle both JSON request and Form Data
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
    
    # Validation
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    # Handle File Upload (Verification Photo)
    verification_photo = None
    if not request.is_json and 'verificationPhoto' in request.files:
        photo = request.files['verificationPhoto']
        if photo and photo.filename:
            filename = secure_filename(photo.filename)
            # Use specific verified folder
            upload_folder = os.path.join(current_app.static_folder, 'img', 'users', 'verification')
            os.makedirs(upload_folder, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            final_filename = f"{timestamp}_{filename}"
            photo.save(os.path.join(upload_folder, final_filename))
            verification_photo = final_filename

    password_hash = generate_password_hash(password)
    
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        # Insert User (with verification_photo and profession)
        cur.execute(
            """INSERT INTO user (name, email, password_hash, role, birth_date, phone, language_pref, profession, verification_status, verification_photo)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)""",
            (name, email, password_hash, role, birth_date, phone, language, profession, verification_photo)
        )
        user_id = cur.lastrowid
        
        # Helper to process skills
        def process_skills(skills, table_name):
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
            process_skills(teach_skills, 'user_skill_offered')
        if learn_skills:
            process_skills(learn_skills, 'user_skill_interest')

        conn.commit()
        
        # Auto-login
        session['user_id'] = user_id
        session['user_name'] = name
        session['user_role'] = role
        
        return jsonify({'message': 'Registration successful', 'redirect': url_for('dashboard.dashboard')})

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()




# Temporary route to simulate login for testing purposes
@home_bp.route('/mock_login/<role>')
def mock_login(role):
    session['user_role'] = role
    session['user_name'] = f"Test {role.capitalize()}"

# =====================================================
# GOOGLE OAUTH
# =====================================================
@home_bp.route('/google/login')
def google_login():
    """Initiate Google OAuth flow."""
    redirect_uri = url_for('home.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri, prompt='select_account')

@home_bp.route('/google/callback')
def google_callback():
    """Handle Google OAuth callback."""
    try:
        token = oauth.google.authorize_access_token()
        user_info = oauth.google.userinfo()
        
        email = user_info.get('email')
        name = user_info.get('name')
        
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM user WHERE email = ?", (email,)).fetchone()
        
        if user:
            # User exists - Login
            session['user_id'] = user['user_id']
            session['user_name'] = user['name']
            session['user_role'] = user['role']
            session.permanent = True # Default to perma session for ease? Or follow remember me? Default true for oauth is fine.
            conn.close()
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for('dashboard.dashboard'))
        else:
            # New User - Redirect to completion
            session['google_info'] = user_info
            conn.close()
            return redirect(url_for('home.google_signup'))
            
    except Exception as e:
        flash(f"Google Login failed: {str(e)}", "error")
        return redirect(url_for('home.login_page'))

@home_bp.route('/google/signup')
def google_signup():
    """Show role selection for new Google users."""
    if 'google_info' not in session:
        return redirect(url_for('home.home'))
    
    google_info = session['google_info']
    full_name = google_info.get('name', '')
    # Basic Name Splitting
    parts = full_name.split(' ', 1)
    first_name = parts[0]
    last_name = parts[1] if len(parts) > 1 else ''

    return render_template('shared/google_signup.html', 
                          google_name=full_name,
                          google_first_name=first_name,
                          google_last_name=last_name)

@home_bp.route('/google/complete', methods=['POST'])
def complete_google_signup():
    """Create account for new Google user with full details."""
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
        
        # Insert User with all details (Added profession)
        cur.execute(
            """INSERT INTO user (name, email, role, verification_status, password_hash, language_pref, birth_date, phone, profession)
               VALUES (?, ?, ?, 'verified', 'google_oauth', ?, ?, ?, ?)""",
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
        
        # Cleanup
        session.pop('google_info', None)
        
        flash("Account created successfully via Google!", "success")
        return jsonify({'message': 'Success', 'redirect': url_for('dashboard.dashboard')})
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

