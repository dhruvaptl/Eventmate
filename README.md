# ⚡ Last-Minute Event Buddy

A full-stack Flask web app to find companions for last-minute events.

## Features

- **User Auth** — Register, login, logout with session management
- **Events** — Create, browse, search & filter events by type/location
- **Real-time Chat** — AJAX-powered messaging with auto-polling
- **Connection Requests** — Send, accept, decline buddy requests
- **Availability Status** — Toggle Free / Busy in one click
- **User Profiles** — Bio, events created, ratings
- **Rating System** — Rate event companions 1–5 stars
- **Discover (Swipe)** — Tinder-like event browsing with keyboard support
- **Google Maps** — Live location previews on every event card

## Project Structure

```
event-buddy/
├── app.py              # App factory & entry point
├── database.py         # SQLite init & helpers
├── requirements.txt
├── routes/
│   ├── auth.py         # Register / Login / Logout
│   ├── events.py       # Dashboard, Create, Search, Discover
│   ├── chat.py         # Chat, Conversations, Poll
│   ├── requests.py     # Send / Accept / Decline + Rating
│   └── profile.py      # Profile view & update
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── create_event.html
│   ├── discover.html
│   ├── chat.html
│   ├── conversations.html
│   ├── requests.html
│   └── profile.html
└── static/
    ├── css/style.css
    └── js/main.js
```

## Setup & Run

```bash
# 1. Install dependencies
pip install flask

# 2. Run the app
python app.py

# 3. Open in browser
http://localhost:5000
```

## Database

SQLite (`event_buddy.db`) is auto-created on first run with tables:
- `users` — name, email, password, phone, status, bio, avatar_color
- `events` — title, location, event_time, event_type, description
- `messages` — sender_id, receiver_id, content, timestamp
- `requests` — sender_id, receiver_id, event_id, status
- `availability` — user_id, status
- `ratings` — rater_id, rated_id, score
