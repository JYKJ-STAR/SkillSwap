from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify, current_app
from app.db import get_db_connection
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import os
import json
from datetime import datetime

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings')
def settings():
    if 'user_id' not in session:
        return redirect(url_for('home.login_page'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM user WHERE user_id = ?", (user_id,)).fetchone()
    grcs = conn.execute("SELECT * FROM grc").fetchall()
    
    # Fetch Skills
    all_skills_rows = conn.execute("SELECT name, category FROM skill").fetchall()
    all_skills = [row['name'] for row in all_skills_rows]
    
    user_teach_rows = conn.execute("""
        SELECT s.name FROM skill s 
        JOIN user_skill_offered uso ON s.skill_id = uso.skill_id 
        WHERE uso.user_id = ?
    """, (user_id,)).fetchall()
    teach_skills = [row['name'] for row in user_teach_rows]
    
    user_learn_rows = conn.execute("""
        SELECT s.name FROM skill s 
        JOIN user_skill_interest usi ON s.skill_id = usi.skill_id 
        WHERE usi.user_id = ?
    """, (user_id,)).fetchall()
    learn_skills = [row['name'] for row in user_learn_rows]
    
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
    
    # Calculate Age from BirthDate
    birth_date_str = user['birth_date']
    age_display = 'N/A'
    if birth_date_str:
        try:
             # Handle YYYY-MM-DD
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d')
            today = datetime.today()
            age_display = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        except:
             age_display = 'N/A'

    # Prepare User Data for Template
    user_data = {
        'first_name': first_name,
        'last_name': last_name,
        'email': user['email'],
        'birth_date': user['birth_date'],
        'age': age_display, # For header
        'role': user['role'],
        'language': user['language_pref'],
        'profession': user['profession'] or '',
        'bio': user['bio'] or '',
        'verification_status': user['verification_status'],
        'profile_photo': user['profile_photo'],
        'grc_id': user['grc_id'],
        'is_google_user': (user['password_hash'] == 'google_oauth')
    }
    
    return render_template('shared/settings.html', 
                           user=user_data, 
                           grcs=grcs, 
                           all_skills=all_skills, 
                           teach_skills=teach_skills, 
                           learn_skills=learn_skills)


@settings_bp.route('/settings/update', methods=['POST'])
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
        birth_date = request.form.get('birth_date')

        try:
            grc_id = int(request.form.get('grc_id')) if request.form.get('grc_id') else None
        except ValueError:
            grc_id = None
        
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
                SET name = ?, language_pref = ?, profession = ?, bio = ?, profile_photo = ?, grc_id = ?, birth_date = ?
                WHERE user_id = ?
            """, (name, language, profession, bio, profile_photo, grc_id, birth_date, user_id))
        else:
             cur.execute("""
                UPDATE user 
                SET name = ?, language_pref = ?, profession = ?, bio = ?, grc_id = ?, birth_date = ?
                WHERE user_id = ?
            """, (name, language, profession, bio, grc_id, birth_date, user_id))
            
        conn.commit()
        conn.close()
        
        # Update Session Name if changed
        session['user_name'] = name
        
        return jsonify({'success': True, 'message': 'Profile updated successfully', 'new_photo': profile_photo})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@settings_bp.route('/settings/update_password', methods=['POST'])
def update_password():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        user_id = session['user_id']
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        if not current_password or not new_password:
             return jsonify({'success': False, 'message': 'Missing fields'}), 400
             
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get current hash
        user = cur.execute("SELECT password_hash FROM user WHERE user_id = ?", (user_id,)).fetchone()
        
        if not user:
            conn.close()
            return jsonify({'success': False, 'message': 'User not found'}), 404
            
        stored_hash = user['password_hash']

        if stored_hash == 'google_oauth':
             conn.close()
             return jsonify({'success': False, 'message': 'Google users cannot change password.'}), 403
        
        # Use simple string check for demo if hash is 'demo_hash', else real verify
        if stored_hash == 'demo_hash':
             # For demo, if stored is demo_hash, accept anything? Or enforce rules? 
             # Let's say if stored is demo_hash, we check if current_pw is 'demo_hash'??
             # Uh oh, if user logs in with 'demo_hash' (which acts as password), then they must type 'demo_hash' 
             # as current password.
             pass_valid = (current_password == 'demo_hash')
        else:
             pass_valid = check_password_hash(stored_hash, current_password)
             
        if not pass_valid:
            conn.close()
            return jsonify({'success': False, 'message': 'Incorrect current password'}), 400
            
        # Update Password
        new_hash = generate_password_hash(new_password)
        cur.execute("UPDATE user SET password_hash = ? WHERE user_id = ?", (new_hash, user_id))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Password updated successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@settings_bp.route('/settings/update_skills', methods=['POST'])
def update_skills():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        user_id = session['user_id']
        data = request.get_json()
        teach_skills = data.get('teach_skills', [])
        learn_skills = data.get('learn_skills', [])
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Helper to get or create skill ID
        def get_or_create_skill_id(skill_name):
            # Check exist
            row = cur.execute("SELECT skill_id FROM skill WHERE name = ? COLLATE NOCASE", (skill_name,)).fetchone()
            if row:
                return row['skill_id']
            else:
                # Create new skill (default category 'General' or derived?)
                # We'll just set a default category for now
                cur.execute("INSERT INTO skill (name, category) VALUES (?, ?)", (skill_name, 'General'))
                return cur.lastrowid

        # 1. Update Teach Skills
        # First, remove all existing for this user (simplest way to sync)
        cur.execute("DELETE FROM user_skill_offered WHERE user_id = ?", (user_id,))
        
        for skill_name in teach_skills:
            if not skill_name.strip(): continue
            sid = get_or_create_skill_id(skill_name.strip())
            # Insert if not duplicate (though we cleared, but input list might have dupes)
            try:
                cur.execute("INSERT OR IGNORE INTO user_skill_offered (user_id, skill_id) VALUES (?, ?)", (user_id, sid))
            except:
                pass

        # 2. Update Learn Skills
        cur.execute("DELETE FROM user_skill_interest WHERE user_id = ?", (user_id,))
        
        for skill_name in learn_skills:
            if not skill_name.strip(): continue
            sid = get_or_create_skill_id(skill_name.strip())
            try:
                cur.execute("INSERT OR IGNORE INTO user_skill_interest (user_id, skill_id) VALUES (?, ?)", (user_id, sid))
            except:
                pass
                
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Skills updated successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
