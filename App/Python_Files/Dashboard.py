from flask import Blueprint, render_template, session, redirect, url_for, flash, request
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

    # Fetch Active/Published Challenges with Progress
    challenges_raw = conn.execute('''
        SELECT 
            c.challenge_id,
            c.title,
            c.description,
            c.start_date,
            c.end_date,
            c.bonus_points,
            c.target_count,
            c.status,
            (SELECT COUNT(*) 
             FROM user_challenge uc
             WHERE uc.user_id = ? 
               AND uc.challenge_id = c.challenge_id
               AND uc.status = 'approved'
            ) as progress_count
        FROM challenge c
        WHERE c.status IN ('active', 'published')
        ORDER BY c.end_date ASC
    ''', (user_id,)).fetchall()

    challenges = []
    from datetime import datetime
    for c in challenges_raw:
        # Calculate days left
        try:
            end_date = datetime.strptime(c['end_date'], '%Y-%m-%d')
            days_left = (end_date - datetime.now()).days
            if days_left < 0:
                time_str = "Ended"
            else:
                time_str = f"Ends in {days_left} days"
        except:
            time_str = c['end_date']

        challenges.append({
            'id': c['challenge_id'],
            'title': c['title'],
            'description': c['description'],
            'bonus_points': c['bonus_points'],
            'target_count': c['target_count'] or 1,
            'progress': c['progress_count'],
            'time_left': time_str,
            'status': 'Completed' if c['progress_count'] >= (c['target_count'] or 1) else 'In Progress'
        })
    
    conn.close()

    if role == 'admin':
        return redirect(url_for('admin.admin_dashboard'))
    elif role == 'senior':
        return render_template('senior/senior_dashboard.html', 
                             user=user_data, 
                             upcoming_events=upcoming_events,
                             notifications=notifications,
                             challenges=challenges)
    elif role == 'youth':
        return render_template('youth/youth_dashboard.html', 
                             user=user_data, 
                             upcoming_events=upcoming_events,
                             notifications=notifications,
                             challenges=challenges)
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

