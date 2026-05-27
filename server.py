from datetime import datetime
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
    sendmessage = "you are now connected\ntype and press enter to start chatting\nenter /commands for a list of commands and their uses\n"
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
            
            elif decoded.startswith("/nick"):
                parts = decoded.split(" ", 1)
                if len(parts) > 1:
                    newUsername = parts[1]
                    if usernames.count(newUsername) < 1:
                        print(f"{sender} has changed their name to {newUsername}!")
                        recipients = [c for c in clients if c != client]
                        for c in recipients:
                            c.send(f"{sender} has changed their username to {newUsername}".encode())
                        client.send("username changed succesfully".encode())
                        usernames[clients.index(client)] = newUsername
                    else:
                        client.send("enter a unique username!".encode())
                else:
                        client.send("enter a valid username".encode())

            elif decoded.startswith("/commands"):
                client.send("/msg:\n" \
                "Usage: /msg <username> <message>\n" \
                "Description: sends a private message to the specified user".encode())

                client.send("/list:\n" \
                "Usage: /list\n" \
                "Description: Gives the user a list of all users currently connected".encode())

                client.send("/nick:\n" \
                    "Usage: /nick <username>\n" \
                    "Description: changes your username to the unique username specified".encode())

            else:
                time = datetime.now().strftime("%H:%M:%S")
                message = f"[{time}] {sender}: {decoded}"
                print(message)
                recipients = [c for c in clients if c != client]
                for c in recipients:
                    c.send(message.encode())

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
