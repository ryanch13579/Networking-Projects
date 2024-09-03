import threading
import socket

# Setup server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('public_ip', rando_port_number))  # Listen on all network interfaces at port 55555
server.listen()

clients = []
nicknames = []
roles = {}
lock = threading.Lock()

def broadcast(message):
    with lock:
        for client in clients[:]:
            try:
                client.send(message)
            except (socket.error, BrokenPipeError):
                remove(client)

def remove(client):
    with lock:
        if client in clients:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames.pop(index)
            roles.pop(nickname, None)
            print(f'Client {nickname} has been removed from the chat.')
            broadcast(f'{nickname} left the chat'.encode('ascii'))

def kick_client(nickname_to_kick, admin_nickname):
    with lock:
        if roles.get(admin_nickname) != 'admin':
            print(f'Admin {admin_nickname} tried to kick a user without permissions.')
            return 'You do not have permission to kick users'.encode('ascii')
        
        if nickname_to_kick not in nicknames:
            print(f'Kick attempt failed: No user with the nickname {nickname_to_kick} found.')
            return f'No user with the nickname {nickname_to_kick} found.'.encode('ascii')
        
        index = nicknames.index(nickname_to_kick)
        client_to_kick = clients[index]

        print(f'Kicking client {nickname_to_kick} from the chat.')
        remove(client_to_kick)
        
        kick_message = f'{nickname_to_kick} has been kicked out of the chat'.encode('ascii')
        broadcast(kick_message)
        print(f'Client {nickname_to_kick} has been kicked by {admin_nickname}.')
        
        return kick_message

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            if not message:
                remove(client)
                break

            decoded_message = message.decode('ascii')
            client_index = clients.index(client)
            client_nickname = nicknames[client_index]

            print(f'Message from {client_nickname}: {decoded_message}')

            if decoded_message.startswith('/kick'):
                parts = decoded_message.split(' ')
                if len(parts) > 1:
                    nickname_to_kick = parts[1]
                    response = kick_client(nickname_to_kick, client_nickname)
                    client.send(response)
                else:
                    client.send('Usage: /kick <nickname>'.encode('ascii'))

            elif decoded_message.startswith('/leave'):
                remove(client)
                break

            else:
                broadcast(message)

        except Exception as e:
            print(f'Error: {e}')
            remove(client)
            break

def receive():
    while True:
        client, address = server.accept()
        print(f'Connected with {address}')

        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')

        with lock:
            if nickname == 'admin':
                if 'admin' in roles:
                    client.send('Admin already exists. Choose another nickname.'.encode('ascii'))
                    client.close()
                    continue
                role = 'admin'
            else:
                role = 'user'
            
            if nickname in nicknames:
                client.send('Nickname already taken. Try again.'.encode('ascii'))
                client.close()
                continue

            nicknames.append(nickname)
            roles[nickname] = role
            clients.append(client)

        print(f'Nickname of client is {nickname} with role {role}!')
        broadcast(f'{nickname} joined the chat'.encode('ascii'))
        client.send('Connected to the Server'.encode('ascii'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print('Server is listening...')
receive()
