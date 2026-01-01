import socket
import threading
import tkinter as tk
from tkinter import simpledialog

# --- Configuration réseau ---
host = '0.0.0.0'  # écoute toutes les interfaces
port = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen(1)
print("En attente d'un client...")

conn, addr = server.accept()
print(f"Connecté à {addr}")

# --- Interface graphique ---
root = tk.Tk()
root.title("Chat Serveur")
root.geometry("400x400")

chat_log = tk.Text(root, state='normal', bg="#f0f0f0")
chat_log.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

entry = tk.Entry(root, font=("Arial", 14))
entry.pack(padx=10, pady=5, fill=tk.X)

pseudo = simpledialog.askstring("Pseudo", "Entrez votre pseudo (Serveur):")
if not pseudo:
    pseudo = "Serveur"

# --- Envoyer message ---
def envoyer():
    msg = entry.get()
    if msg:
        chat_log.insert(tk.END, f"{pseudo}: {msg}\n", 'serveur')
        chat_log.tag_config('serveur', foreground='blue')
        conn.send(msg.encode())
        entry.delete(0, tk.END)

button = tk.Button(root, text="Envoyer", command=envoyer)
button.pack(pady=5)

# --- Recevoir messages ---
def recevoir():
    while True:
        try:
            msg_client = conn.recv(1024).decode()
            chat_log.insert(tk.END, f"Client: {msg_client}\n", 'client')
            chat_log.tag_config('client', foreground='green')
        except:
            break

thread = threading.Thread(target=recevoir)
thread.daemon = True
thread.start()

root.mainloop()