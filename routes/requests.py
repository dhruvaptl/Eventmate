from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for
from database import get_db
from functools import wraps

requests_bp = Blueprint('requests', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@requests_bp.route('/requests')
@login_required
def view_requests():
    db = get_db()
    user_id = session['user_id']

    incoming = db.execute('''
        SELECT r.*, u.name as sender_name, u.avatar_color, u.status as sender_status,
               e.title as event_title
        FROM requests r
        JOIN users u ON r.sender_id = u.id
        LEFT JOIN events e ON r.event_id = e.id
        WHERE r.receiver_id = ? AND r.status = 'pending'
        ORDER BY r.created_at DESC
    ''', (user_id,)).fetchall()

    sent = db.execute('''
        SELECT r.*, u.name as receiver_name, u.avatar_color,
               e.title as event_title
        FROM requests r
        JOIN users u ON r.receiver_id = u.id
        LEFT JOIN events e ON r.event_id = e.id
        WHERE r.sender_id = ?
        ORDER BY r.created_at DESC
    ''', (user_id,)).fetchall()

    accepted = db.execute('''
        SELECT r.*, u.name as other_name, u.id as other_id, u.avatar_color,
               e.title as event_title
        FROM requests r
        JOIN users u ON (CASE WHEN r.sender_id=? THEN r.receiver_id ELSE r.sender_id END = u.id)
        LEFT JOIN events e ON r.event_id = e.id
        WHERE (r.sender_id=? OR r.receiver_id=?) AND r.status='accepted'
        ORDER BY r.created_at DESC
    ''', (user_id, user_id, user_id)).fetchall()

    db.close()
    return render_template('requests.html', incoming=incoming, sent=sent, accepted=accepted)

@requests_bp.route('/requests/send', methods=['POST'])
@login_required
def send_request():
    data = request.get_json()
    receiver_id = data.get('receiver_id')
    event_id = data.get('event_id')

    if not receiver_id:
        return jsonify({'error': 'Missing receiver'}), 400

    if int(receiver_id) == session['user_id']:
        return jsonify({'error': 'Cannot connect with yourself'}), 400

    db = get_db()
    existing = db.execute(
        'SELECT id FROM requests WHERE sender_id=? AND receiver_id=? AND status="pending"',
        (session['user_id'], receiver_id)
    ).fetchone()

    if existing:
        db.close()
        return jsonify({'error': 'Request already sent'}), 400

    db.execute('INSERT INTO requests (sender_id, receiver_id, event_id) VALUES (?,?,?)',
               (session['user_id'], receiver_id, event_id))
    db.commit()
    db.close()
    return jsonify({'success': True})

@requests_bp.route('/requests/accept/<int:req_id>', methods=['POST'])
@login_required
def accept_request(req_id):
    db = get_db()
    db.execute('UPDATE requests SET status="accepted" WHERE id=? AND receiver_id=?',
               (req_id, session['user_id']))
    db.commit()
    db.close()
    return jsonify({'success': True})

@requests_bp.route('/requests/decline/<int:req_id>', methods=['POST'])
@login_required
def decline_request(req_id):
    db = get_db()
    db.execute('UPDATE requests SET status="declined" WHERE id=? AND receiver_id=?',
               (req_id, session['user_id']))
    db.commit()
    db.close()
    return jsonify({'success': True})

@requests_bp.route('/rate', methods=['POST'])
@login_required
def rate_user():
    data = request.get_json()
    rated_id = data.get('rated_id')
    score = data.get('score')

    if not rated_id or not score:
        return jsonify({'error': 'Missing fields'}), 400

    score = int(score)
    if score < 1 or score > 5:
        return jsonify({'error': 'Invalid score'}), 400

    db = get_db()
    db.execute('''INSERT INTO ratings (rater_id, rated_id, score) VALUES (?,?,?)
                  ON CONFLICT(rater_id, rated_id) DO UPDATE SET score=excluded.score''',
               (session['user_id'], rated_id, score))
    db.commit()
    avg = db.execute('SELECT AVG(score) as avg FROM ratings WHERE rated_id=?', (rated_id,)).fetchone()
    db.close()
    return jsonify({'success': True, 'avg': round(avg['avg'] or 0, 1)})
