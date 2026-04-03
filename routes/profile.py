from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for
from database import get_db
from functools import wraps

profile_bp = Blueprint('profile', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@profile_bp.route('/profile')
@profile_bp.route('/profile/<int:user_id>')
@login_required
def profile(user_id=None):
    if user_id is None:
        user_id = session['user_id']

    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        db.close()
        return redirect(url_for('events.dashboard'))

    avg_rating = db.execute('SELECT AVG(score) as avg, COUNT(*) as cnt FROM ratings WHERE rated_id=?',
                            (user_id,)).fetchone()
    events = db.execute('SELECT * FROM events WHERE user_id=? ORDER BY created_at DESC', (user_id,)).fetchall()

    my_rating = None
    if session['user_id'] != user_id:
        my_rating = db.execute('SELECT score FROM ratings WHERE rater_id=? AND rated_id=?',
                               (session['user_id'], user_id)).fetchone()

    db.close()
    return render_template('profile.html',
                           profile_user=user,
                           avg_rating=round(avg_rating['avg'] or 0, 1),
                           rating_count=avg_rating['cnt'],
                           events=events,
                           my_rating=my_rating['score'] if my_rating else 0,
                           is_own=session['user_id'] == user_id)

@profile_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    bio = request.form.get('bio', '').strip()
    db = get_db()
    db.execute('UPDATE users SET bio=? WHERE id=?', (bio, session['user_id']))
    db.commit()
    db.close()
    return jsonify({'success': True})
