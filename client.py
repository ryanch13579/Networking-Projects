import socket
import threading
import logging

# Get nickname from user
nickname = input('Choose a nickname: ')

# Create socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to server
server_host = 'public_server_ip'  # Update with the server address if different
server_port = 55555
client.connect((server_host, server_port))

def receive():
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
            else:
                print(message)
                f"Received: {message}"
        except (socket.error, BrokenPipeError) as e:
            f"Connection error: {e}"
            client.close()
            break
        except Exception as e:
            f"An error occurred: {e}"
            client.close()
            break

def write():
    while True:
        try:
            message_input = input('')  # Get input from the user
            if message_input.lower() == '/leave':
                client.send('/leave'.encode('ascii'))
                print(f'{nickname} has left the chat')
                client.close()
                break
            elif message_input.lower().startswith('/kick'):
                # Ensure the command format is correct
                if len(message_input.split(' ')) == 2:
                    client.send(message_input.encode('ascii'))
                else:
                    print('Usage: /kick <nickname>')
            else:
                message = f'{nickname}: {message_input}'  # Format the message
                client.send(message.encode('ascii'))  # Send the message to the server
        except (socket.error, BrokenPipeError) as e:
            f"Connection error: {e}"
            client.close()
            break
        except Exception as e:
            f"An error occurred: {e}"
            client.close()
            break

# Create and start threads
receive_thread = threading.Thread(target=receive, daemon=True)
receive_thread.start()

write_thread = threading.Thread(target=write, daemon=True)
write_thread.start()

# Wait for the write_thread to finish before exiting the script
write_thread.join()
