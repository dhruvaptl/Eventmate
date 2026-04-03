from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for
from database import get_db
from functools import wraps

chat_bp = Blueprint('chat', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@chat_bp.route('/chat/<int:other_id>')
@login_required
def chat(other_id):
    db = get_db()
    other_user = db.execute('SELECT * FROM users WHERE id = ?', (other_id,)).fetchone()
    if not other_user:
        db.close()
        return redirect(url_for('events.dashboard'))

    messages = db.execute('''
        SELECT m.*, u.name as sender_name, u.avatar_color
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE (m.sender_id = ? AND m.receiver_id = ?)
           OR (m.sender_id = ? AND m.receiver_id = ?)
        ORDER BY m.created_at ASC
    ''', (session['user_id'], other_id, other_id, session['user_id'])).fetchall()

    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    db.close()
    return render_template('chat.html', other_user=other_user,
                           messages=messages, user=user)

@chat_bp.route('/chat/send', methods=['POST'])
@login_required
def send_message():
    data = request.get_json()
    receiver_id = data.get('receiver_id')
    content = data.get('content', '').strip()

    if not content or not receiver_id:
        return jsonify({'error': 'Missing fields'}), 400

    db = get_db()
    db.execute('INSERT INTO messages (sender_id, receiver_id, content) VALUES (?, ?, ?)',
               (session['user_id'], receiver_id, content))
    db.commit()

    messages = db.execute('''
        SELECT m.*, u.name as sender_name, u.avatar_color
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE (m.sender_id = ? AND m.receiver_id = ?)
           OR (m.sender_id = ? AND m.receiver_id = ?)
        ORDER BY m.created_at ASC
    ''', (session['user_id'], receiver_id, receiver_id, session['user_id'])).fetchall()

    db.close()
    return jsonify({'success': True, 'messages': [dict(m) for m in messages]})

@chat_bp.route('/chat/poll/<int:other_id>')
@login_required
def poll_messages(other_id):
    db = get_db()
    messages = db.execute('''
        SELECT m.*, u.name as sender_name, u.avatar_color
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE (m.sender_id = ? AND m.receiver_id = ?)
           OR (m.sender_id = ? AND m.receiver_id = ?)
        ORDER BY m.created_at ASC
    ''', (session['user_id'], other_id, other_id, session['user_id'])).fetchall()
    db.close()
    return jsonify([dict(m) for m in messages])

@chat_bp.route('/conversations')
@login_required
def conversations():
    db = get_db()
    user_id = session['user_id']
    convs = db.execute('''
        SELECT DISTINCT
            CASE WHEN sender_id = ? THEN receiver_id ELSE sender_id END as other_id,
            u.name, u.avatar_color, u.status,
            MAX(m.created_at) as last_msg_time,
            (SELECT content FROM messages WHERE
                ((sender_id=? AND receiver_id=u.id) OR (sender_id=u.id AND receiver_id=?))
                ORDER BY created_at DESC LIMIT 1) as last_msg
        FROM messages m
        JOIN users u ON u.id = CASE WHEN sender_id=? THEN receiver_id ELSE sender_id END
        WHERE sender_id=? OR receiver_id=?
        GROUP BY other_id
        ORDER BY last_msg_time DESC
    ''', (user_id, user_id, user_id, user_id, user_id, user_id)).fetchall()
    db.close()
    return render_template('conversations.html', convs=convs)
