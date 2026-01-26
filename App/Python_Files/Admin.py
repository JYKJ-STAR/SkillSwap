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
        "SELECT admin_id, name, email, password_hash, privileged FROM admin WHERE email = ?",
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
                           user_name=session.get('user_name'),
                           admin_email=session.get('admin_email', 'Admin@123.com'),
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
    """Delete a user from the User Management page."""
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
    """Edit a user's name and email from the User Management page."""
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
    conn.execute(
        """INSERT INTO event (created_by_user_id, grc_id, title, description, start_datetime, location, category, led_by, max_capacity, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')""",
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
            (SELECT COALESCE(SUM(required_count), 0) FROM event_role_requirement err WHERE err.event_id = e.event_id) as manpower_required
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
    
    return render_template('admin/admin_manage_events.html',
                           user_name=session.get('admin_name'),
                           admin_email=session.get('admin_email', 'Admin@123.com'),
                           events=events,
                           grcs=grcs,
                           category_display=category_display,
                           current_filter=filter_status,
                           search_query=search_query)


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
    notified_count = 0
    if notify_users and participants:
        notification_message = f"The event '{event_title}' you registered for has been cancelled by the organisers."
        for participant in participants:
            conn.execute("""
                INSERT INTO notification (user_id, message, event_id, created_at) 
                VALUES (?, ?, ?, datetime('now'))
            """, (participant['user_id'], notification_message, event_id))
            notified_count += 1
    
    conn.commit()
    conn.close()
    
    # If this was a published event with participants and notifications were sent, show confirmation page
    if was_published and participants and notify_users:
        # Store participant info in session for confirmation page
        session['cancelled_event'] = {
            'event_id': event_id,
            'event_title': event_title,
            'void_reason': void_reason,
            'participants': [{'name': p['name'], 'role': p['role']} for p in participants]
        }
        return redirect(url_for('admin.event_cancellation_confirm'))
    
    # Show appropriate message based on notification status
    if notified_count > 0:
        flash(f"Event removed successfully. All {notified_count} registered participants have been notified.", "success")
    else:
        flash("Event removed successfully.", "success")
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
    conn.execute("UPDATE event SET status = 'ended' WHERE event_id = ?", (event_id,))
    conn.commit()
    conn.close()
    
    flash("Event ended and moved to Past.", "success")
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
                           user_name=session.get('admin_name'),
                           admin_email=session.get('admin_email', 'Admin@123.com'),
                           all_users=all_users)


@admin_bp.route('/verify-user/<int:user_id>', methods=['POST'])
@admin_required
def verify_user(user_id):
    """Approve a user's verification from User Management page."""
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
    """Reject a user's verification - delete their verification photo."""
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

