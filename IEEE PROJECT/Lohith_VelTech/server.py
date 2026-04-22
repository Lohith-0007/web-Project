hithVeimport socket
import ssl
import threading
import json

clients = {}

def handle_client(conn, addr):
    print(f"[+] Connected: {addr}")

    try:
        username = conn.recv(1024).decode()
        password = conn.recv(1024).decode()

        print("Login attempt:", username)

        with open("users.json") as f:
            users = json.load(f)

        if username in users and users[username] == password:
            conn.send(b"LOGIN_SUCCESS")
            clients[username] = conn
            print(f"{username} logged in")
        else:
            conn.send(b"LOGIN_FAILED")
            conn.close()
            return

        while True:
            try:
                data = conn.recv(4096)
                if not data:
                    break

                target_user = conn.recv(1024).decode()

                print(f"{username} → {target_user}")

                if target_user in clients:
                    clients[target_user].send(data)
                    print("Message forwarded ✅")
                else:
                    print("User not online ❌")

            except:
                break

    except Exception as e:
        print("Error:", e)

    finally:
        if username in clients:
            del clients[username]
        conn.close()
        print(f"[-] Disconnected: {addr}")


def start_server():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 5555))
    server_socket.listen(5)

    print("[*] Server started...")

    while True:
        client_socket, addr = server_socket.accept()
        conn = context.wrap_socket(client_socket, server_side=True)

        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


if __name__ == "__main__":
    start_server()