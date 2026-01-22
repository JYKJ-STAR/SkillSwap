from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.db import get_db_connection
from functools import wraps
import os
from datetime import datetime
from flask import current_app

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# =====================================================
# DECORATOR: Require Admin Role
# =====================================================
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if admin is logged in via admin table
        if not session.get('is_admin') or not session.get('admin_id'):
            flash("Admin access required.", "error")
            return redirect(url_for('admin.admin_login_page'))
        return f(*args, **kwargs)
    return decorated_function

# =====================================================
# ADMIN AUTHENTICATION (Separate from User Auth)
# =====================================================
@admin_bp.route('/login')
def admin_login_page():
    """Display admin login page."""
    # If already logged in as admin, redirect to dashboard
    if session.get('is_admin') and session.get('admin_id'):
        return redirect(url_for('admin.admin_dashboard'))
    return render_template('admin/admin_login.html')

@admin_bp.route('/signup')
def admin_signup_page():
    """Display admin signup page. Restricted to Privileged Admins."""
    # Check if logged in
    if not session.get('is_admin') or not session.get('admin_id'):
        flash("Privileged Admin access required to create new admins. Please log in.", "info")
        return redirect(url_for('admin.admin_login_page', next=url_for('admin.admin_signup_page')))
    
    # Check privilege
    if session.get('privileged') != 'Yes':
        flash("Access Denied. Only Privileged Admins can create new accounts.", "error")
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin/admin_signup.html')

@admin_bp.route('/signup', methods=['POST'])
def admin_signup_submit():
    """Handle admin signup."""
    # Security Check again
    if not session.get('is_admin') or session.get('privileged') != 'Yes':
        flash("Unauthorized action.", "error")
        return redirect(url_for('admin.admin_login_page'))

    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    privileged = request.form.get('privileged', 'No') # Default to No
    photo = request.files.get('photo')

    if not all([name, email, password]):
        flash("All fields are required.", "error")
        return redirect(url_for('admin.admin_signup_page'))

    # Password Complexity Validation
    import re
    strong_regex = r"^(?=.*[A-Z])(?=.*[!@#$&*]).{8,}$"
    if not re.match(strong_regex, password):
        flash("Password must have at least 8 characters, 1 uppercase letter, and 1 special character.", "error")
        return redirect(url_for('admin.admin_signup_page'))

    conn = get_db_connection()
    
    # Check if email exists
    existing = conn.execute("SELECT admin_id FROM admin WHERE email = ?", (email,)).fetchone()
    if existing:
        flash("Email already registered.", "error")
        conn.close()
        return redirect(url_for('admin.admin_signup_page'))

    # Handle Photo Upload
    photo_filename = None
    if photo and photo.filename:
        filename = secure_filename(photo.filename)
        # Use current_app.static_folder which maps to 'Styling'
        upload_folder = os.path.join(current_app.static_folder, 'img', 'admin')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Add timestamp to filename to prevent duplicates/caching issues
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        final_filename = f"{timestamp}_{filename}"
        
        photo.save(os.path.join(upload_folder, final_filename))
        photo_filename = final_filename

    # Insert Admin
    password_hash = generate_password_hash(password)
    
    conn.execute(
        "INSERT INTO admin (name, email, password_hash, photo, privileged) VALUES (?, ?, ?, ?, ?)",
        (name, email, password_hash, photo_filename, privileged)
    )
    conn.commit()
    conn.close()

    flash("New Admin account created successfully!", "success")
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/login', methods=['POST'])
def admin_login_submit():
    """Handle admin login - no role selection."""
    email = request.form.get('email')
    password = request.form.get('password')
    
    conn = get_db_connection()
    admin = conn.execute(
        "SELECT admin_id, name, password_hash, privileged FROM admin WHERE email = ?",
        (email,)
    ).fetchone()
    conn.close()
    
    if admin is None:
        flash("Admin email not found.", "error")
        return redirect(url_for('admin.admin_login_page'))
    
    # For demo: accept 'demo_hash' as valid password
    if admin['password_hash'] != 'demo_hash' and not check_password_hash(admin['password_hash'], password):
        flash("Incorrect password.", "error")
        return redirect(url_for('admin.admin_login_page'))
    
    # Set admin session (different keys from regular users)
    session['admin_id'] = admin['admin_id']
    session['admin_name'] = admin['name']
    session['is_admin'] = True
    session['privileged'] = admin['privileged']
    session['user_name'] = admin['name']  # For template compatibility
    session.permanent = True
    
    flash(f"Welcome back, {admin['name']}!", "success")
    
    # Handle 'next' redirect if present
    next_url = request.args.get('next')
    if next_url:
        return redirect(next_url)

    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/logout')
def admin_logout():
    """Clear admin session."""
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    session.pop('is_admin', None)
    session.pop('user_name', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('admin.admin_login_page'))

