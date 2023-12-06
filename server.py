# Import required modules
import socket
import threading
import time
import struct
import cv2
import pickle

HOST = socket.gethostname()
host_ip = socket.gethostbyname(HOST)
PORT = 6000 # You can use any port between 0 to 65535

print(f'{host_ip}')

active_clients = [] # List of all currently connected users
FORMAT = 'utf-8'
# Function to listen for upcoming messages from a client
def broadcast(message,client1,command):
    
    for client in active_clients:
        if(client[1]!=client1):
            if(command=='M'):
                client[1].send(message.encode('utf-8'))
            else:
                print("active_clients")
                client[1].send(message)
def unicat_documnent(message,clinet,client_reciver,command):
      for client in active_clients:
        if(client[1]==client_reciver):
                if(command=='M'):
                    client[1].send(message.encode('utf-8'))
                else:
                    client[1].send(message)
def broadcastc(command,client1):
    for client in active_clients:
        if(client[1]!=client1):
            client[1].send(command.encode('utf-8'))
def broadcast_intro_video(client_1,command):
    print('HI-important')
    x = 'video'
    for client in active_clients:
        if(client[1]!=client_1):
            client[1].send(x.encode('utf-8'))
    
def function_intro(client,header1):
    command = 'F'
    for client_1 in active_clients:
        if client_1[1]!= client:
            client_1[1].send('document'.encode('Utf-8'))
            time.sleep(1)
            time.sleep(5)
            header=header1.decode('utf-8')
            file_name, file_size_str = header.strip().split('|')
            file_size = int(file_size_str)
            broadcast(header1,client,command)
            with open(file_name, "wb") as file:
                bytes_received = 0
                while bytes_received < file_size:
                            file_data = client.recv(1024)
                            if not file_data:  
                                break
                            file.write(file_data)
                            bytes_received += len(file_data)
                            broadcast(file_data,client,command)
                file.close()
                print("File received and saved successfully.")
            
def listen_for_messages(client,username):
    while(1):
        
        try:
            message_2 = client.recv(2048).decode('utf-8')
        except ConnectionResetError as e:
            print(f"ConnectionResetError: {e}")
            # Handle the error as needed (e.g., remove the client from the list)
            break
        except ConnectionAbortedError as e:
            print(f"ConnectionAbortedError: {e}")
            # Handle the error as needed (e.g., remove the client from the list)
            break
        if message_2 == 'chat':
            print('Hi')
            
            message_1= client.recv(2048).decode('utf-8')
            print(f'{message_1}')
            if message_1 == 'all':
                    
                        print('all')
                        message = client.recv(2048).decode('utf-8')
                        if message != '':
                            
                            final_msg = username + '~' + message
                            send_messages_to_all(final_msg)

                        else:
                            print(f"The message send from client {username} is empty")
            else:
                    
                        print('selected')
                        message = client.recv(2048).decode('utf-8')
                        print(f'{message}')
                        if message != '':
                            
                            final_msg = username + '~' + message
                            send_message_to_client(message_1,final_msg)

                        else:
                            print(f"The message send from client {username} is empty")        
        elif message_2 == 'doucment':
            command = 'F'
            print('Server recognized this as a document sending application')
            message_1= client.recv(2048).decode('utf-8')
            print(f'{message_1}')
            if message_1!="all":
                print("Uni-casting")
                client_1=search_client(message_1)
                x = 'document'
                client_1.send(x.encode('utf-8'))
                time.sleep(5)
                header1 = client.recv(100)
                header=header1.decode('utf-8')
                file_name, file_size_str = header.strip().split('|')
                file_size = int(file_size_str)
                time.sleep(5)
                unicat_documnent(header1,client,client_1,command)
                with open(file_name, "wb") as file:
                        bytes_received = 0
                        while bytes_received < file_size:
                            file_data = client.recv(1024)
                            if not file_data:  
                                break
                            file.write(file_data)
                            bytes_received += len(file_data)
                            unicat_documnent(file_data,client,client_1,command)
                file.close()
                print("File received and saved successfully.")
            else:
                print("broad-casting")
                header1 = client.recv(100)
                function_intro(client,header1)
                
            
        elif message_2 == 'video':
            command ='V'
            print('this is recognized as an video frame transfer')
            print('The client is listening to the frame')
            data = b""
            payload_size = struct.calcsize("L")
            cv2.namedWindow("Receiving video", cv2.WINDOW_NORMAL)
            broadcast_intro_video(client,command)
            while True:
                    while len(data) < payload_size:
                        packet = client.recv(4 * 1024)
                        
                        if not packet:
                            break
                        data += packet
                    
                    packed_msg_size = data[:payload_size]
                    data = data[payload_size:]
                    
                    try:
                        msg_size = struct.unpack("L", packed_msg_size)[0]
                    except:
                        print("Done!")
                        cv2.destroyAllWindows()
                        break
                    broadcast(packed_msg_size,client,command)
                    while len(data) < msg_size:
                        data += client.recv(4 * 1024)
                    
                    frame_data = data[:msg_size]
                    data = data[msg_size:]
                    broadcast(frame_data,client,command)
                    status, frame = pickle.loads(frame_data)
                    # print(type(status))
                    if status==b'1':
                        cv2.destroyAllWindows()
                        break
                        # sys.exit(0)
                    cv2.imshow("Receiving video", frame)
                    key = cv2.waitKey(1) & 0xFF
                    
                    if key == ord('q'):
                        last_frame_data = pickle.dumps((status, frame))
                        client.send(struct.pack("L", len(last_frame_data)))
                        client.send(last_frame_data)
                        cv2.destroyAllWindows()
                        client.send(b'q')
                        # sys.exit(0)
        elif message_2 == 'screen-sharing':
             print('This is a screen sharing apllication information')
             message_1 = client.recv(1024).decode('utf-8')
             print(f'{message_1}')
             send_messages_to_all_1(message_1,client)
            

