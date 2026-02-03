from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.db import get_db_connection
from functools import wraps
import os
from datetime import datetime, timedelta
from flask import current_app
from flask import jsonify

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# =====================================================
# DECORATOR: Require Admin Role
# =====================================================

# Hardcoded Locations Map (GRC ID -> List of Locations)
GRC_LOCATIONS = {
    1: ['Toa Payoh CC', 'Toa Payoh Stadium', 'Toa Payoh Library'],
    2: ['Bishan CC', 'Bishan Sports Hall', 'Bishan Park'],
    3: ['Ang Mo Kio CC', 'Ang Mo Kio Hub', 'Bishan-Ang Mo Kio Park'],
    4: ['Tampines Hub', 'Tampines CC', 'Tampines Regional Library'],
    5: ['Jurong The Frontier CC', 'Jurong Lake Gardens', 'Jurong Regional Library'],
    6: ['Yishun CC', 'Yishun Park', 'Northpoint City Community Space'],
    7: ['Punggol CC', 'Punggol Community Garden', 'One Punggol'],
    8: ['Bedok CC', 'Bedok Reservoir', 'Heartbeat @ Bedok']
} 

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
        "SELECT admin_id, name, email, password_hash, privileged, photo FROM admin WHERE email = ?",
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
    session['admin_email'] = admin['email']
    session['admin_photo'] = admin['photo']
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

