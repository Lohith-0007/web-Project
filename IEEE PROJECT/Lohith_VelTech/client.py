import socket
import ssl
from aes_utils import *
import time

key = generate_key()

def start_client():
    context = ssl._create_unverified_context()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn = context.wrap_socket(sock, server_hostname="localhost")

    conn.connect(("127.0.0.1", 5555))

    username = input("Username: ")
    password = input("Password: ")

    conn.send(username.encode())
    conn.send(password.encode())

    response = conn.recv(1024).decode()

    if response != "LOGIN_SUCCESS":
        print("Login failed")
        return

    print("Login successful")

    while True:
        msg = input("Message: ")
        receiver = input("Send to: ")

        start = time.time()

        encrypted = encrypt_message(key, msg)
        conn.send(encrypted)
        conn.send(receiver.encode())

        print("Encrypted sent:", encrypted)

        data = conn.recv(4096)
        if data:
            decrypted = decrypt_message(key, data)
            print("Received:", decrypted)

        end = time.time()
        print("Time:", end - start)

if __name__ == "__main__":
    start_client()