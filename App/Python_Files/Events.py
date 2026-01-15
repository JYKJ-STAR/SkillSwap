from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from app.db import get_db_connection

events_bp = Blueprint('events', __name__)

# Category display names with emojis
CATEGORY_DISPLAY = {
    'tech_digital': '🖥️ Tech & Digital Skills',
    'life_skills': '🍳 Life Skills & Home Skills',
    'health_wellness': '🧘 Health & Wellness',
    'culture_creative': '🎨 Culture, Heritage & Creative',
    'social_games': '🎲 Social & Games',
    'community_projects': '🛠️ Hands-On / Community Projects'
}

def get_all_events():
    """Fetch all open events from database."""
    db = get_db_connection()
    cursor = db.execute('''
        SELECT event_id, title, description, category, led_by, 
               start_datetime, location, status, base_points_participant
        FROM event 
        WHERE status = 'open'
        ORDER BY start_datetime ASC
    ''')
    events = cursor.fetchall()
    
    # Convert to list of dicts
    event_list = []
    for e in events:
        # Parse date and time from start_datetime
        datetime_str = e['start_datetime']
        date_part = datetime_str.split(' ')[0] if ' ' in datetime_str else datetime_str
        time_part = datetime_str.split(' ')[1] if ' ' in datetime_str else ''
        
        event_list.append({
            'id': e['event_id'],
            'title': e['title'],
            'description': e['description'],
            'category': e['category'],
            'category_display': CATEGORY_DISPLAY.get(e['category'], e['category']),
            'led_by': e['led_by'],
            'date': date_part,
            'time': time_part,
            'location': e['location'],
            'points': e['base_points_participant']
        })
    
    return event_list

def get_user_interests(user_id):
    """Get skill categories user is interested in."""
    db = get_db_connection()
    cursor = db.execute('''
        SELECT DISTINCT s.category
        FROM user_skill_interest usi
        JOIN skill s ON usi.skill_id = s.skill_id
        WHERE usi.user_id = ?
    ''', (user_id,))
    
    interests = [row['category'] for row in cursor.fetchall()]
    return interests

def categorize_events(events, user_interests=None):
    """Organize events into recommendation sections."""
    recommended = []
    bond_events = []
    by_category = {}
    
    for event in events:
        category = event['category']
        
        # Initialize category list if not exists
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(event)
        
        # Add to bond events (social games are for bonding)
        if category == 'social_games':
            bond_events.append(event)
        
        # Check if matches user interests
        if user_interests:
            # Map event categories to skill categories
            category_skill_map = {
                'tech_digital': 'Tech & Digital',
                'life_skills': 'Life Skills',
                'health_wellness': 'Health & Wellness',
                'culture_creative': 'Culture & Creative'
            }
            skill_category = category_skill_map.get(category)
            if skill_category and skill_category in user_interests:
                recommended.append(event)
    
    # If no recommendations based on interests, show popular events
    if not recommended:
        recommended = events[:5]
    
    return {
        'recommended': recommended[:8],  # Limit to 8
        'bond': bond_events[:8],  # Limit to 8
        'by_category': by_category
    }

@events_bp.route('/events')
def events():
    """Route to Events Page."""
    if 'user_id' not in session:
        flash("Please log in to access events.", "warning")
        return redirect(url_for('home.login_page'))
        
    role = session.get('user_role')
    user_id = session.get('user_id')
    
    if role == 'admin':
        return redirect(url_for('admin.admin_dashboard'))
    elif role == 'senior':
        return render_template('senior/senior_events.html',
                             recommended_events=categorized['recommended'],
                             bond_events=categorized['bond'],
                             events_by_category=categorized['by_category'],
                             category_display=CATEGORY_DISPLAY)
    else:  # youth or default
        return render_template('youth/youth_events.html',
                             recommended_events=categorized['recommended'],
                             bond_events=categorized['bond'],
                             events_by_category=categorized['by_category'],
                             category_display=CATEGORY_DISPLAY)
