from flask import Flask
from database import init_db
from routes.auth import auth_bp
from routes.events import events_bp
from routes.chat import chat_bp
from routes.requests import requests_bp
from routes.profile import profile_bp
import os

def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)

    init_db()

    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(requests_bp)
    app.register_blueprint(profile_bp)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
