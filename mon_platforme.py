from flask import Flask, render_template, request
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# dictionnaire pour stocker pseudo et couleur
users = {}
colors = ["blue", "green", "red", "orange", "purple", "brown"]

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def on_join(data):
    sid = request.sid
    pseudo = data['pseudo']
    color = colors[len(users) % len(colors)]
    users[sid] = {'pseudo': pseudo, 'color': color}
    send(f"{pseudo} a rejoint le chat", broadcast=True)

@socketio.on("send_message")
def handle_message(data):
    emit("receive_message", data, broadcast=True)
    emit("message_send", {"username": data["username"]}, broadcast=True)

@socketio.on("message_seen", function(data) {
    if( data.username === username) {
        const messages = document.querrySelectorAll("right");
        if(messages.length  ) {
            const last = message[message.length - 1];
            if(! last.querySelector(".seen")) {
                cont seen = document.createElement("div");
                seen.className = "seen";
                seen.textContent = ""

        }
    }
})

@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    user = users.pop(sid, {'pseudo': 'Inconnu'})
    send(f"{user['pseudo']} a quitté le chat", broadcast=True)

import eventlet
eventlet.monkey_patch()

import os

if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )