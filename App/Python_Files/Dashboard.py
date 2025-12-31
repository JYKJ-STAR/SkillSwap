from flask import Blueprint, render_template, session, redirect, url_for, flash

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    # Simulating a user being logged in if 'user_role' is not in session
    # In a real app, this would redirect to login.
    if 'user_role' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('home.home')) # Redirect to home if not logged in

    role = session.get('user_role')
    user_name = session.get('user_name', 'User')

    if role == 'admin':
        return redirect(url_for('admin.admin_dashboard'))
    elif role == 'senior':
        return render_template('senior_dashboard.html', user_name=user_name)
    elif role == 'youth':
        return render_template('youth_dashboard.html', user_name=user_name)
    else:
        # Fallback or error
        return "Unknown role", 403

