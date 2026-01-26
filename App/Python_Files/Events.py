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
    
    # Check if published_at column exists
    cursor = db.execute("PRAGMA table_info(event)")
    columns = [row['name'] for row in cursor.fetchall()]
    has_published_at = 'published_at' in columns
    
    if has_published_at:
        # Use the new query with published_at
        cursor = db.execute('''
            SELECT event_id, title, description, category, led_by, 
                   start_datetime, location, status, base_points_participant,
                   published_at,
                   CASE 
                       WHEN published_at IS NOT NULL 
                       AND julianday('now') - julianday(published_at) <= 7 
                       THEN 1 
                       ELSE 0 
                   END as is_new
            FROM event 
            WHERE status IN ('approved', 'published')
            ORDER BY start_datetime ASC
        ''')
    else:
        # Fallback query without published_at (backward compatibility)
        cursor = db.execute('''
            SELECT event_id, title, description, category, led_by, 
                   start_datetime, location, status, base_points_participant,
                   NULL as published_at,
                   0 as is_new
            FROM event 
            WHERE status IN ('approved', 'published')
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
            'points': e['base_points_participant'],
            'is_new': bool(e['is_new']) if has_published_at else False,
            'published_at': e['published_at'] if has_published_at else None
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
    new_events = []
    by_category = {}
    
    for event in events:
        category = event['category']
        
        # Initialize category list if not exists
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(event)
        
        # Add to new events if marked as new
        if event.get('is_new', False):
            new_events.append(event)
        
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
    
    # If no recommendations based on interests, show popular events (fallback)
    if not recommended:
        recommended = events[:5]
    
    # Sort new events by published_at DESC (most recent first)
    new_events.sort(key=lambda x: x.get('published_at', '') or '', reverse=True)
    
    # DEDUPLICATION:
    # If an event is in 'new', remove it from 'recommended' and 'bond' to avoid duplicates on dashboard
    new_ids = {e['id'] for e in new_events}
    
    recommended = [e for e in recommended if e['id'] not in new_ids]
    bond_events = [e for e in bond_events if e['id'] not in new_ids]
    
    return {
        'new': new_events[:8],  # Limit to 8 newest events
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
    
    # Fetch all events
    all_events = get_all_events()
    
    # Get user's interests
    user_interests = get_user_interests(user_id) if user_id else []
    
    # Categorize events
    categorized = categorize_events(all_events, user_interests)
    
    if role == 'admin':
        return redirect(url_for('admin.admin_dashboard'))
    elif role == 'senior':
        return render_template('senior/senior_events.html',
                             new_events=categorized['new'],
                             recommended_events=categorized['recommended'],
                             bond_events=categorized['bond'],
                             events_by_category=categorized['by_category'],
                             category_display=CATEGORY_DISPLAY)
    else:  # youth or default
        return render_template('youth/youth_events.html',
                             new_events=categorized['new'],
                             recommended_events=categorized['recommended'],
                             bond_events=categorized['bond'],
                             events_by_category=categorized['by_category'],
                             category_display=CATEGORY_DISPLAY)


# =====================================================
# EVENT DETAILS & SIGN-UP
# =====================================================

# Role display names mapping
ROLE_DISPLAY = {
    'teacher': 'Mentor',
    'participant': 'Participant'
}

def get_event_by_id(event_id):
    """Fetch full event details by ID."""
    db = get_db_connection()
    
    # Check if published_at column exists
    cursor = db.execute("PRAGMA table_info(event)")
    columns = [row['name'] for row in cursor.fetchall()]
    has_published_at = 'published_at' in columns
    
    if has_published_at:
        cursor = db.execute('''
            SELECT e.*, g.name as grc_name,
                   CASE 
                       WHEN e.published_at IS NOT NULL 
                       AND julianday('now') - julianday(e.published_at) <= 7 
                       THEN 1 
                       ELSE 0 
                   END as is_new
            FROM event e
            LEFT JOIN grc g ON e.grc_id = g.grc_id
            WHERE e.event_id = ? 
            AND e.status IN ('approved', 'published', 'voided', 'cancelled')
        ''', (event_id,))
    else:
        cursor = db.execute('''
            SELECT e.*, g.name as grc_name, 0 as is_new
            FROM event e
            LEFT JOIN grc g ON e.grc_id = g.grc_id
            WHERE e.event_id = ? 
            AND e.status IN ('approved', 'published', 'voided', 'cancelled')
        ''', (event_id,))
        
    event = cursor.fetchone()
    
    if not event:
        return None
    
    # Parse date and time
    datetime_str = event['start_datetime']
    date_part = datetime_str.split(' ')[0] if ' ' in datetime_str else datetime_str
    time_part = datetime_str.split(' ')[1][:5] if ' ' in datetime_str else ''
    
    return {
        'id': event['event_id'],
        'title': event['title'],
        'description': event['description'],
        'category': event['category'],
        'category_display': CATEGORY_DISPLAY.get(event['category'], event['category']),
        'led_by': event['led_by'],
        'date': date_part,
        'time': time_part,
        'location': event['location'],
        'grc_name': event['grc_name'],
        'base_points_teacher': event['base_points_teacher'] or 0,
        'base_points_buddy': event['base_points_buddy'] or 0,
        'base_points_participant': event['base_points_participant'] or 0,
        'max_capacity': event['max_capacity'],
        'status': event['status'],
        'void_reason': event['void_reason'],
        'is_new': bool(event['is_new']) if has_published_at else False,
        'published_at': event['published_at'] if has_published_at else None
    }


def get_role_requirements(event_id):
    """Get required slots per role for an event (Mentor and Participant only)."""
    db = get_db_connection()
    cursor = db.execute('''
        SELECT role_type, required_count
        FROM event_role_requirement
        WHERE event_id = ? AND role_type IN ('teacher', 'participant')
    ''', (event_id,))
    
    requirements = {}
    for row in cursor.fetchall():
        requirements[row['role_type']] = row['required_count']
    
    # Return defaults if no requirements set (only if DB record missing)
    # The logic above already fetches correct values from DB.
    # We just ensure keys exist for safety.
    if 'teacher' not in requirements:
        requirements['teacher'] = 5
    if 'participant' not in requirements:
        requirements['participant'] = 15
    
    return requirements


def get_role_bookings(event_id):
    """Get current bookings per role with user details (Mentor and Participant only)."""
    db = get_db_connection()
    cursor = db.execute('''
        SELECT eb.role_type, eb.user_id, u.name, u.role as user_role
        FROM event_booking eb
        JOIN user u ON eb.user_id = u.user_id
        WHERE eb.event_id = ? AND eb.status = 'booked' AND eb.role_type IN ('teacher', 'participant')
        ORDER BY eb.booked_at ASC
    ''', (event_id,))
    
    bookings = {
        'teacher': [],
        'participant': []
    }
    
    for row in cursor.fetchall():
        role_type = row['role_type']
        if role_type in bookings:
            bookings[role_type].append({
                'user_id': row['user_id'],
                'name': row['name'],
                'user_role': row['user_role']
            })
    
    return bookings


def get_role_slots(event_id):
    """Calculate filled vs required slots per role (Mentor and Participant only)."""
    requirements = get_role_requirements(event_id)
    bookings = get_role_bookings(event_id)
    
    slots = {}
    total_filled = 0
    total_capacity = 0
    
    for role in ['teacher', 'participant']:
        required = requirements.get(role, 0)
        filled = len(bookings.get(role, []))
        available = max(0, required - filled)
        
        slots[role] = {
            'required': required,
            'filled': filled,
            'available': available,
            'is_full': available == 0,
            'users': bookings.get(role, [])
        }
        
        total_filled += filled
        total_capacity += required
    
    # Add overall event capacity info
    slots['total_filled'] = total_filled
    slots['total_capacity'] = total_capacity
    slots['is_event_full'] = total_filled >= total_capacity
    
    return slots


def is_user_signed_up(event_id, user_id):
    """Check if user is already signed up for this event."""
    db = get_db_connection()
    cursor = db.execute('''
        SELECT role_type FROM event_booking
        WHERE event_id = ? AND user_id = ? AND status = 'booked'
    ''', (event_id, user_id))
    row = cursor.fetchone()
    return row['role_type'] if row else None


def can_user_mentor(event_led_by, user_role):
    """Check if user is eligible to mentor based on who leads the event.
    
    Rules:
    - Youth-led events: Only youth can mentor
    - Senior-led events: Only seniors can mentor
    - Employee-led events: No one can mentor (employees run these)
    """
    if event_led_by == 'youth' and user_role == 'youth':
        return True
    if event_led_by == 'senior' and user_role == 'senior':
        return True
    # Employee-led events: no mentors allowed (employees run the event)
    return False


@events_bp.route('/event/<int:event_id>')
def event_details(event_id):
    """Display event details page with role sign-up options."""
    if 'user_id' not in session:
        flash("Please log in to view event details.", "warning")
        return redirect(url_for('home.login_page'))
    
    user_id = session.get('user_id')
    role = session.get('user_role')
    
    # Get event details
    event = get_event_by_id(event_id)
    if not event:
        flash("Event not found or not available.", "error")
        return redirect(url_for('events.events'))
    
    # Check if event is voided/cancelled
    if event['status'] == 'voided':
        # Show cancellation notice instead of event details
        return render_template('shared/event_cancelled.html',
                             event_title=event['title'],
                             void_reason=event.get('void_reason', 'This event has been cancelled.'),
                             user_role=role)
    
    # Get role slot information
    slots = get_role_slots(event_id)
    
    # Check if user is already signed up
    user_signed_up_role = is_user_signed_up(event_id, user_id)
    
    # Check mentor eligibility
    can_mentor = can_user_mentor(event['led_by'], role)
    
    # Prepare template data
    template = 'shared/event_details.html'
    
    return render_template(template,
                         event=event,
                         slots=slots,
                         role_display=ROLE_DISPLAY,
                         user_signed_up_role=user_signed_up_role,
                         user_role=role,
                         can_mentor=can_mentor)


@events_bp.route('/event/<int:event_id>/signup', methods=['POST'])
def event_signup(event_id):
    """Handle user sign-up for an event role."""
    if 'user_id' not in session:
        flash("Please log in to sign up.", "warning")
        return redirect(url_for('home.login_page'))
    
    user_id = session.get('user_id')
    role_type = request.form.get('role_type')
    
    if role_type not in ['teacher', 'participant']:
        flash("Invalid role selected.", "error")
        return redirect(url_for('events.event_details', event_id=event_id))
    
    # Get event details for validation
    event = get_event_by_id(event_id)
    if not event:
        flash("Event not found.", "error")
        return redirect(url_for('events.events'))

    # Validate mentor eligibility
    if role_type == 'teacher':
        user_role = session.get('user_role')
        if not can_user_mentor(event['led_by'], user_role):
            flash(f"Only {event['led_by'].capitalize()}s can mentor this event.", "error")
            return redirect(url_for('events.event_details', event_id=event_id))
    
    # Check if already signed up
    existing_role = is_user_signed_up(event_id, user_id)
    if existing_role:
        flash(f"You are already signed up as {ROLE_DISPLAY.get(existing_role, existing_role)}.", "warning")
        return redirect(url_for('events.event_details', event_id=event_id))
    
    # Check slot availability
    slots = get_role_slots(event_id)
    if slots[role_type]['is_full']:
        flash(f"Sorry, {ROLE_DISPLAY.get(role_type, role_type)} slots are full.", "error")
        return redirect(url_for('events.event_details', event_id=event_id))
    
    # Check for existing booking (to handle re-signup after withdrawal)
    db = get_db_connection()
    cursor = db.execute('SELECT status FROM event_booking WHERE user_id = ? AND event_id = ?', (user_id, event_id))
    existing_booking = cursor.fetchone()
    
    if existing_booking:
        # Update existing record (e.g. if status was 'cancelled')
        db.execute('''
            UPDATE event_booking 
            SET role_type = ?, status = 'booked', booked_at = datetime('now')
            WHERE user_id = ? AND event_id = ?
        ''', (role_type, user_id, event_id))
    else:
        # Insert new record
        db.execute('''
            INSERT INTO event_booking (user_id, event_id, role_type, status, booked_at)
            VALUES (?, ?, ?, 'booked', datetime('now'))
        ''', (user_id, event_id, role_type))
        
    db.commit()
    
    flash(f"Successfully signed up as {ROLE_DISPLAY.get(role_type, role_type)}! 🎉", "success")
    return redirect(url_for('events.event_details', event_id=event_id))


@events_bp.route('/event/<int:event_id>/withdraw', methods=['POST'])
def event_withdraw(event_id):
    """Handle user withdrawal from an event."""
    if 'user_id' not in session:
        flash("Please log in.", "warning")
        return redirect(url_for('home.login_page'))
    
    user_id = session.get('user_id')
    
    # Check if signed up
    existing_role = is_user_signed_up(event_id, user_id)
    if not existing_role:
        flash("You are not signed up for this event.", "warning")
        return redirect(url_for('events.event_details', event_id=event_id))
    
    # Update booking status to cancelled
    db = get_db_connection()
    db.execute('''
        UPDATE event_booking 
        SET status = 'cancelled'
        WHERE event_id = ? AND user_id = ?
    ''', (event_id, user_id))
    db.commit()
    
    flash("You have withdrawn from this event.", "info")
    return redirect(url_for('events.event_details', event_id=event_id))

