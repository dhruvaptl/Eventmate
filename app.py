from flask import Flask, render_template
from database import init_db
from routes.auth import auth
from routes.events import events
from routes.chat import chat

app = Flask(__name__)
app.secret_key = "supersecretkey"

init_db()

app.register_blueprint(auth)
app.register_blueprint(events)
app.register_blueprint(chat)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat/<int:user_id>")
def chat_page(user_id):
    return render_template("chat.html", user_id=user_id)

if __name__ == "__main__":
    app.run(debug=True)