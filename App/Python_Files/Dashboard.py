from flask import Blueprint, render_template, session, redirect, url_for, flash
from app.db import get_db_connection

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    # Helper to clean session access
    if 'user_id' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('home.login_page'))

    role = session.get('user_role')
    user_id = session.get('user_id')
    
    # Verify user exists in DB to prevent stale sessions
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM user WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()

    if not user:
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
        'impact_score': 98      # Still mock for now
    }

    # Mock Upcoming Events
    upcoming_events = [
        {
            'name': 'Digital Literacy Workshop',
            'date': '2024-03-15',
            'time': '10:00 AM',
            'location': 'Community Center',
            'description': 'Learn the basics of smartphones and tablets.',
            'points': 20,
            'category': 'Technology'
        }
    ]

    if role == 'admin':
        return redirect(url_for('admin.admin_dashboard'))
    elif role == 'senior':
        return render_template('senior/senior_dashboard.html', user=user_data, upcoming_events=upcoming_events)
    elif role == 'youth':
        return render_template('youth/youth_dashboard.html', user=user_data, upcoming_events=upcoming_events)
    else:
        # Fallback
        return render_template('senior/senior_dashboard.html', user=user_data, upcoming_events=upcoming_events)

@dashboard_bp.route('/activities')
def activities():
    if 'user_id' not in session:
         return redirect(url_for('home.login_page'))
    # Only youth has this for now?
    return render_template('youth/youth_activities.html')



