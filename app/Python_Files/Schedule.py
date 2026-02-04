from flask import Blueprint, render_template, session, redirect, url_for, flash, request, current_app
from app.db import get_db_connection
from datetime import datetime
import os
from werkzeug.utils import secure_filename

schedule_bp = Blueprint('schedule', __name__)

@schedule_bp.route('/schedule')
def schedule():
    if 'user_id' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('home.login_page'))
    
    user_id = session.get('user_id')
    role = session.get('user_role')

    # Fetch User Data
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM user WHERE user_id = ?", (user_id,)).fetchone()
    # Fetch User Skills (Offered)
    skills_query = """
        SELECT s.name 
        FROM skill s
        JOIN user_skill_offered uso ON s.skill_id = uso.skill_id
        WHERE uso.user_id = ?
    """
    skills_rows = conn.execute(skills_query, (user_id,)).fetchall()
    
    # Fetch User Interests
    interests_query = """
        SELECT s.name 
        FROM skill s
        JOIN user_skill_interest usi ON s.skill_id = usi.skill_id
        WHERE usi.user_id = ?
    """
    interests_rows = conn.execute(interests_query, (user_id,)).fetchall()
    
    conn.close()

    if not user:
        session.clear()
        return redirect(url_for('home.login_page'))

    # Prepare user data object (consistent with dashboard)
    # Convert sqlite3.Row to dict to use .get()
    user_dict = dict(user)
    print(f"DEBUG_KEYS: {user_dict.keys()}")
    print(f"DEBUG_PHOTO: {user_dict.get('profile_photo')}")
    
    user_data = {
        'name': user_dict['name'],
        'age': user_dict.get('age', 26), # Default if not in DB
        'points': user_dict['total_points'],
        'role': role,
        'skills': [row['name'] for row in skills_rows],
        'interests': [row['name'] for row in interests_rows],
        'profile_photo': user_dict.get('profile_photo')
    }

    
    # Fetch User's Reviews to check if feedback is given
    conn = get_db_connection()
    reviews_query = "SELECT event_id FROM review WHERE user_id = ?"
    reviews_rows = conn.execute(reviews_query, (user_id,)).fetchall()
    reviewed_event_ids = {row['event_id'] for row in reviews_rows}
    
    # Fetch User's Booked Events (exclude cancelled/withdrawn)
    events_query = """
        SELECT 
            e.event_id, e.title, e.start_datetime, e.end_datetime, e.category, e.location,
            eb.role_type, eb.status, eb.hours_earned, eb.proof_media_url,
            (e.base_points_participant) as points
        FROM event_booking eb
        JOIN event e ON eb.event_id = e.event_id
        WHERE eb.user_id = ? AND eb.status != 'cancelled'
        ORDER BY e.start_datetime ASC
    """
    events_rows = conn.execute(events_query, (user_id,)).fetchall()
    conn.close()

    upcoming_events = []
    ongoing_events = []
    action_required_events = []
    pending_review_events = []
    completed_events = []
    today = datetime.now()

    for row in events_rows:
        evt = dict(row)
        
        # Parse datetime for display and comparison
        try:
            start_dt = datetime.strptime(evt['start_datetime'], '%Y-%m-%d %H:%M:%S')
            
            # Try to parse end_datetime
            if evt['end_datetime']:
                try:
                    end_dt = datetime.strptime(evt['end_datetime'], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    end_dt = start_dt
            else:
                end_dt = start_dt

            evt['display_date'] = start_dt.strftime('%d - %m - %Y')
            evt['display_time'] = start_dt.strftime('%H%M')
            
            is_past = end_dt < today
            is_ongoing = start_dt <= today <= end_dt
            is_upcoming = start_dt > today
            
        except ValueError:
            evt['display_date'] = evt['start_datetime']
            evt['display_time'] = ''
            is_past = False
            is_ongoing = False
            is_upcoming = True

        # Check conditions
        has_proof = evt['proof_media_url'] is not None and evt['proof_media_url'] != ''
        has_feedback = evt['event_id'] in reviewed_event_ids
        is_verified = evt['status'] == 'completed'

        # Categorization Logic
        if is_upcoming:
            upcoming_events.append(evt)
        elif is_ongoing:
            ongoing_events.append(evt)
        elif is_past:
            # Past events
            if is_verified:
                # Admin verified - goes to Completed
                completed_events.append(evt)
            elif has_proof and has_feedback:
                # User did both - goes to Pending Review
                evt['status_display'] = 'Pending Review'
                pending_review_events.append(evt)
            else:
                # Missing proof OR feedback - goes to Action Required
                action_required_events.append(evt)

    if role == 'youth':
        return render_template('youth/youth_schedule.html', 
                             user=user_data, 
                             ongoing_events=ongoing_events,
                             upcoming_events=upcoming_events, 
                             action_required_events=action_required_events,
                             pending_review_events=pending_review_events,
                             completed_events=completed_events)
    else:
        return render_template('senior/senior_schedule.html', 
                             user=user_data,
                             ongoing_events=ongoing_events,
                             upcoming_events=upcoming_events, 
                             completed_events=completed_events)


@schedule_bp.route('/upload_proof', methods=['POST'])
def upload_proof():
    if 'user_id' not in session:
        return redirect(url_for('home.login_page'))
    
    user_id = session['user_id']
    event_id = request.form.get('event_id')
    photo = request.files.get('photo')
    
    if not event_id or not photo:
        flash("Missing info.", "error")
        return redirect(url_for('schedule.schedule'))
        
    filename = secure_filename(photo.filename)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    final_filename = f"{user_id}_{event_id}_{timestamp}_{filename}"
    
    # Save path: app/Styling/img/users/Upload_proof
    upload_folder = os.path.join(current_app.static_folder, 'img', 'users', 'Upload_proof')
    os.makedirs(upload_folder, exist_ok=True)
    
    photo.save(os.path.join(upload_folder, final_filename))
    
    conn = get_db_connection()
    conn.execute("UPDATE event_booking SET proof_media_url = ? WHERE user_id = ? AND event_id = ?", 
                 (final_filename, user_id, event_id))
    conn.commit()
    conn.close()
    
    flash("Proof uploaded successfully!", "success")
    return redirect(url_for('schedule.schedule'))

@schedule_bp.route('/log_reflection/<int:event_id>')
def log_reflection(event_id):
    if 'user_id' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('home.login_page'))
    
    user_id = session.get('user_id')
    role = session.get('user_role')

    # Fetch User Data
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM user WHERE user_id = ?", (user_id,)).fetchone()
    
    # Fetch User Skills
    skills_query = """
        SELECT s.name 
        FROM skill s
        JOIN user_skill_offered uso ON s.skill_id = uso.skill_id
        WHERE uso.user_id = ?
    """
    skills_rows = conn.execute(skills_query, (user_id,)).fetchall()
    
    # Fetch User Interests
    interests_query = """
        SELECT s.name 
        FROM skill s
        JOIN user_skill_interest usi ON s.skill_id = usi.skill_id
        WHERE usi.user_id = ?
    """
    interests_rows = conn.execute(interests_query, (user_id,)).fetchall()
    
    # Fetch Event Details
    event = conn.execute("""
        SELECT e.event_id, e.title, eb.role_type, e.base_points_participant as points
        FROM event e
        JOIN event_booking eb ON e.event_id = eb.event_id
        WHERE e.event_id = ? AND eb.user_id = ?
    """, (event_id, user_id)).fetchone()
    
    conn.close()

    if not user or not event:
        flash("Event not found or unauthorized access.", "error")
        return redirect(url_for('schedule.schedule'))

    user_dict = dict(user)
    user_data = {
        'name': user_dict['name'],
        'age': user_dict.get('age', 26),
        'points': user_dict['total_points'],
        'role': role,
        'skills': [row['name'] for row in skills_rows],
        'interests': [row['name'] for row in interests_rows]
    }

    return render_template('youth/youth_log_reflection.html', 
                         user=user_data, 
                         event_id=event['event_id'],
                         event_title=event['title'],
                         points=event['points'])

