from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database import get_db
import hashlib
import random

auth_bp = Blueprint('auth', __name__)

AVATAR_COLORS = ['#6C63FF','#FF6584','#43C59E','#F7B731','#FC5C65','#26de81','#fd9644','#45aaf2']

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@auth_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('events.dashboard'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        phone = request.form.get('phone', '').strip()

        if not all([name, email, password]):
            flash('Please fill in all required fields.', 'error')
            return render_template('register.html')

        db = get_db()
        existing = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        if existing:
            flash('Email already registered.', 'error')
            db.close()
            return render_template('register.html')

        color = random.choice(AVATAR_COLORS)
        db.execute(
            'INSERT INTO users (name, email, password, phone, avatar_color) VALUES (?, ?, ?, ?, ?)',
            (name, email, hash_password(password), phone, color)
        )
        db.commit()
        user = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        db.execute('INSERT OR IGNORE INTO availability (user_id, status) VALUES (?, ?)', (user['id'], 'Free'))
        db.commit()
        db.close()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ? AND password = ?',
                          (email, hash_password(password))).fetchone()
        db.close()

        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            return redirect(url_for('events.dashboard'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