def search_client(user_name):
    for i in range(0,len(active_clients)):
        if active_clients[i][0] == user_name:
            client = active_clients[i][1]
            break
        else:
            continue
    return(client)
# Function to send message to a single client
def send_message_to_client(user_name, message):
    print('send_message_to_client')
    
    for i in range(0,len(active_clients)):
        if active_clients[i][0] == user_name:
            client = active_clients[i][1]
            break
        else:
            continue
    m='message'
    client.send(m.encode('utf-8'))
    client.send(message.encode())

# Function to send any new message to all the clients that
# are currently connected to this server
def send_messages_to_all(message):
    
    for user in active_clients:
         
            send_message_to_client(user[0], message)

def send_message_to_client_1(user_name, message):
    print('send_message_to_client_1')
    
    for i in range(0,len(active_clients)):
        if active_clients[i][0] == user_name:
            client = active_clients[i][1]
            break
        else:
            continue
    m='screen-sharing'
    client.send(m.encode('utf-8'))
    client.send(message.encode())

# Function to send any new message to all the clients that
# are currently connected to this server
def send_messages_to_all_1(message,client):
    
    for user in active_clients:
        if user[1] != client:
            send_message_to_client_1(user[0], message)

def send_document_to_all(file_name,x):
    
    for user in active_clients:
        if user[1]!=x:
            user[1].send('document'.encode('utf-8'))
            user[1].send(file_name.encode('utf-8'))
            time.sleep(1)
            with open(file_name, 'r') as fp:
                while True:    
                    data = fp.read()
                    if not data:
                        user[1].send('`'.encode(FORMAT))
                        break
                    user[1].send(data.encode(FORMAT))
            fp.close()
            
def send_document_to_client(user_name,file_name):
    for i in range(0,len(active_clients)):
        if active_clients[i][0] == user_name:
            client = active_clients[i][1]
            print('yes found the user')
            break
        else:
            continue
    client.send('document'.encode('utf-8'))
    client.send(file_name.encode('utf-8'))
    with open(file_name, 'r') as fp:
                while True:    
                    data = fp.read()
                    if not data:
                        client.send('`'.encode(FORMAT))
                        break
                    client.send(data.encode(FORMAT))
    fp.close()
# Function to handle client
def client_handler(client):
    
    # Server will listen for client message that will
    # Contain the username
    

        username = client.recv(2048).decode('utf-8')
        if username != '':
            active_clients.append((username,client))
            prompt_message = "SERVER~" + f"{username} joined"
            send_messages_to_all(prompt_message)
            
        else:
            print("Client username is empty")

        threading.Thread(target=listen_for_messages, args=(client, username, )).start()

# Main function
def main():
    global host_ip
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Creating a try catch block
    try:
        # Provide the server with an address in the form of
        # host IP and port
        server.bind((host_ip, PORT))
        print(f"Running the server on {HOST} {PORT}")
    except:
        print(f"Unable to bind to host {HOST} and port {PORT}")

    # Set server limit
    server.listen()

    # This while loop will keep listening to client connections
    while 1:
        
        client, address = server.accept()
        print(f"Connection Succesfull {client} {address}")

        threading.Thread(target=client_handler, args=(client, )).start()

if __name__ == '__main__':
    main()
