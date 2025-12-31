from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import get_db_connection
from app import oauth

home_bp = Blueprint("home", __name__)

@home_bp.route("/")
def home():
    """Homepage - guest view. Redirect to dashboard if logged in."""
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard'))
    return render_template("guestview.html")

@home_bp.route("/login")
def login_page():
    """Display authentication page with login tab active."""
    return render_template("auth.html", active_tab='login')

@home_bp.route("/signup")
def signup_page():
    """Display authentication page with signup tab active."""
    return render_template("auth.html", active_tab='signup')

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
    """Handle user registration with JSON support."""
    data = request.get_json() if request.is_json else request.form
    
    if request.is_json:
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'youth')
        first_name = data.get('firstName', '')
        last_name = data.get('lastName', '')
        name = f"{first_name} {last_name}".strip() or email.split('@')[0]
        age = data.get('age')
        phone = data.get('phone')
        language = data.get('language', 'English')
        teach_skills = data.get('teachSkills', [])
        learn_skills = data.get('learnSkills', [])
    else:
        # Fallback for standard form submission
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'youth')
        name = email.split('@')[0]
        age = None
        language = 'English'
        teach_skills = []
        learn_skills = []

    if not email or not password:
        response = {'error': 'Email and password are required'}
        return jsonify(response) if request.is_json else flash("Missing credentials", "error") or redirect(url_for('home.signup_page'))

    password_hash = generate_password_hash(password)
    
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        # Insert User
        cur.execute(
            """INSERT INTO user (name, email, password_hash, role, age, phone, language_pref, verification_status)
               VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')""",
            (name, email, password_hash, role, age, phone, language)
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
        
        if request.is_json:
            return jsonify({'message': 'Registration successful', 'redirect': url_for('dashboard.dashboard')})
        else:
            flash("Registration successful!", "success")
            return redirect(url_for('dashboard.dashboard'))

    except Exception as e:
        conn.rollback()
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        else:
            flash(f"Registration failed: {str(e)}", "error")
            return redirect(url_for('home.signup_page'))
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
    return oauth.google.authorize_redirect(redirect_uri)

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
    return render_template('google_signup.html')

@home_bp.route('/google/complete', methods=['POST'])
def complete_google_signup():
    """Create account for new Google user."""
    if 'google_info' not in session:
        return redirect(url_for('home.home'))
        
    google_info = session['google_info']
    role = request.form.get('role')
    
    if role not in ['youth', 'senior']:
        flash("Invalid role selected", "error")
        return redirect(url_for('home.google_signup'))
    
    conn = get_db_connection()
    try:
        # Insert with verified status
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO user (name, email, role, verification_status, password_hash, language_pref)
               VALUES (?, ?, ?, 'verified', 'google_oauth', 'English')""",
            (google_info['name'], google_info['email'], role)
        )
        user_id = cur.lastrowid
        conn.commit()
        
        # Login
        session['user_id'] = user_id
        session['user_name'] = google_info['name']
        session['user_role'] = role
        session.permanent = True
        
        # Cleanup
        session.pop('google_info', None)
        
        flash("Account created successfully via Google!", "success")
        return redirect(url_for('dashboard.dashboard'))
        
    except Exception as e:
        conn.rollback()
        flash(f"Creation failed: {str(e)}", "error")
        return redirect(url_for('home.google_signup'))
    finally:
        conn.close()

