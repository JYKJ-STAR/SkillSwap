from flask import Blueprint, render_template, session, redirect, url_for, flash

support_bp = Blueprint('support', __name__)

@support_bp.route('/support')
def support():
    """Route to Support Center."""
    if 'user_id' not in session:
        flash("Please log in to access support.", "warning")
        return redirect(url_for('home.login_page'))
        
    role = session.get('user_role')
    
    if role == 'admin':
        return redirect(url_for('admin.admin_dashboard'))
    elif role == 'senior':
        return render_template('senior/senior_support.html')
    elif role == 'youth':
        return render_template('youth/youth_support.html')
    else:
        return render_template('youth/youth_support.html')
