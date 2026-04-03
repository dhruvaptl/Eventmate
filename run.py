#!/usr/bin/env python3
"""
⚡ Last-Minute Event Buddy
Run this file to start the app: python run.py
Then open: http://localhost:5000
"""
import subprocess
import sys
import os

# Auto-install Flask if missing
try:
    import flask
except ImportError:
    print("Installing Flask...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from app import app
print("\n" + "="*50)
print("⚡  EVENT BUDDY is running!")
print("="*50)
print("👉  Open your browser: http://localhost:5000")
print("    Press CTRL+C to stop")
print("="*50 + "\n")
app.run(debug=False, port=5000, host="0.0.0.0")
