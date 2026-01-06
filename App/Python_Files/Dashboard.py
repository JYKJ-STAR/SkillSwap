from flask import Blueprint, render_template, session, redirect, url_for, flash

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    # Helper to clean session access
    if 'user_id' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('home.login_page'))

    role = session.get('user_role')
    user_id = session.get('user_id')
    
    # In a real app, fetch these from DB. For now, we mock/construct them or fetch basic info.
    # Since the templates expect specific fields (events_completed, total_hours, etc.) which might not be in DB yet,
    # we will verify if we can fetch them or defaults.
    
    # Mock/Default User Object to satisfy template
    user_data = {
        'name': session.get('user_name', 'User'),
        'points': 50, # Default or fetch from DB
        'events_completed': 12,
        'total_hours': 45,
        'impact_score': 98
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
        return render_template('Senior_dashboard.html', user=user_data, upcoming_events=upcoming_events)
    elif role == 'youth':
        return render_template('Youth_dashboard.html', user=user_data, upcoming_events=upcoming_events)
    else:
        # Fallback
        return render_template('Senior_dashboard.html', user=user_data, upcoming_events=upcoming_events)

