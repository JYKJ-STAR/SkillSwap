from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify, current_app
from app.db import get_db_connection
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime

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


@dashboard_bp.route('/settings')
def settings():
    if 'user_id' not in session:
        return redirect(url_for('home.login_page'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM user WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    
    if not user:
        session.clear()
        flash("User not found. Please log in again.", "error")
        return redirect(url_for('home.login_page'))
    
    # Process Name
    full_name = user['name'] or ''
    parts = full_name.split(' ', 1)
    first_name = parts[0]
    last_name = parts[1] if len(parts) > 1 else ''
    
    # Prepare User Data for Template
    user_data = {
        'first_name': first_name,
        'last_name': last_name,
        'email': user['email'],
        'age': user['age'],
        'role': user['role'],
        'language': user['language_pref'],
        'profession': user['profession'] or '',
        'bio': user['bio'] or '',
        'verification_status': user['verification_status'],
        'profile_photo': user['profile_photo'],
    }
    
    return render_template('shared/settings.html', user=user_data)

@dashboard_bp.route('/settings/update', methods=['POST'])
def update_settings():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        user_id = session['user_id']
        # Handle FormData which might include file
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        language = request.form.get('language')
        profession = request.form.get('profession')
        bio = request.form.get('bio')
        
        name = f"{first_name} {last_name}".strip()
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Helper for file upload
        profile_photo = None
        if 'profile_photo' in request.files:
            file = request.files['profile_photo']
            if file and file.filename:
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                final_filename = f"profile_{user_id}_{timestamp}_{filename}"
                
                upload_folder = os.path.join(current_app.static_folder, 'img', 'users', 'profiles')
                os.makedirs(upload_folder, exist_ok=True)
                
                file.save(os.path.join(upload_folder, final_filename))
                profile_photo = final_filename

        # Update Query
        if profile_photo:
            cur.execute("""
                UPDATE user 
                SET name = ?, language_pref = ?, profession = ?, bio = ?, profile_photo = ?
                WHERE user_id = ?
            """, (name, language, profession, bio, profile_photo, user_id))
        else:
             cur.execute("""
                UPDATE user 
                SET name = ?, language_pref = ?, profession = ?, bio = ?
                WHERE user_id = ?
            """, (name, language, profession, bio, user_id))
            
        conn.commit()
        conn.close()
        
        # Update Session Name if changed
        session['user_name'] = name
        
        return jsonify({'success': True, 'message': 'Profile updated successfully', 'new_photo': profile_photo})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