# =====================================================
# ADMIN DASHBOARD (All features in one page)
# =====================================================
@admin_bp.route('/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard with all features."""
    conn = get_db_connection()
    
    # Pending users
    pending_users = conn.execute(
        "SELECT user_id, name, role, email, phone FROM user WHERE verification_status = 'pending'"
    ).fetchall()
    
    # All users for points management
    all_users = conn.execute(
        "SELECT user_id, name, role, total_points FROM user ORDER BY total_points DESC"
    ).fetchall()
    
    # All events
    events = conn.execute(
        """SELECT e.event_id, e.title, e.start_datetime, e.location, e.status, g.name as grc_name
           FROM event e
           LEFT JOIN grc g ON e.grc_id = g.grc_id
           ORDER BY e.start_datetime DESC"""
    ).fetchall()
    
    # GRCs for event creation form
    grcs = conn.execute("SELECT grc_id, name FROM grc").fetchall()
    
    conn.close()
    
    return render_template('admin/admin_dashboard.html', 
                           user_name=session.get('user_name'),
                           pending_users=pending_users,
                           all_users=all_users,
                           events=events,
                           grcs=grcs)

# =====================================================
# USER VERIFICATION / APPROVAL
# =====================================================
@admin_bp.route('/approve_user/<int:user_id>', methods=['POST'])
@admin_required
def approve_user(user_id):
    """Approve a user's verification."""
    conn = get_db_connection()
    conn.execute(
        "UPDATE user SET verification_status = 'verified' WHERE user_id = ?",
        (user_id,)
    )
    conn.commit()
    conn.close()
    flash("User approved successfully.", "success")
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/reject_user/<int:user_id>', methods=['POST'])
@admin_required
def reject_user(user_id):
    """Reject (delete) a user's verification request."""
    conn = get_db_connection()
    conn.execute("DELETE FROM user WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    flash("User rejected.", "info")
    return redirect(url_for('admin.admin_dashboard'))

# =====================================================
# POINTS MANAGEMENT
# =====================================================
@admin_bp.route('/add_points/<int:user_id>', methods=['POST'])
@admin_required
def add_points(user_id):
    """Add points to a user."""
    points = int(request.form.get('points', 0))
    remarks = request.form.get('remarks', 'Admin adjustment')
    
    conn = get_db_connection()
    conn.execute(
        "UPDATE user SET total_points = total_points + ? WHERE user_id = ?",
        (points, user_id)
    )
    conn.execute(
        "INSERT INTO points_transaction (user_id, points_change, remarks) VALUES (?, ?, ?)",
        (user_id, points, remarks)
    )
    conn.commit()
    conn.close()
    flash(f"Added {points} points.", "success")
    return redirect(url_for('admin.admin_dashboard'))

# =====================================================
# EVENT CREATION
# =====================================================
@admin_bp.route('/create_event', methods=['POST'])
@admin_required
def create_event():
    """Create a new event."""
    title = request.form.get('title')
    description = request.form.get('description')
    start_datetime = request.form.get('start_datetime')
    location = request.form.get('location')
    grc_id = request.form.get('grc_id') or None
    category = request.form.get('category', 'social_games')
    led_by = request.form.get('led_by', 'employee')
    max_capacity = request.form.get('max_capacity') or None
    
    admin_id = session.get('admin_id', 1)
    
    conn = get_db_connection()
    conn.execute(
        """INSERT INTO event (created_by_user_id, grc_id, title, description, start_datetime, location, category, led_by, max_capacity)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (admin_id, grc_id, title, description, start_datetime, location, category, led_by, max_capacity)
    )
    conn.commit()
    conn.close()
    flash("Event created successfully.", "success")
    
    # Redirect back to the referring page or manage events
    referer = request.referrer
    if referer and 'manage-events' in referer:
        return redirect(url_for('admin.admin_manage_events'))
    return redirect(url_for('admin.admin_dashboard'))


# =====================================================
# EVENT MANAGEMENT PAGE
# =====================================================
@admin_bp.route('/manage-events')
@admin_required
def admin_manage_events():
    """Display the event management page with filters."""
    filter_status = request.args.get('filter', 'all')
    
    conn = get_db_connection()
    
    # Build query based on filter
    base_query = """
        SELECT 
            e.event_id, 
            e.title, 
            e.start_datetime, 
            e.location, 
            e.status, 
            e.category,
            e.led_by,
            e.max_capacity,
            g.name as grc_name,
            (SELECT COUNT(*) FROM event_booking eb WHERE eb.event_id = e.event_id AND eb.status = 'booked') as participant_count,
            (SELECT COALESCE(SUM(required_count), 0) FROM event_role_requirement err WHERE err.event_id = e.event_id) as manpower_required
        FROM event e
        LEFT JOIN grc g ON e.grc_id = g.grc_id
    """
    
    # Apply filters 
    if filter_status == 'pending':
        # Pending = status is 'open' and start_datetime is in the future
        base_query += " WHERE e.status = 'open' AND datetime(e.start_datetime) > datetime('now')"
    elif filter_status == 'approved':
        # Approved = status is 'open' (all open events)
        base_query += " WHERE e.status = 'open'"
    elif filter_status == 'past':
        # Past = cancelled OR start_datetime is in the past
        base_query += " WHERE e.status = 'cancelled' OR datetime(e.start_datetime) < datetime('now')"
    
    base_query += " ORDER BY e.start_datetime DESC"
    
    events = conn.execute(base_query).fetchall()
    
    # GRCs for event creation/edit forms
    grcs = conn.execute("SELECT grc_id, name FROM grc").fetchall()
    
    # Category display mapping
    category_display = {
        'tech_digital': '🖥️ Tech & Digital',
        'life_skills': '🍳 Life Skills',
        'health_wellness': '🧘 Health & Wellness',
        'culture_creative': '🎨 Culture & Creative',
        'social_games': '🎲 Social & Games',
        'community_projects': '🛠️ Community Projects'
    }
    
    conn.close()
    
    return render_template('admin/admin_manage_events.html',
                           user_name=session.get('admin_name'),
                           admin_email=session.get('admin_email', 'Admin@123.com'),
                           events=events,
                           grcs=grcs,
                           category_display=category_display,
                           current_filter=filter_status)


@admin_bp.route('/update-event/<int:event_id>', methods=['POST'])
@admin_required
def admin_update_event(event_id):
    """Update an existing event."""
    title = request.form.get('title')
    description = request.form.get('description')
    start_datetime = request.form.get('start_datetime')
    location = request.form.get('location')
    grc_id = request.form.get('grc_id') or None
    category = request.form.get('category', 'social_games')
    led_by = request.form.get('led_by', 'employee')
    status = request.form.get('status', 'open')
    max_capacity = request.form.get('max_capacity') or None
    
    conn = get_db_connection()
    conn.execute(
        """UPDATE event 
           SET title = ?, description = ?, start_datetime = ?, location = ?, 
               grc_id = ?, category = ?, led_by = ?, status = ?, max_capacity = ?
           WHERE event_id = ?""",
        (title, description, start_datetime, location, grc_id, category, led_by, status, max_capacity, event_id)
    )
    conn.commit()
    conn.close()
    
    flash("Event updated successfully.", "success")
    return redirect(url_for('admin.admin_manage_events'))


@admin_bp.route('/delete-event/<int:event_id>', methods=['POST'])
@admin_required
def admin_delete_event(event_id):
    """Delete an event."""
    conn = get_db_connection()
    conn.execute("DELETE FROM event WHERE event_id = ?", (event_id,))
    conn.commit()
    conn.close()
    
    flash("Event deleted successfully.", "success")
    return redirect(url_for('admin.admin_manage_events'))


# =====================================================
# USER MANAGEMENT PAGE
# =====================================================
@admin_bp.route('/manage-users')
@admin_required
def admin_manage_users():
    """Display the user management page."""
    conn = get_db_connection()
    
    # Get all users
    all_users = conn.execute(
        """SELECT user_id, name, email, phone, role, verification_status, total_points, created_at
           FROM user ORDER BY created_at DESC"""
    ).fetchall()
    
    conn.close()
    
    return render_template('admin/admin_manage_users.html',
                           user_name=session.get('admin_name'),
                           admin_email=session.get('admin_email', 'Admin@123.com'),
                           all_users=all_users)


# =====================================================
# SUPPORT TICKETS PAGE
# =====================================================
@admin_bp.route('/support-tickets')
@admin_required
def admin_support_tickets():
    """Display the support tickets management page."""
    conn = get_db_connection()
    
    # Get all support tickets
    tickets = conn.execute(
        """SELECT st.ticket_id, st.subject, st.description, st.status, st.created_at,
                  u.name as user_name, u.email as user_email
           FROM support_ticket st
           JOIN user u ON st.user_id = u.user_id
           ORDER BY st.created_at DESC"""
    ).fetchall()
    
    conn.close()
    
    return render_template('admin/admin_support_tickets.html',
                           user_name=session.get('admin_name'),
                           admin_email=session.get('admin_email', 'Admin@123.com'),
                           tickets=tickets)


# =====================================================
# MANAGE REWARDS PAGE (Placeholder)
# =====================================================
@admin_bp.route('/manage-rewards')
@admin_required
def admin_manage_rewards():
    """Display the rewards management page."""
    conn = get_db_connection()
    
    # Get all rewards
    rewards = conn.execute(
        """SELECT reward_id, name, description, points_required, is_active, total_quantity
           FROM reward ORDER BY points_required ASC"""
    ).fetchall()
    
    conn.close()
    
    return render_template('admin/admin_manage_rewards.html',
                           user_name=session.get('admin_name'),
                           admin_email=session.get('admin_email', 'Admin@123.com'),
                           rewards=rewards)
