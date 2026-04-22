from flask import Flask, request, jsonify
import socket, ssl
from aes_utils import *

app = Flask(__name__)

# 🔐 AES Key
key = generate_key()

# 🌐 TLS Socket Setup
context = ssl._create_unverified_context()
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn = context.wrap_socket(sock, server_hostname="localhost")
conn.connect(("127.0.0.1", 5555))

conn.setblocking(False)   # ✅ IMPORTANT (prevents freezing)

# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json

    conn.send(data["username"].encode())
    conn.send(data["password"].encode())

    res = conn.recv(1024).decode()
    return res


# ---------------- SEND MESSAGE ----------------
@app.route("/send", methods=["POST"])
def send():
    data = request.json

    encrypted = encrypt_message(key, data["message"])

    conn.send(encrypted)
    conn.send(data["receiver"].encode())

    return jsonify({
        "encrypted": str(encrypted)
    })


# ---------------- RECEIVE MESSAGE ----------------
@app.route("/receive", methods=["GET"])
def receive():
    try:
        data = conn.recv(4096)

        if data:
            decrypted = decrypt_message(key, data)
            return jsonify({"message": decrypted})

    except BlockingIOError:
        pass   # ✅ No data available (normal case)

    except Exception as e:
        print("Receive Error:", e)

    return jsonify({"message": None})


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(port=5001, debug=True)