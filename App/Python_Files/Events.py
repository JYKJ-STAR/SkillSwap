from flask import Blueprint, render_template, session, redirect, url_for, flash

events_bp = Blueprint('events', __name__)

@events_bp.route('/events')
def events():
    """Route to Events Page."""
    if 'user_id' not in session:
        flash("Please log in to access events.", "warning")
        return redirect(url_for('home.login_page'))
        
    role = session.get('user_role')
    
    if role == 'admin':
        return redirect(url_for('admin.admin_dashboard'))
    elif role == 'senior':
        return render_template('senior/senior_events.html')
    elif role == 'youth':
        return render_template('youth/youth_events.html')
    else:
        return render_template('youth/youth_events.html')
