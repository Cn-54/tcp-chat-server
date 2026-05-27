import sys
import socket
import threading

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 4444
PROMPT = "> "


def safe_print(msg):
    sys.stdout.write(f"\n{msg}\n{PROMPT}")
    sys.stdout.flush()

def listen_for_messages(sock):
    while True:
        try:
            safe_print(sock.recv(1024).decode())
        except OSError:
            safe_print("Lost connection to server.")
            break

username = input("Enter your username: ")
s = socket.socket()
s.connect((SERVER_HOST, SERVER_PORT))
s.send(username.encode())

threading.Thread(target=listen_for_messages, daemon=True, args=(s,)).start()

while True:
    try:
        message = input(PROMPT)
    except (EOFError, KeyboardInterrupt):
        break
    if message.lower() == "q":
        break
    if message:
        s.send(message.encode())

s.close()