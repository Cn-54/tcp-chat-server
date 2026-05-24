import socket
import threading
from datetime import datetime

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 4444

def listen_for_messages(sock):
    while True:
        try:
            message = sock.recv(1024).decode()
            print("\n" + message)
        except:
            print("Lost connection to server.")
            break


username = input("enter your username: ")
s = socket.socket()
s.connect((SERVER_HOST, SERVER_PORT))
s.send(username.encode())

threading.Thread(target=listen_for_messages,daemon=True, args=(s,)).start()

while True:
    message = input()
    if message.lower() == 'q':
        break
    to_send = f"{message}"
    s.send(to_send.encode())

s.close()   