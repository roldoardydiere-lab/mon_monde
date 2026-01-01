from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from database import init_db

app = Flask(__name__)
app.secret_key = "secret"
socketio = SocketIO(app)

init_db()

def get_db():
    return sqlite3.connect("chat.db")

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]

        db = get_db()
        c = db.cursor()
        c.execute("SELECT password FROM users WHERE username=?", (user,))
        row = c.fetchone()

        if row and check_password_hash(row[0], pwd):
            session["user"] = user
            return redirect("/chat")

    return render_template("login.html")

@app.route("/register", methods=["POST"])
def register():
    user = request.form["username"]
    pwd = generate_password_hash(request.form["password"])

    db = get_db()
    c = db.cursor()
    c.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?,?)", (user, pwd))
    db.commit()
    return redirect("/")

@app.route("/chat")
def chat():
    db = get_db()
    c = db.cursor()
    c.execute("SELECT username, text FROM messages")
    messages = [{"username": u, "text": t} for u, t in c.fetchall()]
    return render_template("chat.html", username=session.get("user"), messages=messages)

@socketio.on("send_message")
def handle_message(data):
    db = get_db()
    c = db.cursor()
    c.execute("INSERT INTO messages (username, text) VALUES (?,?)",
              (data["username"], data["text"]))
    db.commit()
    emit("receive_message", data, broadcast=True)

if __name__ == "__main__":
    app.run()
