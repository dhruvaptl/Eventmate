from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from database import get_db
from functools import wraps

events_bp = Blueprint('events', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@events_bp.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    user_id = session['user_id']

    events = db.execute('''
        SELECT e.*, u.name as creator_name, u.avatar_color,
               (SELECT AVG(score) FROM ratings WHERE rated_id = u.id) as avg_rating
        FROM events e
        JOIN users u ON e.user_id = u.id
        ORDER BY e.created_at DESC
    ''').fetchall()

    pending_count = db.execute(
        'SELECT COUNT(*) as cnt FROM requests WHERE receiver_id = ? AND status = "pending"',
        (user_id,)
    ).fetchone()['cnt']

    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    db.close()

    return render_template('dashboard.html', events=events,
                           pending_count=pending_count, user=user)

@events_bp.route('/events/create', methods=['GET', 'POST'])
@login_required
def create_event():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        location = request.form.get('location', '').strip()
        event_time = request.form.get('event_time', '').strip()
        event_type = request.form.get('event_type', '').strip()
        description = request.form.get('description', '').strip()

        if not all([title, location, event_time, event_type]):
            flash('Please fill in all required fields.', 'error')
            return render_template('create_event.html')

        db = get_db()
        db.execute(
            'INSERT INTO events (user_id, title, location, event_time, event_type, description) VALUES (?,?,?,?,?,?)',
            (session['user_id'], title, location, event_time, event_type, description)
        )
        db.commit()
        db.close()
        flash('Event created successfully!', 'success')
        return redirect(url_for('events.dashboard'))

    return render_template('create_event.html')

@events_bp.route('/events/search')
@login_required
def search_events():
    query = request.args.get('q', '').strip()
    db = get_db()
    events = db.execute('''
        SELECT e.*, u.name as creator_name, u.avatar_color,
               (SELECT AVG(score) FROM ratings WHERE rated_id = u.id) as avg_rating
        FROM events e
        JOIN users u ON e.user_id = u.id
        WHERE e.title LIKE ? OR e.location LIKE ?
        ORDER BY e.created_at DESC
    ''', (f'%{query}%', f'%{query}%')).fetchall()
    db.close()
    return jsonify([dict(e) for e in events])

@events_bp.route('/events/discover')
@login_required
def discover():
    db = get_db()
    user_id = session['user_id']
    events = db.execute('''
        SELECT e.*, u.name as creator_name, u.avatar_color, u.status as user_status,
               (SELECT AVG(score) FROM ratings WHERE rated_id = u.id) as avg_rating
        FROM events e
        JOIN users u ON e.user_id = u.id
        WHERE e.user_id != ?
        ORDER BY RANDOM()
        LIMIT 10
    ''', (user_id,)).fetchall()
    db.close()
    return render_template('discover.html', events=[dict(e) for e in events])

@events_bp.route('/availability', methods=['POST'])
@login_required
def set_availability():
    status = request.form.get('status', 'Free')
    db = get_db()
    db.execute('''INSERT INTO availability (user_id, status) VALUES (?, ?)
                  ON CONFLICT(user_id) DO UPDATE SET status=excluded.status, updated_at=CURRENT_TIMESTAMP''',
               (session['user_id'], status))
    db.execute('UPDATE users SET status = ? WHERE id = ?', (status, session['user_id']))
    db.commit()
    db.close()
    return jsonify({'success': True, 'status': status})
