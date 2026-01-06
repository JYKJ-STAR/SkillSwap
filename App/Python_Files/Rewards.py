from flask import Blueprint, render_template, session, redirect, url_for, flash

rewards_bp = Blueprint('rewards', __name__)

@rewards_bp.route('/rewards')
def rewards():
    """Route to Rewards Page."""
    if 'user_id' not in session:
        flash("Please log in to access rewards.", "warning")
        return redirect(url_for('home.login_page'))
        
    role = session.get('user_role')
    
    if role == 'admin':
        return redirect(url_for('admin.admin_dashboard'))
    elif role == 'senior':
        return render_template('senior/senior_rewards.html')
    elif role == 'youth':
        return render_template('youth/youth_rewards.html')
    else:
        return render_template('youth/youth_rewards.html')
