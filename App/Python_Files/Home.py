from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from App.db import get_db_connection

home_bp = Blueprint("home", __name__)

@home_bp.route("/")
def home():
    """Homepage - also serves as login/register page."""
    conn = get_db_connection()
    grcs = conn.execute("SELECT grc_id, name FROM grc").fetchall()
    conn.close()
    return render_template('Homepage.html', grcs=grcs)

# =====================================================
# AUTHENTICATION (Login/Register/Logout for ALL users)
# =====================================================
@home_bp.route('/login', methods=['POST'])
def login():
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
        flash("Invalid email or password.", "error")
        return redirect(url_for('home.home'))
    
    # For demo: accept 'demo_hash' as valid password
    if user['password_hash'] != 'demo_hash' and not check_password_hash(user['password_hash'], password):
        flash("Invalid email or password.", "error")
        return redirect(url_for('home.home'))
    
    if user['verification_status'] != 'verified':
        flash("Your account is pending verification.", "warning")
        return redirect(url_for('home.home'))
    
    # Set session
    session['user_id'] = user['user_id']
    session['user_name'] = user['name']
    session['user_role'] = user['role']
    
    flash(f"Welcome back, {user['name']}!", "success")
    return redirect(url_for('dashboard.dashboard'))

@home_bp.route('/register', methods=['POST'])
def register():
    """Handle user registration."""
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role', 'youth')
    age = request.form.get('age')
    phone = request.form.get('phone')
    grc_id = request.form.get('grc_id') or None
    
    password_hash = generate_password_hash(password)
    
    conn = get_db_connection()
    try:
        conn.execute(
            """INSERT INTO user (grc_id, name, password_hash, age, phone, email, role, verification_status)
               VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')""",
            (grc_id, name, password_hash, age, phone, email, role)
        )
        conn.commit()
        flash("Registration successful! Please wait for admin approval.", "success")
    except Exception as e:
        flash(f"Registration failed: {str(e)}", "error")
    finally:
        conn.close()
    
    return redirect(url_for('home.home'))

@home_bp.route('/logout')
def logout():
    """Log out current user."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home.home'))

# Temporary route to simulate login for testing purposes
@home_bp.route('/mock_login/<role>')
def mock_login(role):
    session['user_role'] = role
    session['user_name'] = f"Test {role.capitalize()}"
    flash(f"Logged in as {role}", "success")
    return redirect(url_for('dashboard.dashboard'))
