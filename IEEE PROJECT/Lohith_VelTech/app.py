from flask import Flask, request, jsonify
import socket, ssl
from aes_utils import *

app = Flask(__name__)

clients = {}   # store connection per user
keys = {}      # AES key per user


def create_connection():
    context = ssl._create_unverified_context()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn = context.wrap_socket(sock, server_hostname="localhost")
    conn.connect(("127.0.0.1", 5555))
    return conn


# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        username = data["username"]

        conn = create_connection()

        conn.send(username.encode())
        conn.send(data["password"].encode())

        res = conn.recv(1024).decode()

        if res == "LOGIN_SUCCESS":
            clients[username] = conn
            keys[username] = generate_key()
            return "LOGIN_SUCCESS"

        return "LOGIN_FAILED"

    except Exception as e:
        print("Login Error:", e)
        return "LOGIN_FAILED"


# ---------------- SEND ----------------
@app.route("/send", methods=["POST"])
def send():
    try:
        data = request.json
        username = data.get("sender")   # we’ll send this from UI

        conn = clients.get(username)
        key = keys.get(username)

        encrypted = encrypt_message(key, data["message"])

        conn.send(encrypted)
        conn.send(data["receiver"].encode())

        return jsonify({"encrypted": str(encrypted)})

    except Exception as e:
        print("Send Error:", e)
        return jsonify({"encrypted": "error"})


# ---------------- RECEIVE ----------------
@app.route("/receive", methods=["POST"])
def receive():
    try:
        data = request.json
        username = data.get("username")

        conn = clients.get(username)
        key = keys.get(username)

        conn.settimeout(0.5)

        try:
            data = conn.recv(4096)
            if data:
                decrypted = decrypt_message(key, data)
                return jsonify({"message": decrypted})
        except:
            pass

        return jsonify({"message": None})

    except Exception as e:
        print("Receive Error:", e)
        return jsonify({"message": None})


if __name__ == "__main__":
    app.run(port=5000, debug=True)