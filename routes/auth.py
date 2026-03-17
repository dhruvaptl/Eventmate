from flask import Blueprint, render_template, request, redirect, session
from database import get_db

auth = Blueprint("auth", __name__)

@auth.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        db = get_db()
        db.execute(
            "INSERT INTO users (name,email,password,phone) VALUES (?,?,?,?)",
            (
                request.form["name"],
                request.form["email"],
                request.form["password"],
                request.form["phone"]
            )
        )
        db.commit()
        return redirect("/login")

    return render_template("register.html")

@auth.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (request.form["email"], request.form["password"])
        ).fetchone()

        if user:
            session["user"] = user[0]
            return redirect("/dashboard")

    return render_template("login.html")

@auth.route("/logout")
def logout():
    session.clear()
    return redirect("/")