@dashboard_bp.route('/challenge/<int:challenge_id>', methods=['GET', 'POST'])
def challenge_details(challenge_id):
    """Display full challenge details with proof submission."""
    if 'user_id' not in session:
        flash("Please log in.", "warning")
        return redirect(url_for('home.login_page'))
    
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    conn = get_db_connection()
    
    # Get challenge details
    challenge = conn.execute(
        "SELECT * FROM challenge WHERE challenge_id = ?",
        (challenge_id,)
    ).fetchone()
    
    if not challenge:
        conn.close()
        flash("Challenge not found.", "error")
        return redirect(url_for('dashboard.dashboard'))

    # Check for existing submissions
    submission = conn.execute(
        """SELECT * FROM user_challenge 
           WHERE user_id = ? AND challenge_id = ? 
           ORDER BY created_at DESC 
           LIMIT 1""",
        (user_id, challenge_id)
    ).fetchone()

    # Check if challenge is voided or ended explicitly - if so, show cancellation/ended page
    if challenge['status'] in ['voided', 'ended']:
        conn.close()
        return render_template('shared/challenge_cancelled.html', challenge=challenge, user_role=user_role)

    # REDIRECT LOGIC: If the MOST RECENT submission is rejected and not retrying, go to feedback page
    if submission and submission['status'] == 'rejected' and not request.args.get('retry'):
        conn.close()
        return redirect(url_for('dashboard.challenge_rejection', challenge_id=challenge_id))

    # Handle Proof Submission
    if request.method == 'POST':
        description = request.form.get('proof_description')
        file = request.files.get('proof_file')
        filename = None
        
        # Save file to challenges_proof directory
        if file and file.filename:
            import os
            from werkzeug.utils import secure_filename
            from datetime import datetime
            
            # Generate unique filename
            original_filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{user_id}_{challenge_id}_{timestamp}_{original_filename}"
            
            # Ensure directory exists
            upload_folder = os.path.join('app', 'Styling', 'img', 'users', 'challenges_proof')
            os.makedirs(upload_folder, exist_ok=True)
            
            # Save file
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
        
        # Always insert a new proof submission (allow multiple proofs per challenge)
        conn.execute('''
            INSERT INTO user_challenge (user_id, challenge_id, proof_description, proof_file, status)
            VALUES (?, ?, ?, ?, 'pending')
        ''', (user_id, challenge_id, description, filename))
        
        conn.commit()
        conn.close()
        flash("Proof submitted successfully! We will review it shortly.", "success")
        return redirect(url_for('dashboard.challenge_details', challenge_id=challenge_id))
    
    # Calculate user's progress (Event based)
    user_progress = conn.execute('''
        SELECT COUNT(*) as count
        FROM event_booking eb 
        JOIN event e ON eb.event_id = e.event_id 
        WHERE eb.user_id = ? 
          AND eb.status = 'completed'
          AND e.start_datetime BETWEEN ? AND ?
    ''', (user_id, challenge['start_date'], challenge['end_date'])).fetchone()['count']
    
    # Determine challenge status
    from datetime import datetime
    try:
        # Try parsing with time first, then fallback to just date
        try:
            start_date = datetime.strptime(challenge['start_date'], '%Y-%m-%d %H:%M')
            end_date = datetime.strptime(challenge['end_date'], '%Y-%m-%d %H:%M')
        except ValueError:
            try:
                start_date = datetime.strptime(challenge['start_date'], '%Y-%m-%d')
                end_date = datetime.strptime(challenge['end_date'], '%Y-%m-%d')
            except ValueError:
                 # Try with seconds if present
                start_date = datetime.strptime(challenge['start_date'], '%Y-%m-%d %H:%M:%S')
                end_date = datetime.strptime(challenge['end_date'], '%Y-%m-%d %H:%M:%S')

        now = datetime.now()
        
        if now < start_date:
            status = 'Not Yet Started'
            days_until = (start_date - now).days
            if days_until == 0:
                 hours_until = int((start_date - now).seconds / 3600)
                 time_left = f"Starts in {hours_until} hours"
            else:
                 time_left = f"Starts in {days_until} days"
        elif now > end_date:
            status = 'Ended'
            time_left = "Challenge has ended"
        else:
            status = 'Active'
            days_left = (end_date - now).days
            if days_left == 0:
                 hours_left = int((end_date - now).seconds / 3600)
                 time_left = f"{hours_left} hours remaining"
            else:
                 time_left = f"{days_left} days remaining"
    except Exception as e:
        print(f"Date parsing error: {e}")
        status = 'Active'
        time_left = challenge['end_date']
    
    # Check if challenge has Ended - if so, show ended page (reusing cancelled template)
    if status == 'Ended':
        # Create a dict copy to effectively modify status for the template
        challenge_view = dict(challenge)
        challenge_view['status'] = 'Ended'
        conn.close()
        return render_template('shared/challenge_cancelled.html', challenge=challenge_view, user_role=user_role)
    is_new = False
    if challenge['published_at']:
        try:
            published_date = datetime.fromisoformat(challenge['published_at'].replace(' ', 'T'))
            days_since_published = (datetime.now() - published_date).days
            is_new = days_since_published <= 7
        except:
            pass
    
    
    # Prepare challenge data
    # Calculate user's progress based on approved proofs for THIS challenge
    approved_proofs_count = conn.execute('''
        SELECT COUNT(*) as count
        FROM user_challenge
        WHERE user_id = ? AND challenge_id = ? AND status = 'approved'
    ''', (user_id, challenge_id)).fetchone()['count']
    
    # Check if there's a pending submission
    pending_submission = conn.execute('''
        SELECT * FROM user_challenge
        WHERE user_id = ? AND challenge_id = ? AND status = 'pending'
        ORDER BY created_at DESC
        LIMIT 1
    ''', (user_id, challenge_id)).fetchone()
    
    conn.close()
    
    challenge_data = {
        'id': challenge['challenge_id'],
        'title': challenge['title'],
        'description': challenge['description'],
        'status': status,
        'start_date': challenge['start_date'],
        'end_date': challenge['end_date'],
        'bonus_points': challenge['bonus_points'] or 0,
        'target_count': challenge['target_count'] or 1,
        'user_progress': approved_proofs_count,  # Progress is now based on approved proofs
        'time_left': time_left,
        'is_new': is_new
    }
    
    return render_template('shared/challenge_details.html', 
                         challenge=challenge_data,
                         user_role=user_role,
                         submission=pending_submission)  # Show pending submission if exists

@dashboard_bp.route('/challenge/<int:challenge_id>/feedback')
def challenge_rejection(challenge_id):
    """Display rejection feedback for a challenge submission."""
    if 'user_id' not in session:
        return redirect(url_for('home.login_page'))
    
    user_id = session.get('user_id')
    conn = get_db_connection()
    
    challenge = conn.execute("SELECT * FROM challenge WHERE challenge_id = ?", (challenge_id,)).fetchone()
    # Get the most recent rejected submission
    submission = conn.execute("""
        SELECT * FROM user_challenge 
        WHERE user_id = ? AND challenge_id = ? AND status = 'rejected'
        ORDER BY created_at DESC
        LIMIT 1
    """, (user_id, challenge_id)).fetchone()
    
    conn.close()
    
    # If no rejected submission, redirect back to details
    if not submission:
        return redirect(url_for('dashboard.challenge_details', challenge_id=challenge_id))
    
    return render_template('shared/challenge_rejection.html', challenge=challenge, submission=submission)

@dashboard_bp.route('/challenge-details/<int:challenge_id>')
def challenge_notification_details(challenge_id):
    """Legacy route for voided/ended challenge notifications - redirects to main details."""
    return redirect(url_for('dashboard.challenge_details', challenge_id=challenge_id))

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
