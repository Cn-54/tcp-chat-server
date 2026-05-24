import socket
import threading

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


host = '127.0.0.1'
port = 4444

clients = []
usernames = []

s.bind((host,port))
s.listen(10)


def clientThread(client):
    sendmessage = "you are now connected\n type and press enter to start chatting\n"
    client.send(sendmessage.encode())
    while True:
        try:
            data = client.recv(1024)
            if not data:
                break
            decoded = data.decode()
            sender = usernames[clients.index(client)]

            if decoded.startswith("/msg"):
                parts = decoded.split(" ", 2)
                if len(parts) < 3:
                    client.send(b"Usage: /msg <username> <message>\n")
                elif parts[1] == sender:
                    client.send(b"You cannot message yourself.\n")
                elif parts[1] not in usernames:
                    client.send(f"User '{parts[1]}' not found.\n".encode())
                else:
                    recipient = clients[usernames.index(parts[1])]
                    recipient.send(f"(PM from {sender}): {parts[2]}".encode())
                    print(f"(PM) {sender} -> {parts[1]}: {parts[2]}")
            elif decoded.startswith("/list"):
                client.send("--- User List ---".encode())
                for i,user in enumerate(usernames):
                    client.send((f"{i}: {user}\n").encode())
            else:
                print(f"{sender}: {decoded}")
                recipients = [c for c in clients if c != client]
                for c in recipients:
                    c.send(f"{sender}: ".encode() + data)

        except (ConnectionResetError, ConnectionAbortedError, OSError):
            break

    idx = clients.index(client)
    message = f"{usernames[idx]} has disconnected."
    print(message)
    clients.remove(client)
    usernames.pop(idx)
    for c in clients:
        c.send(message.encode())
    client.close()


while True:
    c,addr = s.accept()
    username = c.recv(1024).decode()
    message = username + " has connected to the servr on: " + addr[0]+":"+ str(addr[1])

    print(message)
    for client in clients:
        client.send(message.encode())

    clients.append(c)
    usernames.append(username)

    threading.Thread(target=clientThread, args=(c,), daemon=True).start()
