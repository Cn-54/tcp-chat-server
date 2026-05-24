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
            print(usernames[clients.index(client)] + ": " + data.decode())
            if data.decode().split(" ")[0] == "/msg":
                recipient = clients[usernames.index(data.decode().split(" ")[1])]
                privatemsg = f"(private message from: {usernames[clients.index(client)]})"
                recipient.send((privatemsg + " "+ data.decode().split(" ")[2]).encode())
            else:
                for c in clients:
                    if c != client:
                        c.send((usernames[clients.index(client)] + ": ").encode() + data)

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