@schedule_bp.route('/submit_reflection', methods=['POST'])
def submit_reflection():
    if 'user_id' not in session:
        return redirect(url_for('home.login_page'))
        
    user_id = session['user_id']
    event_id = request.form.get('event_id')
    rating = request.form.get('rating')
    comment = request.form.get('comment')
    photo = request.files.get('photo')
    
    if not event_id or not rating:
        flash("Please provide a rating.", "error")
        return redirect(url_for('schedule.log_reflection', event_id=event_id))
    
    if not photo:
        flash("Please upload a photo.", "error")
        return redirect(url_for('schedule.log_reflection', event_id=event_id))
        
    conn = get_db_connection()
    
    # Check if already reviewed
    existing = conn.execute("SELECT review_id FROM review WHERE user_id = ? AND event_id = ?", (user_id, event_id)).fetchone()
    
    if not existing:
        conn.execute("INSERT INTO review (user_id, event_id, rating, comment) VALUES (?, ?, ?, ?)",
                     (user_id, event_id, rating, comment))
        conn.commit()
    else:
        flash("You have already submitted feedback for this event.", "info")
        conn.close()
        return redirect(url_for('schedule.schedule'))
    
    # Handle photo upload
    filename = secure_filename(photo.filename)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    final_filename = f"{user_id}_{event_id}_{timestamp}_{filename}"
    
    upload_folder = os.path.join(current_app.static_folder, 'img', 'users', 'Upload_proof')
    os.makedirs(upload_folder, exist_ok=True)
    
    photo.save(os.path.join(upload_folder, final_filename))
    
    conn.execute("UPDATE event_booking SET proof_media_url = ? WHERE user_id = ? AND event_id = ?", 
                 (final_filename, user_id, event_id))
    conn.commit()
    conn.close()
    
    flash("Reflection submitted successfully!", "success")
    return redirect(url_for('schedule.schedule'))
