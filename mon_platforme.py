import eventlet
eventlet.monkey_patch()

import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# ==========================
# DATABASE MODELS
# ==========================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    profile_pic = db.Column(db.String(200), default="default.png")

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    text = db.Column(db.Text)
    image = db.Column(db.String(200))
    room = db.Column(db.String(100))

# ==========================
# ROUTES
# ==========================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat/<room>")
def chat(room):
    messages = Message.query.filter_by(room=room).all()
    return render_template("chat.html", room=room, messages=messages)

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["image"]
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        return {"url": url_for("static", filename="uploads/" + filename)}

# ==========================
# SOCKET EVENTS
# ==========================

@socketio.on("join")
def on_join(data):
    username = data["username"]
    room = data["room"]
    join_room(room)
    emit("receive_message", {
        "username": "System",
        "text": f"{username} a rejoint le salon",
        "room": room
    }),

@socketio.on("send_message")
def handle_message(data):
    message = Message(
        username=data["username"],
        text=data.get("text"),
        image=data.get("image"),
        room=data["room"]
    )
    db.session.add(message)
    db.session.commit()

    emit("receive_message", data, room=data["room"])

@socketio.on("typing")
def typing(data):
    emit("show_typing", data, room=data["room"], include_self=False)

@socketio.on("seen")
def seen(data):
    emit("message_seen", data, room=data["room"])

# ==========================
# RUN
# ==========================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )