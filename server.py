from datetime import datetime
import socket
import threading

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


host = '127.0.0.1'
port = 4444

clients = {}
rooms = {}

"""
rooms:
    name:
        clients = set()
        owner = client
"""

def doPM(decoded,sender,client):
    parts = decoded.split(" ", 2)
    if len(parts) < 3:
        client.send(b"Usage: /msg <username> <message>\n")
    elif parts[1] == sender:
        client.send(b"You cannot message yourself.\n")
    elif get_client_by_username(parts[1]) is None:
        client.send(f"User '{parts[1]}' not found.\n".encode())
    else:
        recipient = get_client_by_username(parts[1])
        recipient.send(f"(PM from {sender}): {parts[2]}".encode())
        print(f"(PM) {sender} -> {parts[1]}: {parts[2]}")

def doList(client):
    room = clients[client]["room"]

    if room is None:
        client.send(b"You are not in a room.")
        return

    client.send(b"--- User List ---\n")

    for i, c in enumerate(rooms[room]["clients"]):
        user = clients[c]["username"]
        client.send(f"{i}: {user}\n".encode())

def doNick(decoded,sender,client):
    parts = decoded.split(" ", 1)
    if len(parts) > 1:
        found = False
        for c in clients:
            if clients[c]["username"] == parts[1]:
                found = True
                break
        if not found:
            print(f"{sender} has changed their name to {parts[1]}!")
            room = clients[client]["room"]
            

            client.send("username changed succesfully".encode())
            clients[client]["username"] = parts[1]
            sendMessagetoRoom(room,f"{sender} has changed their name to {parts[1]}!",client)
        else:
            client.send("enter a unique username!".encode())
    else:
            client.send("enter a valid username".encode())

def doCommand(client):
    client.send("/msg:\n" \
"Usage: /msg <username> <message>\n" \
"Description: sends a private message to the specified user"\
"/list:\n" \
"Usage: /list\n" \
"Description: Gives the user a list of all users currently connected\n" \
"nick:\n" \
"Usage: /nick <username>\n" \
"Description: changes your username to the unique username specified".encode())

def doCreateRoom(decoded,client):
    parts = decoded.split(" ", 1)
    if len(parts) < 2:
        client.send(b"Usage: /create <room name>\n")
    elif doesRoomExist(parts[1]):
        client.send("a room with that name already exist try again!".encode())
    else:
        rooms[parts[1]] = {
            "clients": set(),
            "owner": client
        }
        moveClientToRoom(client,parts[1])
        client.send(f"room created with name {parts[1]}\n you are the owner of this room".encode())

def doLeaveRoom(client):
    old_room = clients[client]["room"]

    if old_room is None:
        client.send(b"You are not in a room.")
        return

    username = clients[client]["username"]

    rooms[old_room]["clients"].discard(client)
    clients[client]["room"] = None

    sendMessagetoRoom(old_room, f"{username} has left the room!", client)


def doWhoami(client):
    client.send(clients[client]["username"].encode())

def doWhere(client):
    room = clients[client]["room"]

    if room is None:
        client.send(b"You are not currently in a room.")
    else:
        client.send(f"You are currently in room: {room}".encode())

commands = {
    "message": doPM,
    "list": doList,
    "nick": doNick,
    "command": doCommand,
    "create": doCreateRoom,
    "leave": doLeaveRoom,
    "whoami": doWhoami,
    "where": doWhere
}

s.bind((host,port))
s.listen(10)

def get_client_by_username(username):
    for c in clients:
        if clients[c]["username"] == username:
            return c
    return None


def moveClientToRoom(client, room):
    old_room = clients[client]["room"]
    if old_room is not None:
        rooms[old_room]["clients"].discard(client)
    rooms[room]["clients"].add(client)
    clients[client]["room"] = room

def sendMessagetoRoom(room,message,sender=None):
    if room != None:
        recipients = [
            c for c in rooms[room]["clients"]
            if c != sender
        ]
        for c in recipients:
            c.send(message.encode())

def doesRoomExist(name):
    return name in rooms

def clientThread(client):
    client.send("you are now connected\ntype and press enter to start chatting\nenter /commands for a list of commands and their uses\n".encode())
    while True:
        try:
            data = client.recv(1024)
            if not data:
                break
            decoded = data.decode()
            sender = clients[client]["username"]
            if decoded.startswith("/msg"):
                commands["message"](decoded,sender,client)
            elif decoded.startswith("/list"):
                commands["list"](client)
            elif decoded.startswith("/nick"):
                commands["nick"](decoded,sender,client)
            elif decoded.startswith("/commands"):
                commands["command"](client)

            elif decoded.startswith("/whoami"):
                commands["whoami"](client)
            elif decoded.startswith("/where"):
                commands["where"](client)

            elif decoded.startswith("/create"):
                commands["create"](decoded,client)
            elif decoded.startswith("/leave"):
                commands["leave"](client)
            else:
                time = datetime.now().strftime("%H:%M:%S")
                message = f"[{time}] {sender}: {decoded}"
                room = clients[client]["room"]
                print(f"{room} -> {message}")
                sendMessagetoRoom(room,message,client)
        except (ConnectionResetError, ConnectionAbortedError, OSError):
            break

    room = clients[client]["room"]
    message = f"{clients[client]["username"]} has disconnected."
    print(message)
    sendMessagetoRoom(room,message,client)
    del clients[client]
    client.close()


while True:
    c,addr = s.accept()
    username = c.recv(1024).decode()
    message = username + " has connected to the servr on: " + addr[0]+":"+ str(addr[1])

    print(message)
    for client in clients:
        client.send(message.encode())

    clients[c] = {
        "username": username,
        "room": None
    }


    threading.Thread(target=clientThread, args=(c,), daemon=True).start()
