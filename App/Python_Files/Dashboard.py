from flask import Blueprint, render_template, session, redirect, url_for, flash
from app.db import get_db_connection

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    """
    Main User Dashboard.
    
    Displays:
    - User stats (Points, Hours, Impact).
    - Upcoming events (next 5).
    - Unread notifications.
    
    Directs to specific role-based template (Senior vs Youth).
    """
    # Helper to clean session access
    if 'user_id' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('home.login_page'))

    role = session.get('user_role')
    user_id = session.get('user_id')
    
    # Verify user exists in DB to prevent stale sessions
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM user WHERE user_id = ?", (user_id,)).fetchone()
    if not user:
        conn.close()
        session.clear()
        flash("Session expired. Please log in again.", "warning")
        return redirect(url_for('home.login_page'))
    
    # Mock/Default User Object to satisfy template (Merge DB data with mocks if needed)
    # Using real name from DB
    user_data = {
        'name': user['name'],
        'points': user['total_points'],
        'events_completed': 12, # Still mock for now
        'total_hours': 45,      # Still mock for now
        'impact_score': 98,      # Still mock for now
        'profile_photo': user['profile_photo']
    }

    # Get user's real upcoming events from event_booking table
    upcoming_events_raw = conn.execute('''
        SELECT 
            e.event_id,
            e.title,
            e.start_datetime,
            e.location,
            e.category,
            eb.role_type,
            eb.status
        FROM event_booking eb
        JOIN event e ON eb.event_id = e.event_id
        WHERE eb.user_id = ? 
          AND eb.status = 'booked'
          AND e.status NOT IN ('voided', 'cancelled')
          AND datetime(e.start_datetime) > datetime('now')
        ORDER BY e.start_datetime ASC
        LIMIT 5
    ''', (user_id,)).fetchall()
    
    # Format events for template
    upcoming_events = []
    for event in upcoming_events_raw:
        # Parse datetime
        datetime_str = event['start_datetime']
        date_part = datetime_str.split(' ')[0] if ' ' in datetime_str else datetime_str
        time_part = datetime_str.split(' ')[1][:5] if ' ' in datetime_str else ''
        
        upcoming_events.append({
            'id': event['event_id'],
            'title': event['title'],
            'date': date_part,
            'time': time_part,
            'location': event['location'],
            'category': event['category'],
            'role': event['role_type']  # 'teacher' or 'participant'
        })
    
    
    notifications_rows = conn.execute('''
        SELECT notification_id, message, created_at, event_id, challenge_id 
        FROM notification 
        WHERE user_id = ? AND is_read = 0 
        ORDER BY created_at DESC
    ''', (user_id,)).fetchall()

    notifications = [dict(row) for row in notifications_rows]
    
    conn.close()

    if role == 'admin':
        return redirect(url_for('admin.admin_dashboard'))
    elif role == 'senior':
        return render_template('senior/senior_dashboard.html', 
                             user=user_data, 
                             upcoming_events=upcoming_events,
                             notifications=notifications)
    elif role == 'youth':
        return render_template('youth/youth_dashboard.html', 
                             user=user_data, 
                             upcoming_events=upcoming_events,
                             notifications=notifications)
    else:
        # Fallback
        return render_template('senior/senior_dashboard.html', 
                             user=user_data, 
                             upcoming_events=upcoming_events,
                             notifications=notifications)


@dashboard_bp.route('/notification/<int:notification_id>/dismiss', methods=['POST'])
def dismiss_notification(notification_id):
    """
    API Endpoint: Dismiss a notification.
    Marks the notification as read via AJAX.
    """
    if 'user_id' not in session:
        return {'status': 'error', 'message': 'Unauthorized'}, 401
    
    user_id = session.get('user_id')
    conn = get_db_connection()
    # Ensure user owns this notification
    conn.execute("UPDATE notification SET is_read = 1 WHERE notification_id = ? AND user_id = ?", 
                 (notification_id, user_id))
    conn.commit()
    conn.close()
    return {'status': 'success'}


@dashboard_bp.route('/notification/<int:notification_id>/view')
def view_notification_details(notification_id):
    """
    Handle notification click.
    Marks as read and redirects to relevant page (e.g., Event Details or Challenge Details).
    """
    if 'user_id' not in session:
        flash("Please log in.", "warning")
        return redirect(url_for('home.login_page'))
    
    user_id = session.get('user_id')
    conn = get_db_connection()
    
    # Get notification details
    note = conn.execute("SELECT event_id, challenge_id FROM notification WHERE notification_id = ? AND user_id = ?", 
                       (notification_id, user_id)).fetchone()
    
    if note:
        # Mark as read
        conn.execute("UPDATE notification SET is_read = 1 WHERE notification_id = ?", (notification_id,))
        conn.commit()
        
        # Check challenge_id first (use bracket notation for Row objects)
        challenge_id = note['challenge_id'] if note['challenge_id'] else None
        event_id = note['event_id'] if note['event_id'] else None
        
        if challenge_id:
            conn.close()
            return redirect(url_for('dashboard.challenge_notification_details', challenge_id=challenge_id))
        
        if event_id:
            conn.close()
            return redirect(url_for('dashboard.event_notification_details', event_id=event_id))
            
    conn.close()
    
    # Default fallback if no event_id/challenge_id or not found
    return redirect(url_for('dashboard.dashboard'))

@dashboard_bp.route('/challenge-details/<int:challenge_id>')
def challenge_notification_details(challenge_id):
    """Display challenge details for voided or ended challenges."""
    if 'user_id' not in session:
        flash("Please log in.", "warning")
        return redirect(url_for('home.login_page'))
    
    user_role = session.get('user_role')
    conn = get_db_connection()
    
    # Get challenge details
    challenge = conn.execute(
        "SELECT * FROM challenge WHERE challenge_id = ?",
        (challenge_id,)
    ).fetchone()
    
    conn.close()
    
    if not challenge:
        flash("Challenge not found.", "error")
        return redirect(url_for('dashboard.dashboard'))
    
    # Prepare challenge data (use bracket notation for Row objects)
    challenge_data = {
        'title': challenge['title'],
        'description': challenge['description'],
        'status': challenge['status'],
        'void_reason': challenge['void_reason'] if challenge['void_reason'] else None,
        'start_date': challenge['start_date'],
        'end_date': challenge['end_date']
    }
    
    return render_template('shared/challenge_details.html', 
                         challenge=challenge_data,
                         user_role=user_role)

@dashboard_bp.route('/event-details/<int:event_id>')
def event_notification_details(event_id):
    """Display event details for voided or ended events."""
    if 'user_id' not in session:
        flash("Please log in.", "warning")
        return redirect(url_for('home.login_page'))
    
    user_role = session.get('user_role')
    conn = get_db_connection()
    
    # Get event details
    event = conn.execute(
        "SELECT * FROM event WHERE event_id = ?",
        (event_id,)
    ).fetchone()
    
    conn.close()
    
    if not event:
        flash("Event not found.", "error")
        return redirect(url_for('dashboard.dashboard'))
    
    # Prepare event data
    event_data = {
        'title': event['title'],
        'description': event['description'],
        'status': event['status'],
        'void_reason': event['void_reason'] if event['void_reason'] else None,
        'location': event['location'],
        'start_datetime': event['start_datetime']
    }
    
    return render_template('shared/event_notification_details.html', 
                         event=event_data,
                         user_role=user_role)
