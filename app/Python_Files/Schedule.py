from flask import Blueprint, render_template, session, redirect, url_for, flash
from app.db import get_db_connection

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
    
    user_data = {
        'name': user_dict['name'],
        'age': user_dict.get('age', 26), # Default if not in DB
        'points': user_dict['total_points'],
        'role': role,
        'skills': [row['name'] for row in skills_rows],
        'interests': [row['name'] for row in interests_rows]
    }

    
    # Fetch User's Booked Events
    conn = get_db_connection()
    events_query = """
        SELECT 
            e.event_id, e.title, e.start_datetime, e.end_datetime, e.category, e.location,
            eb.role_type, eb.status, eb.hours_earned,
            (e.base_points_participant) as points -- Simplified points logic for now
        FROM event_booking eb
        JOIN event e ON eb.event_id = e.event_id
        WHERE eb.user_id = ?
        ORDER BY e.start_datetime ASC
    """
    events_rows = conn.execute(events_query, (user_id,)).fetchall()
    conn.close()

    upcoming_events = []
    completed_events = []

    from datetime import datetime

    for row in events_rows:
        # Convert row to dict
        evt = dict(row)
        
        # Parse datetime for display
        try:
            dt_obj = datetime.strptime(evt['start_datetime'], '%Y-%m-%d %H:%M:%S')
            evt['display_date'] = dt_obj.strftime('%d - %m - %Y')
            evt['display_time'] = dt_obj.strftime('%H%M')
        except ValueError:
            evt['display_date'] = evt['start_datetime']
            evt['display_time'] = ''

        # Categorize
        if evt['status'] == 'booked':
            upcoming_events.append(evt)
        elif evt['status'] == 'completed':
            completed_events.append(evt)
        # Handle other statuses if needed (e.g., cancelled)

    if role == 'youth':
        return render_template('youth/youth_schedule.html', 
                             user=user_data, 
                             upcoming_events=upcoming_events, 
                             completed_events=completed_events)
    else:
        # Fallback for seniors/others to their version or same page if shared
        return render_template('senior/senior_schedule.html', 
                             user=user_data,
                             upcoming_events=upcoming_events, 
                             completed_events=completed_events)
