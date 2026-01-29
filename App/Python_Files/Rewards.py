from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from app.db import get_db_connection
from datetime import datetime

rewards_bp = Blueprint('rewards', __name__)

@rewards_bp.route('/rewards')
def rewards():
    """Route to Rewards Page with user data."""
    if 'user_id' not in session:
        flash("Please log in to access rewards.", "warning")
        return redirect(url_for('home.login_page'))
        
    user_id = session.get('user_id')
    role = session.get('user_role')
    
    if role == 'admin':
        return redirect(url_for('admin.admin_manage_rewards'))
    
    conn = get_db_connection()
    
    # Fetch User Data
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
    
    # Fetch User's Claimed/Redeemed Rewards (already dismissed)
    # Status 'redeemed' means user has claimed and dismissed the reward
    claimed_rewards = conn.execute("""
        SELECT rr.redemption_id, r.name, 'Vendor' as vendor
        FROM reward_redemption rr
        JOIN reward r ON rr.reward_id = r.reward_id
        WHERE rr.user_id = ? AND rr.status IN ('redeemed', 'cancelled')
    """, (user_id,)).fetchall()
    
    claimed_ids = {row['redemption_id'] for row in claimed_rewards}
    
    # Fetch User's Approved Rewards (not yet claimed/dismissed)
    user_rewards_query = """
        SELECT rr.redemption_id, r.name, 'Vendor' as vendor
        FROM reward_redemption rr
        JOIN reward r ON rr.reward_id = r.reward_id
        WHERE rr.user_id = ? AND rr.status = 'approved'
    """
    user_rewards_rows = conn.execute(user_rewards_query, (user_id,)).fetchall()
    
    # Filter out already claimed rewards
    user_rewards_list = [dict(row) for row in user_rewards_rows if row['redemption_id'] not in claimed_ids]
    
    conn.close()
    
    # Calculate age from birth_date
    age = None
    if user and user['birth_date']:
        try:
            birth_date = datetime.strptime(user['birth_date'], '%Y-%m-%d')
            age = datetime.now().year - birth_date.year
        except:
            age = None
    
    user_dict = dict(user) if user else {}
    user_data = {
        'name': user_dict.get('name', 'User'),
        'age': age,
        'points': user_dict.get('total_points', 0),
        'role': role,
        'skills': [row['name'] for row in skills_rows],
        'interests': [row['name'] for row in interests_rows]
    }
    
    # Fetch all active rewards for Redeem Rewards tab
    conn = get_db_connection()
    all_rewards_query = """
        SELECT reward_id, name, description, points_required, total_quantity
        FROM reward 
        WHERE is_active = 1
        ORDER BY points_required ASC
    """
    all_rewards_rows = conn.execute(all_rewards_query).fetchall()
    all_rewards_list = [dict(row) for row in all_rewards_rows]
    conn.close()
    
    if role == 'senior':
        return render_template('senior/senior_rewards.html', 
                             user=user_data, 
                             user_rewards=user_rewards_list,
                             rewards=all_rewards_list)
    else:
        return render_template('youth/youth_rewards.html', 
                             user=user_data, 
                             user_rewards=user_rewards_list,
                             rewards=all_rewards_list)

@rewards_bp.route('/dismiss_reward', methods=['POST'])
def dismiss_reward():
    """Mark reward as claimed/dismissed (redeemed status)."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    user_id = session.get('user_id')
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    redemption_id = data.get('redemption_id')
    
    if not redemption_id:
        return jsonify({'success': False, 'error': 'Missing redemption_id'}), 400
    
    conn = get_db_connection()
    
    # Verify this redemption belongs to the user
    redemption = conn.execute("""
        SELECT user_id FROM reward_redemption 
        WHERE redemption_id = ?
    """, (redemption_id,)).fetchone()
    
    if not redemption or redemption['user_id'] != user_id:
        conn.close()
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    # Update status to 'redeemed' (meaning user has claimed it)
    conn.execute("""
        UPDATE reward_redemption 
        SET status = 'redeemed' 
        WHERE redemption_id = ? AND user_id = ?
    """, (redemption_id, user_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})


@rewards_bp.route('/redeem_reward', methods=['POST'])
def redeem_reward():
    """Handle reward redemption request."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    user_id = session.get('user_id')
    data = request.get_json()
    
    reward_name = data.get('reward_name')
    reward_vendor = data.get('reward_vendor')  
    points_required = data.get('points_required')
    
    if not reward_name or not points_required:
        return jsonify({'success': False, 'error': 'Missing reward data'}), 400
    
    conn = get_db_connection()
    
    # Get user's current points
    user = conn.execute("SELECT total_points FROM user WHERE user_id = ?", (user_id,)).fetchone()
    if not user:
        conn.close()
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    user_points = user['total_points']
    
    # Check if user has enough points
    if user_points < points_required:
        conn.close()
        return jsonify({'success': False, 'error': 'Insufficient points'}), 400
    
    # Get reward_id
    reward = conn.execute("SELECT reward_id FROM reward WHERE name = ?", (reward_name,)).fetchone()
    if not reward:
        conn.close()
        return jsonify({'success': False, 'error': 'Reward not found'}), 404
    
    # Create redemption request (status='requested')
    conn.execute("""
        INSERT INTO reward_redemption (user_id, reward_id, status)
        VALUES (?, ?, 'requested')
    """, (user_id, reward['reward_id']))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Redemption request submitted'})