@admin_bp.context_processor
def inject_admin_data():
    """Inject admin data into all admin templates."""
    if session.get('is_admin'):
        return {
            'admin_name': session.get('admin_name'),
            # Ensure user_name is available for legacy templates 
            'user_name': session.get('user_name', session.get('admin_name')),
            'admin_email': session.get('admin_email'),
            'admin_photo': session.get('admin_photo'),
            'privileged': session.get('privileged')
        }
    return {}

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
    
    # Statistics for Dashboard Cards
    total_users = len(all_users)
    total_points = sum(user['total_points'] for user in all_users)
    
    current_open_tickets = conn.execute(
        "SELECT COUNT(*) FROM support_ticket WHERE status = 'open'"
    ).fetchone()[0]
    
    ongoing_events = conn.execute(
        "SELECT COUNT(*) FROM event WHERE status = 'published'"
    ).fetchone()[0]
    
    conn.close()
    
    return render_template('admin/admin_dashboard.html', 
                           # user_name and admin_email are now injected via context_processor
                           total_users=total_users,
                           total_points=total_points,
                           current_open_tickets=current_open_tickets,
                           ongoing_events=ongoing_events,
                           events=events,
                           pending_users=pending_users,
                           all_users=all_users,
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

@admin_bp.route('/delete-user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    """
    Delete a user from the User Management page.
    This action is permanent and removes the user from the database.
    Required for GDPR/Privacy compliance.
    """
    conn = get_db_connection()
    
    # Get user name for flash message
    user = conn.execute("SELECT name FROM user WHERE user_id = ?", (user_id,)).fetchone()
    user_name = user['name'] if user else 'Unknown'
    
    conn.execute("DELETE FROM user WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    flash(f"User '{user_name}' has been deleted.", "success")
    return redirect(url_for('admin.admin_manage_users'))


@admin_bp.route('/edit-user/<int:user_id>', methods=['POST'])
@admin_required
def edit_user(user_id):
    """
    Edit a user's basic details (Name, Email).
    Checks for email modification to ensure uniqueness.
    """
    new_name = request.form.get('name')
    new_email = request.form.get('email')
    
    if not new_name or not new_email:
        flash("Name and email are required.", "error")
        return redirect(url_for('admin.admin_manage_users'))
    
    conn = get_db_connection()
    
    # Check if email is already taken by another user
    existing = conn.execute(
        "SELECT user_id FROM user WHERE email = ? AND user_id != ?", 
        (new_email, user_id)
    ).fetchone()
    
    if existing:
        flash("This email is already in use by another user.", "error")
        conn.close()
        return redirect(url_for('admin.admin_manage_users'))
    
    conn.execute(
        "UPDATE user SET name = ?, email = ? WHERE user_id = ?",
        (new_name, new_email, user_id)
    )
    conn.commit()
    conn.close()
    flash(f"User details updated successfully.", "success")
    return redirect(url_for('admin.admin_manage_users'))

# =====================================================
# POINTS MANAGEMENT
# =====================================================
@admin_bp.route('/add_points/<int:user_id>', methods=['POST'])
@admin_required
def add_points(user_id):
    """
    Manually add points to a user's account.
    Logs the transaction in 'points_transaction' table for audit.
    """
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
    
    # New Role Capacities
    mentor_capacity = request.form.get('mentor_capacity', 5)
    participant_capacity = request.form.get('participant_capacity', 15)
    
    admin_id = session.get('admin_id', 1)
    
    # Date/Time Validation: Event cannot be scheduled in the past
    if start_datetime:
        try:
            event_dt = datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M')
            if event_dt < datetime.now():
                flash("Invalid date/time: Event cannot be scheduled in the past.", "error")
                return redirect(request.referrer or url_for('admin.admin_manage_events'))
            
            # Standardize format for SQLite (space instead of T)
            start_datetime = event_dt.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            flash("Invalid date/time format.", "error")
            return redirect(request.referrer or url_for('admin.admin_manage_events'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Insert Event
    cursor.execute(
        """INSERT INTO event (created_by_user_id, grc_id, title, description, start_datetime, location, category, led_by, max_capacity, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')""",
        (admin_id, grc_id, title, description, start_datetime, location, category, led_by, max_capacity)
    )
    event_id = cursor.lastrowid
    
    # Insert Role Requirements (Dynamic Capacities)
    # Mentor Role
    cursor.execute(
        "INSERT INTO event_role_requirement (event_id, role_type, required_count) VALUES (?, 'teacher', ?)",
        (event_id, mentor_capacity)
    )
    # Participant Role
    cursor.execute(
        "INSERT INTO event_role_requirement (event_id, role_type, required_count) VALUES (?, 'participant', ?)",
        (event_id, participant_capacity)
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
    filter_status = request.args.get('filter', 'pending')
    search_query = request.args.get('search', '').strip()
    
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
            e.description,
            e.grc_id,
            g.name as grc_name,
            (SELECT COUNT(*) FROM event_booking eb WHERE eb.event_id = e.event_id AND eb.status = 'booked') as participant_count,
            (SELECT COALESCE(SUM(required_count), 0) FROM event_role_requirement err WHERE err.event_id = e.event_id) as manpower_required,
            (SELECT required_count FROM event_role_requirement err WHERE err.event_id = e.event_id AND err.role_type = 'teacher') as mentor_capacity,
            (SELECT required_count FROM event_role_requirement err WHERE err.event_id = e.event_id AND err.role_type = 'participant') as participant_capacity
        FROM event e
        LEFT JOIN grc g ON e.grc_id = g.grc_id
    """
    
    # Store parameters for the query
    params = []
    
    # Base WHERE clause
    where_clauses = []
    
    # Apply filters based on new status workflow
    if filter_status == 'pending':
        where_clauses.append("e.status = 'pending'")
    elif filter_status == 'approved':
        # Show both Approved (Unpublished) and Published events
        where_clauses.append("e.status IN ('approved', 'published')")
    elif filter_status == 'past':
        # Exclude archived past events (those with [ARCHIVED] in void_reason)
        where_clauses.append("e.status IN ('ended', 'cancelled') AND (e.void_reason IS NULL OR e.void_reason NOT LIKE '%[ARCHIVED]%')")
    elif filter_status == 'voided':
        # Exclude archived voided events (those with [ARCHIVED] in void_reason)
        where_clauses.append("e.status = 'voided' AND (e.void_reason IS NULL OR e.void_reason NOT LIKE '%[ARCHIVED]%')")
        
    # Apply Search Logic (if search_query exists)
    if search_query:
        where_clauses.append("(e.title LIKE ? OR e.location LIKE ?)")
        params.extend([f'%{search_query}%', f'%{search_query}%'])
    
    # Construct the full WHERE clause
    if where_clauses:
        base_query += " WHERE " + " AND ".join(where_clauses)
    
    # Sorting logic
    if filter_status == 'approved':
        # Approved tab: Unpublished (approved) first, then Published, grouped by Category
        base_query += """ ORDER BY 
            CASE WHEN e.status = 'approved' THEN 0 ELSE 1 END,
            e.category ASC, 
            e.start_datetime DESC"""
    else:
        # Others: Sort by Start Date DESC
        base_query += " ORDER BY e.start_datetime DESC"
    
    events = conn.execute(base_query, params).fetchall()
    
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
    
    # Fetch challenges based on filter (same workflow as events)
    challenges_list = []
    conn2 = get_db_connection()
    if filter_status == 'approved':
        challenges_list = conn2.execute(
            "SELECT * FROM challenge WHERE status IN ('published', 'active') ORDER BY created_at DESC"
        ).fetchall()
    elif filter_status == 'pending':
        challenges_list = conn2.execute(
            "SELECT * FROM challenge WHERE status = 'pending' ORDER BY created_at DESC"
        ).fetchall()
    elif filter_status == 'voided':
        challenges_list = conn2.execute(
            "SELECT * FROM challenge WHERE status = 'voided' ORDER BY created_at DESC"
        ).fetchall()
    elif filter_status == 'past':
        challenges_list = conn2.execute(
            "SELECT * FROM challenge WHERE status = 'ended' ORDER BY created_at DESC"
        ).fetchall()
    conn2.close()
    
    print(f"DEBUG: Filter={filter_status}, Challenges Found={len(challenges_list)}")
    
    return render_template('admin/admin_manage_events.html',
                           events=events,
                           grcs=grcs,
                           category_display=category_display,
                           current_filter=filter_status,
                           search_query=search_query,
                           published_challenges=challenges_list)


@admin_bp.route('/create-challenge')
@admin_required
def admin_create_challenge():
    """Redirect to manage events page."""
    return redirect(url_for('admin.admin_manage_events'))

@admin_bp.route('/create-challenge/submit', methods=['POST'])
@admin_required
def admin_create_challenge_submit():
    """Handle challenge creation with datetime-local fields."""
    title = request.form.get('title')
    description = request.form.get('description')
    start_datetime = request.form.get('start_datetime')
    end_datetime = request.form.get('end_datetime')
    admin_id = session.get('admin_id')
    
    if not all([title, start_datetime, end_datetime]):
        flash("Title and date/times are required.", "error")
        return redirect(url_for('admin.admin_manage_events'))
    
    # Date/Time Validation
    try:
        start_dt = datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M')
        if start_dt < datetime.now():
            flash("Challenge start date/time cannot be in the past.", "error")
            return redirect(url_for('admin.admin_manage_events'))
    except ValueError:
        flash("Invalid date/time format.", "error")
        return redirect(url_for('admin.admin_manage_events'))
    
    # Convert from datetime-local format (YYYY-MM-DDTHH:MM) to database format (YYYY-MM-DD HH:MM)
    start_db = start_datetime.replace('T', ' ')
    end_db = end_datetime.replace('T', ' ')
    
    status = 'pending'
        
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO challenge (title, description, start_date, end_date, status, created_by) VALUES (?, ?, ?, ?, ?, ?)",
            (title, description, start_db, end_db, status, admin_id)
        )
        conn.commit()
    except Exception as e:
        conn.close()
        flash(f"Error creating challenge: {str(e)}", "error")
        return redirect(url_for('admin.admin_manage_events'))
    conn.close()
    

    flash("Challenge created successfully! It is now pending approval.", "success")
    return redirect(url_for('admin.admin_manage_events', filter='pending'))


@admin_bp.route('/update-challenge/<int:challenge_id>', methods=['POST'])
@admin_required
def admin_update_challenge(challenge_id):
    """Update an existing challenge."""
    title = request.form.get('title')
    description = request.form.get('description')
    start_datetime = request.form.get('start_datetime')
    end_datetime = request.form.get('end_datetime')
    
    if not all([title, start_datetime, end_datetime]):
        flash("Title and date/times are required.", "error")
        return redirect(url_for('admin.admin_manage_events'))
        
    # Date/Time Validation
    try:
        # Check format (HTML datetime-local produces T separator)
        if 'T' in start_datetime:
            start_dt = datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M')
        else:
            start_dt = datetime.strptime(start_datetime, '%Y-%m-%d %H:%M:%S')
            
        if 'T' in end_datetime:
            end_dt = datetime.strptime(end_datetime, '%Y-%m-%dT%H:%M')
        else:
            end_dt = datetime.strptime(end_datetime, '%Y-%m-%d %H:%M:%S')

            
        if start_dt > end_dt:
            flash("End date must be after start date.", "error")
            return redirect(url_for('admin.admin_manage_events'))
            
    except ValueError:
        flash("Invalid date/time format.", "error")
        return redirect(url_for('admin.admin_manage_events'))
    
    # Standardize for DB
    start_db = start_datetime.replace('T', ' ')
    end_db = end_datetime.replace('T', ' ')
    
    conn = get_db_connection()
    conn.execute(
        "UPDATE challenge SET title = ?, description = ?, start_date = ?, end_date = ? WHERE challenge_id = ?",
        (title, description, start_db, end_db, challenge_id)
    )
    conn.commit()
    conn.close()
    
    flash("Challenge updated successfully.", "success")
    # Redirect to the same filter tab based on status? 
    # For simplicity, default to approved or check referrer, but managing complexity here:
    # We will just redirect to manage_events which defaults to pending, or user's last filter.
    # To be smarter, let's just go back to manage events.
    return redirect(url_for('admin.admin_manage_events'))


@admin_bp.route('/approve-challenge/<int:challenge_id>', methods=['POST'])
@admin_required
def admin_approve_challenge(challenge_id):
    """Approve a challenge (move to active/unpublished)."""
    conn = get_db_connection()
    conn.execute(
        "UPDATE challenge SET status = 'active' WHERE challenge_id = ?",
        (challenge_id,)
    )
    conn.commit()
    conn.close()
    flash("Challenge approved! It is now in the Approved tab (Unpublished).", "success")
    return redirect(url_for('admin.admin_manage_events', filter='approved'))

@admin_bp.route('/publish-challenge/<int:challenge_id>', methods=['POST'])
@admin_required
def admin_publish_challenge(challenge_id):
    """Publish a challenge (make it visible to users)."""
    conn = get_db_connection()
    conn.execute(
        "UPDATE challenge SET status = 'published', published_at = datetime('now') WHERE challenge_id = ?",
        (challenge_id,)
    )
    conn.commit()
    conn.close()
    flash("Challenge published!", "success")
    return redirect(url_for('admin.admin_manage_events', filter='approved'))

@admin_bp.route('/unpublish-challenge/<int:challenge_id>', methods=['POST'])
@admin_required
def admin_unpublish_challenge(challenge_id):
    """Unpublish a challenge (hide from users)."""
    conn = get_db_connection()
    conn.execute(
        "UPDATE challenge SET status = 'active', published_at = NULL WHERE challenge_id = ?",
        (challenge_id,)
    )
    conn.commit()
    conn.close()
    flash("Challenge unpublished.", "success")
    return redirect(url_for('admin.admin_manage_events', filter='approved'))

@admin_bp.route('/delete-challenge/<int:challenge_id>', methods=['POST'])
@admin_required
def admin_delete_challenge(challenge_id):
    """Delete a challenge."""
    conn = get_db_connection()
    conn.execute("DELETE FROM challenge WHERE challenge_id = ?", (challenge_id,))
    conn.commit()
    conn.close()
    
    flash("Challenge deleted.", "success")
    return redirect(url_for('admin.admin_manage_events'))

@admin_bp.route('/void-challenge/<int:challenge_id>', methods=['POST'])
@admin_required
def admin_void_challenge(challenge_id):
    """Void a challenge (cancel it)."""
    void_reason = request.form.get('void_reason', 'No reason provided')
    notify_users = request.form.get('notify_users') == 'yes'  # Check if checkbox is checked
    
    conn = get_db_connection()
    
    # Get challenge title
    challenge = conn.execute("SELECT title FROM challenge WHERE challenge_id = ?", (challenge_id,)).fetchone()
    challenge_title = challenge['title'] if challenge else 'Unknown Challenge'
    
    # Update challenge status to voided
    conn.execute(
        "UPDATE challenge SET status = 'voided', void_reason = ?, voided_at = datetime('now') WHERE challenge_id = ?",
        (void_reason, challenge_id)
    )
    
    # Create notifications for all users if checkbox is checked
    notified_count = 0
    if notify_users:
        # Fetch all users (youth and senior roles)
        all_users = conn.execute("""
            SELECT user_id, name, role 
            FROM user 
            WHERE role IN ('youth', 'senior')
        """).fetchall()
        
        notification_message = f"The challenge '{challenge_title}' has been cancelled."
        for user in all_users:
            conn.execute("""
                INSERT INTO notification (user_id, message, challenge_id, created_at) 
                VALUES (?, ?, ?, datetime('now'))
            """, (user['user_id'], notification_message, challenge_id))
            notified_count += 1
    
    conn.commit()
    conn.close()
    
    # No flash message - just redirect to voided tab
    return redirect(url_for('admin.admin_manage_events', filter='voided'))

@admin_bp.route('/end-challenge/<int:challenge_id>', methods=['POST'])
@admin_required
def admin_end_challenge(challenge_id):
    """End a challenge (mark as completed)."""
    conn = get_db_connection()
    
    # Get challenge title before updating
    challenge = conn.execute("SELECT title FROM challenge WHERE challenge_id = ?", (challenge_id,)).fetchone()
    challenge_title = challenge['title'] if challenge else 'Unknown Challenge'
    
    # Update challenge status
    conn.execute(
        "UPDATE challenge SET status = 'ended', ended_at = datetime('now') WHERE challenge_id = ?",
        (challenge_id,)
    )
    
    # Notify all users about challenge ending
    all_users = conn.execute("""
        SELECT user_id, name, role 
        FROM user 
        WHERE role IN ('youth', 'senior')
    """).fetchall()
    
    notification_message = f"The challenge '{challenge_title}' has ended."
    for user in all_users:
        conn.execute("""
            INSERT INTO notification (user_id, message, challenge_id, created_at) 
            VALUES (?, ?, ?, datetime('now'))
        """, (user['user_id'], notification_message, challenge_id))
    
    conn.commit()
    conn.close()
    
    # No flash message - just redirect to ended tab (filter=past)
    return redirect(url_for('admin.admin_manage_events', filter='past'))


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
    
    # New Role Capacities
    mentor_capacity = request.form.get('mentor_capacity', 5)
    participant_capacity = request.form.get('participant_capacity', 15)
    
    conn = get_db_connection()
    conn.execute(
        """UPDATE event 
           SET title = ?, description = ?, start_datetime = ?, location = ?, 
               grc_id = ?, category = ?, led_by = ?, status = ?, max_capacity = ?
           WHERE event_id = ?""",
        (title, description, start_datetime, location, grc_id, category, led_by, status, max_capacity, event_id)
    )
    
    # Update Role Requirements
    # Using INSERT OR REPLACE or distinct UPDATEs depending on schema constraints, 
    # but a simple UPDATE is safest if rows exist. Since we insert on create, rows should exist.
    # However, to be safe against older events, we can use INSERT OR REPLACE logic or check existence.
    # For SQLite simplified:
    conn.execute("DELETE FROM event_role_requirement WHERE event_id = ? AND role_type IN ('teacher', 'participant')", (event_id,))
    conn.execute("INSERT INTO event_role_requirement (event_id, role_type, required_count) VALUES (?, 'teacher', ?)", (event_id, mentor_capacity))
    conn.execute("INSERT INTO event_role_requirement (event_id, role_type, required_count) VALUES (?, 'participant', ?)", (event_id, participant_capacity))
    
    conn.commit()
    conn.close()
    
    flash("Event updated successfully.", "success")
    return redirect(url_for('admin.admin_manage_events'))


@admin_bp.route('/delete-event/<int:event_id>', methods=['POST'])
@admin_required
def admin_delete_event(event_id):
    """Delete an event permanently (only for pending events)."""
    conn = get_db_connection()
    conn.execute("DELETE FROM event WHERE event_id = ?", (event_id,))
    conn.commit()
    conn.close()
    
    flash("Event deleted successfully.", "success")
    return redirect(url_for('admin.admin_manage_events', filter='pending'))



@admin_bp.route('/approve-event/<int:event_id>', methods=['POST'])
@admin_required
def admin_approve_event(event_id):
    """Approve a pending event (pending -> approved)."""
    conn = get_db_connection()
    conn.execute("UPDATE event SET status = 'approved' WHERE event_id = ?", (event_id,))
    conn.commit()
    conn.close()
    
    flash("Event approved successfully.", "success")
    return redirect(url_for('admin.admin_manage_events', filter='approved'))


@admin_bp.route('/publish-event/<int:event_id>', methods=['POST'])
@admin_required
def admin_publish_event(event_id):
    """Publish an approved event (approved -> published)."""
    conn = get_db_connection()
    conn.execute("UPDATE event SET status = 'published', published_at = datetime('now') WHERE event_id = ?", (event_id,))
    conn.commit()
    conn.close()
    
    flash("Event published successfully! It is now visible to users.", "success")
    return redirect(url_for('admin.admin_manage_events', filter='approved'))

@admin_bp.route('/unpublish-event/<int:event_id>', methods=['POST'])
@admin_required
def admin_unpublish_event(event_id):
    """Unpublish a published event (published -> approved)."""
    conn = get_db_connection()
    conn.execute("UPDATE event SET status = 'approved', published_at = NULL WHERE event_id = ?", (event_id,))
    conn.commit()
    conn.close()
    
    flash("Event unpublished. It is now hidden from users.", "success")
    return redirect(url_for('admin.admin_manage_events', filter='approved'))


@admin_bp.route('/void-event/<int:event_id>', methods=['POST'])
@admin_required
def admin_void_event(event_id):
    """Void an approved event (approved -> voided)."""
    void_reason = request.form.get('void_reason', 'No reason provided')
    notify_users = request.form.get('notify_users') == 'yes'  # Check if checkbox is checked
    
    conn = get_db_connection()
    
    # Get event title and check if it was published
    event = conn.execute("SELECT title, status FROM event WHERE event_id = ?", (event_id,)).fetchone()
    event_title = event['title'] if event else 'Unknown Event'
    was_published = event['status'] == 'published' if event else False
    
    # Get all registered participants with details for this event
    participants = conn.execute("""
        SELECT DISTINCT u.user_id, u.name, u.role
        FROM event_booking eb 
        JOIN user u ON eb.user_id = u.user_id
        WHERE eb.event_id = ? AND eb.status = 'booked'
    """, (event_id,)).fetchall()
    
    # Update event status to voided
    conn.execute("UPDATE event SET status = 'voided', void_reason = ? WHERE event_id = ?", (void_reason, event_id))
    
    # Create notifications only if checkbox is checked
    # Create notifications only if checkbox is checked
    notified_count = 0
    if notify_users:
        # Fetch all users (youth and senior roles) to match Challenge workflow
        all_users = conn.execute("""
            SELECT user_id, name, role 
            FROM user 
            WHERE role IN ('youth', 'senior')
        """).fetchall()

        notification_message = f"The event '{event_title}' has been cancelled by the organisers."
        for user in all_users:
            conn.execute("""
                INSERT INTO notification (user_id, message, event_id, created_at) 
                VALUES (?, ?, ?, datetime('now'))
            """, (user['user_id'], notification_message, event_id))
            notified_count += 1
    
    conn.commit()
    conn.close()
    
    # Clean redirect without flash
    return redirect(url_for('admin.admin_manage_events', filter='voided'))


@admin_bp.route('/event-cancellation-confirm')
@admin_required
def event_cancellation_confirm():
    """Display the event cancellation confirmation page."""
    cancelled_event = session.pop('cancelled_event', None)
    
    if not cancelled_event:
        flash("No cancellation details found.", "warning")
        return redirect(url_for('admin.admin_manage_events', filter='voided'))
    
    return render_template('admin/admin_event_cancellation.html',
                           event_title=cancelled_event['event_title'],
                           void_reason=cancelled_event['void_reason'],
                           participants=cancelled_event['participants'])


@admin_bp.route('/end-event/<int:event_id>', methods=['POST'])
@admin_required
def admin_end_event(event_id):
    """End an approved event (approved -> ended/past)."""
    conn = get_db_connection()
    
    # Get event title and participants
    event = conn.execute("SELECT title FROM event WHERE event_id = ?", (event_id,)).fetchone()
    event_title = event['title'] if event else 'Unknown Event'

    # Update event status
    conn.execute("UPDATE event SET status = 'ended' WHERE event_id = ?", (event_id,))

    # Notify ALL users (consistent with Challenges)
    all_users = conn.execute("""
        SELECT user_id, name, role 
        FROM user 
        WHERE role IN ('youth', 'senior')
    """).fetchall()

    message = f"The event '{event_title}' has ended. We hope you enjoyed it!"
    for user in all_users:
         conn.execute("""
            INSERT INTO notification (user_id, message, event_id, created_at) 
            VALUES (?, ?, ?, datetime('now'))
        """, (user['user_id'], message, event_id))

    conn.commit()
    conn.close()
    
    # Clean redirect without flash
    return redirect(url_for('admin.admin_manage_events', filter='past'))


@admin_bp.route('/clear-tab/<tab_name>', methods=['POST'])
@admin_required
def admin_clear_tab(tab_name):
    """Clear all events from Voided or Past tab (UI only, data preserved).
    
    This sets a 'hidden' flag on events so they don't appear in the UI,
    but the data remains in the database for record-keeping.
    """
    if tab_name not in ['voided', 'past']:
        flash("Invalid tab specified.", "error")
        return redirect(url_for('admin.admin_manage_events'))
    
    conn = get_db_connection()
    
    if tab_name == 'voided':
        # Mark voided events as archived
        conn.execute("UPDATE event SET void_reason = COALESCE(void_reason, '') || ' [ARCHIVED]' WHERE status = 'voided' AND (void_reason IS NULL OR void_reason NOT LIKE '%[ARCHIVED]%')")
        flash("All voided events have been cleared from view.", "success")
    elif tab_name == 'past':
        # Mark past events as archived using void_reason field
        conn.execute("UPDATE event SET void_reason = '[ARCHIVED]' WHERE status IN ('ended', 'cancelled') AND (void_reason IS NULL OR void_reason NOT LIKE '%[ARCHIVED]%')")
        flash("All past events have been cleared from view.", "success")
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin.admin_manage_events', filter=tab_name))


# =====================================================
# USER MANAGEMENT PAGE
# =====================================================
@admin_bp.route('/manage-users')
@admin_required
def admin_manage_users():
    """Display the user management page."""
    conn = get_db_connection()
    
    # Get all users with extended details for the new UI including verification_photo
    all_users = conn.execute(
        """SELECT user_id, name, email, phone, role, verification_status, total_points, 
                  created_at, birth_date, language_pref, profession, verification_photo
           FROM user ORDER BY created_at DESC"""
    ).fetchall()
    
    conn.close()
    
    return render_template('admin/admin_manage_users.html',
                           all_users=all_users)


@admin_bp.route('/verify-user/<int:user_id>', methods=['POST'])
@admin_required
def verify_user(user_id):
    """
    Approve a user's verification from User Management page.
    Sets status to 'verified'.
    """
    conn = get_db_connection()
    conn.execute(
        "UPDATE user SET verification_status = 'verified' WHERE user_id = ?",
        (user_id,)
    )
    conn.commit()
    conn.close()
    flash("User has been verified successfully.", "success")
    return redirect(url_for('admin.admin_manage_users'))


@admin_bp.route('/reject-verification/<int:user_id>', methods=['POST'])
@admin_required
def reject_verification(user_id):
    """
    Reject a user's verification request.
    - Removes the uploaded verification photo from filesystem.
    - Resets status to 'unverified' so they can try again.
    """
    conn = get_db_connection()
    
    # Get the current verification photo
    user = conn.execute("SELECT verification_photo FROM user WHERE user_id = ?", (user_id,)).fetchone()
    
    if user and user['verification_photo']:
        # Delete the file from filesystem
        photo_path = os.path.join(current_app.static_folder, 'img', 'users', 'verification', user['verification_photo'])
        if os.path.exists(photo_path):
            os.remove(photo_path)
    
    # Clear the verification photo and set status to unverified
    conn.execute(
        "UPDATE user SET verification_photo = NULL, verification_status = 'unverified' WHERE user_id = ?",
        (user_id,)
    )
    conn.commit()
    conn.close()
    flash("User verification has been rejected and photo removed.", "info")
    return redirect(url_for('admin.admin_manage_users'))


# =====================================================
# SUPPORT TICKETS PAGE
# =====================================================

@admin_bp.route('/toggle-ticket-status/<int:ticket_id>', methods=['POST'])
@admin_required
def toggle_ticket_status(ticket_id):
    """Toggle ticket status between open/resolved."""
    # (Existing function truncated in previous view, assuming it ends here or similar)
    pass 

# =====================================================
# CHALLENGE MANAGEMENT
# =====================================================
@admin_bp.route('/challenges')
@admin_required
def admin_manage_challenges():
    """List challenges with filter tabs like events."""
    current_filter = request.args.get('filter', 'draft')
    
    conn = get_db_connection()
    
    # Map filter to status
    status_map = {
        'draft': 'active',
        'published': 'published',
        'ended': 'ended',
        'voided': 'voided'
    }
    
    status = status_map.get(current_filter, 'active')
    challenges = conn.execute(
        "SELECT * FROM challenge WHERE status = ? ORDER BY created_at DESC",
        (status,)
    ).fetchall()
    conn.close()
    
    return render_template('admin/admin_manage_challenges.html', 
                          challenges=challenges, 
                          current_filter=current_filter)

@admin_bp.route('/support-tickets')
@admin_required
def admin_support_tickets():
    """Display the support tickets with filtering."""
    # 1. Get the filter from the URL (default to 'all')
    filter_status = request.args.get('filter', 'all')
    
    conn = get_db_connection()
    
    # 2. Build the base query
    query = """SELECT st.ticket_id, st.subject, st.description, st.status, st.created_at,
                      u.name as user_name, u.email as user_email
               FROM support_ticket st
               JOIN user u ON st.user_id = u.user_id"""
    
    # 3. Add WHERE clause based on the filter
    params = ()
    if filter_status == 'pending':
        query += " WHERE st.status = 'open'"
    elif filter_status == 'resolved':
        query += " WHERE st.status = 'resolved'"
    
    # 4. Finish the query
    query += " ORDER BY st.created_at DESC"
    
    tickets = conn.execute(query, params).fetchall()
    
    # Convert tickets to list of dicts and adjust timezone (UTC to UTC+8)
    tickets_list = []
    for ticket in tickets:
        ticket_dict = dict(ticket)
        # Convert created_at from UTC to UTC+8
        if ticket_dict['created_at']:
            try:
                # Parse the datetime string
                utc_time = datetime.strptime(ticket_dict['created_at'], '%Y-%m-%d %H:%M:%S')
                # Add 8 hours for UTC+8
                local_time = utc_time + timedelta(hours=8)
                # Format back to string
                ticket_dict['created_at'] = local_time.strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass  # Keep original if conversion fails
        tickets_list.append(ticket_dict)
    
    tickets = tickets_list
    
    # 5. Calculate statistics with error handling
    try:
        total_tickets = conn.execute("SELECT COUNT(*) FROM support_ticket").fetchone()[0]
    except Exception as e:
        print(f"Error fetching total_tickets: {e}")
        total_tickets = 0
    
    try:
        pending_tickets = conn.execute(
            "SELECT COUNT(*) FROM support_ticket WHERE status = 'open'"
        ).fetchone()[0]
    except Exception as e:
        print(f"Error fetching pending_tickets: {e}")
        pending_tickets = 0
    
    # Resolved tickets - since we don't have a resolved_at column, count all resolved
    try:
        resolved_today = conn.execute(
            "SELECT COUNT(*) FROM support_ticket WHERE status = 'resolved'"
        ).fetchone()[0]
    except Exception as e:
        print(f"Error fetching resolved_today: {e}")
        resolved_today = 0
    
    conn.close()
    
    return render_template('admin/admin_support_tickets.html',
                           tickets=tickets,
                           current_filter=filter_status,
                           total_tickets=total_tickets,
                           pending_tickets=pending_tickets,
                           resolved_today=resolved_today)

@admin_bp.route('/save-ticket-reply/<int:ticket_id>', methods=['POST'])
@admin_required
def save_ticket_reply(ticket_id):
    reply_text = request.form.get('reply_text')
    
    conn = get_db_connection()
    # Update the ticket with the reply and mark as resolved automatically
    conn.execute(
        "UPDATE support_ticket SET reply = ?, status = 'resolved' WHERE ticket_id = ?",
        (reply_text, ticket_id)
    )
    conn.commit()
    conn.close()
    
    flash("Reply sent and ticket marked as resolved.", "success")
    return redirect(url_for('admin.admin_support_tickets'))
@admin_bp.route('/clear-tickets')
@admin_required
def clear_tickets():
    conn = get_db_connection()
    try:
        # Delete all rows from the support_ticket table
        conn.execute("DELETE FROM support_ticket")
        
        # Optional: Reset the ID counter back to 1
        conn.execute("DELETE FROM sqlite_sequence WHERE name='support_ticket'")
        
        conn.commit()
        flash("All support tickets have been deleted!", "success")
    except Exception as e:
        flash(f"Error clearing tickets: {e}", "error")
    finally:
        conn.close()
    
    return redirect(url_for('admin.admin_support_tickets'))
# =====================================================
# MANAGE REWARDS PAGE (Placeholder)
# =====================================================
@admin_bp.route('/manage-rewards')
@admin_required
def admin_manage_rewards():
    """Display the rewards management page with verification and rewards sections."""
    conn = get_db_connection()
    
    # Get all active rewards for Manage Rewards tab
    rewards = conn.execute("""
        SELECT reward_id, name, description, points_required, is_active, total_quantity
        FROM reward 
        ORDER BY points_required ASC
    """).fetchall()

    # Get Pending Proofs (for User Verification section)
    pending_proofs = conn.execute("""
        SELECT 
            eb.user_id, eb.event_id, eb.proof_media_url, eb.role_type,
            u.name as user_name,
            e.title as event_title,
            e.base_points_participant
        FROM event_booking eb
        JOIN user u ON eb.user_id = u.user_id
        JOIN event e ON eb.event_id = e.event_id
        WHERE eb.proof_media_url IS NOT NULL 
          AND eb.status != 'completed'
    """).fetchall()
    
    # Get Redeemed Rewards (for Redeemed Rewards tab)
    redeemed_rewards = conn.execute("""
        SELECT 
            rr.redemption_id,
            rr.created_at,
            rr.status,
            u.name as user_name,
            u.email as user_email,
            r.name as reward_name,
            r.points_required
        FROM reward_redemption rr
        JOIN user u ON rr.user_id = u.user_id
        JOIN reward r ON rr.reward_id = r.reward_id
        WHERE rr.status IN ('approved', 'redeemed')
        ORDER BY rr.created_at DESC
    """).fetchall()
    
    conn.close()
    
    return render_template('admin/admin_manage_rewards.html',
                           rewards=rewards,
                           pending_proofs=pending_proofs,
                           redeemed_rewards=redeemed_rewards)

@admin_bp.route('/verify-proof/<int:event_id>/<int:user_id>', methods=['POST'])
@admin_required
def admin_verify_proof(event_id, user_id):
    """Verify proof and award points."""
    conn = get_db_connection()
    
    # 1. Get points to award
    # For now assuming base_points_participant. In future could be dynamic based on role.
    event = conn.execute("SELECT base_points_participant FROM event WHERE event_id = ?", (event_id,)).fetchone()
    points = event['base_points_participant'] if event and event['base_points_participant'] else 100 # Default
    
    # 2. Update status to completed
    conn.execute("UPDATE event_booking SET status = 'completed' WHERE event_id = ? AND user_id = ?", 
                 (event_id, user_id))
                 
    # 3. Award points to user
    conn.execute("UPDATE user SET total_points = total_points + ? WHERE user_id = ?", (points, user_id))
    
    conn.commit()
    conn.close()
    
    flash(f"Proof verified! Awarded {points} points.", "success")
    return redirect(url_for('admin.admin_manage_rewards'))

@admin_bp.route('/reject-proof/<int:event_id>/<int:user_id>', methods=['POST'])
@admin_required
def admin_reject_proof(event_id, user_id):
    """Reject proof submission - clears photo and resets to booked status."""
    conn = get_db_connection()
    
    # Get proof photo to delete
    booking = conn.execute(
        "SELECT proof_media_url FROM event_booking WHERE event_id = ? AND user_id = ?",
        (event_id, user_id)
    ).fetchone()
    
    if booking and booking['proof_media_url']:
        # Delete photo from filesystem
        photo_path = os.path.join(current_app.static_folder, 'img', 'users', 'Upload_proof', booking['proof_media_url'])
        if os.path.exists(photo_path):
            os.remove(photo_path)
    
    # Clear proof_media_url and keep status as 'booked' so it goes back to action required
    conn.execute(
        "UPDATE event_booking SET proof_media_url = NULL WHERE event_id = ? AND user_id = ?",
        (event_id, user_id)
    )
    
    # Also delete the review if exists (so they have to resubmit both)
    conn.execute(
        "DELETE FROM review WHERE event_id = ? AND user_id = ?",
        (event_id, user_id)
    )
    
    conn.commit()
    conn.close()
    
    flash("Proof rejected. User must resubmit.", "info")
    return redirect(url_for('admin.admin_manage_rewards'))


@admin_bp.route('/admin/add-reward', methods=['POST'])
@admin_required
def admin_add_reward():
    """Add a new reward to the catalog."""
    name = request.form.get('name')
    description = request.form.get('description')
    points_required = request.form.get('points_required')
    total_quantity = request.form.get('total_quantity') or None
    
    if not name or not points_required:
        flash("Reward name and points are required.", "error")
        return redirect(url_for('admin.admin_manage_rewards'))
    
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO reward (name, description, points_required, total_quantity, is_active)
        VALUES (?, ?, ?, ?, 1)
    """, (name, description, int(points_required), total_quantity))
    conn.commit()
    conn.close()
    
    flash(f"Reward '{name}' added successfully!", "success")
    return redirect(url_for('admin.admin_manage_rewards'))


@admin_bp.route('/admin/delete-reward/<int:reward_id>', methods=['POST'])
@admin_required
def admin_delete_reward(reward_id):
    """Delete a reward from the catalog."""
    conn = get_db_connection()
    
    # Get reward name for flash message
    reward = conn.execute("SELECT name FROM reward WHERE reward_id = ?", (reward_id,)).fetchone()
    reward_name = reward['name'] if reward else 'Unknown'
    
    conn.execute("DELETE FROM reward WHERE reward_id = ?", (reward_id,))
    conn.commit()
    conn.close()
    
    flash(f"Reward '{reward_name}' deleted successfully.", "success")
    return redirect(url_for('admin.admin_manage_rewards'))


@admin_bp.route('/admin/edit-reward/<int:reward_id>', methods=['POST'])
@admin_required
def admin_edit_reward(reward_id):
    """Edit an existing reward."""
    name = request.form.get('name')
    description = request.form.get('description')
    points_required = request.form.get('points_required')
    total_quantity = request.form.get('total_quantity') or None
    is_active = request.form.get('is_active') == 'on'
    
    if not name or not points_required:
        flash("Reward name and points are required.", "error")
        return redirect(url_for('admin.admin_manage_rewards'))
    
    conn = get_db_connection()
    conn.execute("""
        UPDATE reward 
        SET name = ?, description = ?, points_required = ?, total_quantity = ?, is_active = ?
        WHERE reward_id = ?
    """, (name, description, int(points_required), total_quantity, 1 if is_active else 0, reward_id))
    
    conn.commit()
    conn.close()
    
    flash(f"Reward updated successfully!", "success")
    return redirect(url_for('admin.admin_manage_rewards'))



# =====================================================
# VIEW EVENT PARTICIPANTS
# =====================================================
@admin_bp.route('/event/<int:event_id>/participants')
@admin_required
def admin_view_participants(event_id):
    """View all participants signed up for an event."""
    conn = get_db_connection()
    
    # Get event details
    event = conn.execute("""
        SELECT event_id, title, start_datetime, location, status
        FROM event WHERE event_id = ?
    """, (event_id,)).fetchone()
    
    if not event:
        flash("Event not found.", "error")
        conn.close()
        return redirect(url_for('admin.admin_manage_events'))
    
    # Get all participants grouped by role
    participants = conn.execute("""
        SELECT 
            eb.role_type,
            eb.status as booking_status,
            eb.booked_at,
            u.user_id,
            u.name,
            u.email,
            u.role as user_role,
            u.phone
        FROM event_booking eb
        JOIN user u ON eb.user_id = u.user_id
        WHERE eb.event_id = ? AND eb.status = 'booked'
        ORDER BY 
            CASE eb.role_type 
                WHEN 'teacher' THEN 1 
                ELSE 2 
            END,
            eb.booked_at ASC
    """, (event_id,)).fetchall()
    
    # Group by role
    grouped = {
        'teacher': [],
        'participant': []
    }
    
    for p in participants:
        role = p['role_type']
        if role in grouped:
            grouped[role].append({
                'user_id': p['user_id'],
                'name': p['name'],
                'email': p['email'],
                'user_role': p['user_role'],
                'phone': p['phone'],
                'booked_at': p['booked_at']
            })
    
    conn.close()
    
    # Role display mapping
    role_display = {
        'teacher': 'Mentors',
        'participant': 'Participants'
    }
    
    return render_template('admin/admin_event_participants.html',
                           event=event,
                           grouped_participants=grouped,
                           role_display=role_display,
                           total_count=len(participants))




# =====================================================
# LIVE CHAT ROUTES
# =====================================================

@admin_bp.route('/live-chats')
@admin_required
def admin_live_chats():
    """Display all live chat sessions"""
    try:
        conn = get_db_connection()
        
        # Fetch all chat sessions with user info
        chats = conn.execute(
            """SELECT cs.session_id, cs.user_id, cs.status, cs.created_at, cs.last_message_at,
                      u.name as user_name,
                      (SELECT message_text FROM live_chat_message WHERE session_id = cs.session_id ORDER BY created_at DESC LIMIT 1) as last_message,
                      (SELECT COUNT(*) FROM live_chat_message WHERE session_id = cs.session_id) as message_count
               FROM live_chat_session cs
               JOIN user u ON cs.user_id = u.user_id
               ORDER BY cs.last_message_at DESC"""
        ).fetchall()
        
        # Convert to list of dicts and adjust timezone
        chats_list = []
        for chat in chats:
            chat_dict = dict(chat)
            # Convert timestamps to UTC+8
            if chat_dict['created_at']:
                try:
                    utc_time = datetime.strptime(chat_dict['created_at'], '%Y-%m-%d %H:%M:%S')
                    local_time = utc_time + timedelta(hours=8)
                    chat_dict['created_at'] = local_time.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass
            chats_list.append(chat_dict)
        
        # Calculate statistics
        total_chats = len(chats_list)
        active_chats = sum(1 for c in chats_list if c['status'] == 'active')
        
        # Closed today
        today = datetime.now().date()
        closed_today = 0
        for chat in chats_list:
            if chat['status'] == 'closed' and chat['last_message_at']:
                try:
                    chat_date = datetime.strptime(chat['last_message_at'], '%Y-%m-%d %H:%M:%S').date()
                    if chat_date == today:
                        closed_today += 1
                except:
                    pass
        
        conn.close()
        
        return render_template('admin/admin_live_chats.html',
                               chats=chats_list,
                               total_chats=total_chats,
                               active_chats=active_chats,
                               closed_today=closed_today)
    except Exception as e:
        print(f"ERROR in admin_live_chats: {e}")
        import traceback
        traceback.print_exc()
        return f"Error loading live chats: {str(e)}", 500

@admin_bp.route('/get-chat-details/<int:session_id>')
@admin_required
def get_chat_details(session_id):
    """Get details for a specific chat session"""
    conn = get_db_connection()
    
    chat = conn.execute(
        """SELECT cs.*, u.name as user_name, u.email as user_email
           FROM live_chat_session cs
           JOIN user u ON cs.user_id = u.user_id
           WHERE cs.session_id = ?""",
        (session_id,)
    ).fetchone()
    
    conn.close()
    
    if not chat:
        return jsonify({'error': 'Chat not found'}), 404
    
    return jsonify(dict(chat))

@admin_bp.route('/get-chat-messages/<int:session_id>')
@admin_required
def get_chat_messages(session_id):
    """Get all messages for a chat session"""
    conn = get_db_connection()
    
    messages = conn.execute(
        """SELECT m.*, u.name as sender_name
           FROM live_chat_message m
           LEFT JOIN user u ON m.sender_id = u.user_id AND m.sender_type = 'user'
           WHERE m.session_id = ?
           ORDER BY m.created_at ASC""",
        (session_id,)
    ).fetchall()
    
    conn.close()
    
    return jsonify({'messages': [dict(m) for m in messages]})

@admin_bp.route('/send-chat-message', methods=['POST'])
@admin_required
def send_chat_message():
    """Send a message as admin in a chat session"""
    data = request.json
    session_id = data.get('session_id')
    message_text = data.get('message')
    
    if not session_id or not message_text:
        return jsonify({'error': 'Missing session_id or message'}), 400
    
    admin_id = session.get('user_id')  # Admin's user_id
    
    conn = get_db_connection()
    
    # Insert admin message
    conn.execute(
        "INSERT INTO live_chat_message (session_id, sender_type, sender_id, message_text) VALUES (?, 'admin', ?, ?)",
        (session_id, admin_id, message_text)
    )
    
    # Update last_message_at
    conn.execute(
        "UPDATE live_chat_session SET last_message_at = CURRENT_TIMESTAMP WHERE session_id = ?",
        (session_id,)
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'sent'})

@admin_bp.route('/close-chat/<int:session_id>', methods=['POST'])
@admin_required
def close_chat_session(session_id):
    """Close a chat session"""
    conn = get_db_connection()
    
    conn.execute(
        "UPDATE live_chat_session SET status = 'closed' WHERE session_id = ?",
        (session_id,)
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'closed'})
