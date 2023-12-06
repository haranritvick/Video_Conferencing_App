# import required modules
import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
import time
import os
from tkinter import filedialog
from tkinter import font
import pickle
import cv2
import struct
import sys

HOST = '172.16.0.20'
PORT = 6000

#this is for screen sharing
HOST_ss= socket.gethostname()
host_ip_ss= socket.gethostbyname(HOST_ss)
print(f'{host_ip_ss}')
from vidstream import ScreenShareClient
from vidstream import StreamingServer
import threading
status = b'0'  # Example initial status byte

DARK_GREY = '#121212'
MEDIUM_GREY = '#1F1B24'
OCEAN_BLUE = '#464EB8'
WHITE = "white"
LIGHT_BLUE = "#ADD8E6"
DARK_BLUE = "#00008B"
LIGHT_GREY = "#D3D3D3"
WHITE = "#FFFFFF"
FONT = ("Helvetica", 17)
BUTTON_FONT = ("Helvetica", 15)
SMALL_FONT = ("Helvetica", 13)
FORMAT = 'utf-8'

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
data = b""
payload_size = struct.calcsize("Q")
def add_message(message):
    message_box.config(state=tk.NORMAL)
    message_box.insert(tk.END, message + '\n')
    message_box.config(state=tk.DISABLED)

def connect():

    # try except block
    try:

        # Connect to the server
        client.connect((HOST, PORT))
        print("SERVER CONNECTION SUCCESSFUL")
        add_message("[SERVER] SERVER CONNECTION SUCCESSFULL!!!")
    except:
        messagebox.showerror("Unable to connect to server", f"Unable to connect to server {HOST} {PORT}")

    username = username_textbox.get()
    if username != '':
        client.sendall(username.encode())
    else:
        messagebox.showerror("Invalid username", "Username cannot be empty")

    threading.Thread(target=listen_for_messages_from_server, args=(client, )).start()

    username_textbox.config(state=tk.DISABLED)
    username_button.config(state=tk.DISABLED)

def send_message():
    first = 'chat'
    client.send(first.encode())
    time.sleep(1) 
    
    
    message = message_textbox_1.get()
    print(f'{message}')
    
        
    if message != '':
                client.send(message.encode('utf-8'))
                message_textbox_1.delete(0, len(message))
    else:
                messagebox.showerror("Empty message", "Message cannot be empty")
                
    message = message_textbox.get()
    print(f'{message}')
    
        
    if message != '':
                client.sendall(message.encode('utf-8'))
                message_textbox.delete(0, len(message))
    else:
                messagebox.showerror("Empty message", "Message cannot be empty")

def send_documnet():
    first = 'doucment'
    client.send(first.encode())
    sending_info = message_textbox_1.get()
    message_textbox_1.delete(0, len(sending_info))
    print(f'{sending_info}')
    client.send(sending_info.encode())
    file_path = filedialog.askopenfilename()
    print("Selected File:", file_path)
    # client.send(file_path.encode('utf-8'))
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    header = f"{file_name}|{file_size}".ljust(100).encode('utf-8')
    client.send(header)
      
    if file_path:
        with open(file_path, "rb") as file:
            while True:
                file_data = file.read(1024)
                if not file_data:
                    break
                client.send(file_data)  # Send file data to the server


def function_send_frames():
    global status
    cap = cv2.VideoCapture(0)
    
    while True:
        print('...')
        ret,frame = cap.read()
        if not ret:
            break
        
        cv2.imshow('Camera', frame)
        
        data = pickle.dumps((status, frame))
        frame_size = struct.pack("L", len(data))
        
        try:
            client.send(frame_size)
            client.send(data)
        except:
            cap.release()
            cv2.destroyAllWindows()
            break
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            status=b'1'
            last_frame_data = pickle.dumps((status, frame))
            client.send(struct.pack("L", len(last_frame_data)))
            client.send(last_frame_data)
            print("Streaming stopped")
            break
    
    cap.release()
    cv2.destroyAllWindows()
        
    
    
def send_video():
    first = 'video'
    client.send(first.encode('utf-8'))
    function_send_frames()

def s_sharing():
    first = 'screen-sharing'
    client.send(first.encode())
    message = str(host_ip_ss)
    client.send(message.encode('utf-8'))
    time.sleep(5)
    IP = host_ip_ss
    PORT = 9999
    
    server = StreamingServer(IP,PORT)

            # Flag to control the while loop
    running = True

    def start_server():
                print("Server is listening...")
                server.start_server()

            # Function to stop the server and set the running flag to False
    def stop_server():
                print("Stopping the server...")
                server.stop_server()
                global running
                running = False

            # Start the server in a separate thread
    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    try:
                while running:
                    # Your frame sending code goes here
                    # For example, you can replace this line with the actual code for sending frames:
                    print("Sending frames...")

    except KeyboardInterrupt:
                print("\nServer Stopped!!!")
                stop_server()

            # Wait for the server thread to finish before exiting the program
    server_thread.join()
                # Stop the server


def send_message_all():
    first = 'chat'
    client.sendall(first.encode())
    second = 'all'
    client.sendall(second.encode())
    time.sleep(1)
    message = message_textbox.get()
    if message != '':
        client.sendall(message.encode())
        message_textbox.delete(0, len(message))
    else:
        messagebox.showerror("Empty message", "Message cannot be empty")

root = tk.Tk()
root.geometry("1050x600")
root.title("Messenger Client")
root.resizable(False, False)

custom_font = font.Font(family="Arial", size=16)

#Configuring rows weight
root.grid_rowconfigure(0, weight=0)
root.grid_rowconfigure(1, weight=0)  # Adjust the weight for middle_frame
root.grid_rowconfigure(2, weight=0)  # Adjust the weight for bottom_frame
root.grid_rowconfigure(3, weight=0)
# for i in range(4):
#     root.grid_rowconfigure(i, weight=1)
# Frames
top_frame = tk.Frame(root, width=850, height=100, bg=DARK_BLUE)
top_frame.grid(row=0, column=0, sticky=tk.NSEW)

middle_frame = tk.Frame(root, width=850, height=350, bg=DARK_BLUE)
middle_frame.grid(row=1, column=0, sticky=tk.NSEW)

bottom_frame = tk.Frame(root, width=850, height=100, bg=DARK_BLUE)
bottom_frame.grid(row=2, column=0, sticky=tk.NSEW)

next_frame = tk.Frame(root, width=850, height=100, bg=DARK_BLUE)
next_frame.grid(row=3, column=0, sticky=tk.NSEW)

# Top Frame Widgets
username_label = tk.Label(top_frame, text="Enter username:", font=custom_font, bg=DARK_BLUE, fg=WHITE)
username_label.pack(side=tk.LEFT, padx=10, pady=10)

username_textbox = tk.Entry(top_frame, font=custom_font, bg=LIGHT_GREY, fg=WHITE, width=30)
username_textbox.pack(side=tk.LEFT, padx=10, pady=10)

username_button = tk.Button(top_frame, text="Join", font=custom_font, bg=LIGHT_BLUE, fg=WHITE, command=connect)
username_button.pack(side=tk.LEFT, padx=10, pady=10)

# Bottom Frame Widgets
message_label = tk.Label(middle_frame, text="Message:", font=custom_font, bg=DARK_BLUE, fg=WHITE)
message_label.pack(side=tk.LEFT, padx=10, pady=10)

message_textbox = tk.Entry(middle_frame, font=custom_font, bg=LIGHT_GREY, fg=WHITE, width=30)
message_textbox.pack(side=tk.LEFT, padx=10, pady=10)

message_label = tk.Label(middle_frame, text="To:", font=custom_font, bg=DARK_BLUE, fg=WHITE)
message_label.pack(side=tk.LEFT, padx=10, pady=10)

message_textbox_1 = tk.Entry(middle_frame, font=custom_font, bg=LIGHT_GREY, fg=WHITE, width=30)
message_textbox_1.pack(side=tk.LEFT, padx=10, pady=10)

send_button = tk.Button(bottom_frame, text="Send", font=custom_font, bg=LIGHT_BLUE, fg=WHITE, command=send_message)
send_button.pack(side=tk.LEFT, padx=10, pady=10)

send_all_button = tk.Button(bottom_frame, text="Send All", font=custom_font, bg=LIGHT_BLUE, fg=WHITE, command=send_message_all)
send_all_button.pack(side=tk.LEFT, padx=10, pady=10)

document_button = tk.Button(bottom_frame, text="Document", font=custom_font, bg=LIGHT_BLUE, fg=WHITE, command=send_documnet)
document_button.pack(side=tk.LEFT, padx=10, pady=10)

screen_sharing = tk.Button(bottom_frame, text="Screen-share", font=custom_font, bg=LIGHT_BLUE, fg=WHITE, command=s_sharing)
screen_sharing.pack(side=tk.LEFT, padx=10, pady=10)

video_button = tk.Button(bottom_frame, text="video", font=custom_font, bg=LIGHT_BLUE, fg=WHITE, command=send_video)
video_button.pack(side=tk.LEFT, padx=10, pady=10)

# Middle Frame Widgets
message_box = scrolledtext.ScrolledText(next_frame, font=custom_font, bg='#000000', fg="#FFFFFF", width=75, height=15)
message_box.config(state=tk.DISABLED)
message_box.pack(side=tk.TOP, padx=10, pady=10)


def fuction_conference():
    print('The client is listening to the frame')
    data = b""
    payload_size = struct.calcsize("L")
    cv2.namedWindow("Receiving video", cv2.WINDOW_NORMAL)
                
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
                    
                    while len(data) < msg_size:
                        data += client.recv(4 * 1024)
                    
                    frame_data = data[:msg_size]
                    data = data[msg_size:]
                    
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
                        sys.exit(0)
                        
            
    


def listen_for_messages_from_server(client):
    
    while 1:
        
        try:
            m=client.recv(1024).decode('utf-8')
            print(f'{m}')
        except UnicodeDecodeError as e:
            # Handle the exception, such as printing an error message
            print("UnicodeDecodeError: ", e)
            break
        if m == 'message':
            while 1:
                
                message = client.recv(2048).decode('utf-8')
                if message != '':
                    username = message.split("~")[0]
                    content = message.split('~')[1]

                    add_message(f"[{username}] {content}")
                    break
                else:
                    messagebox.showerror("Error", "Message recevied from client is empty")
        elif m=='document':
            print('\nThis is a document file send by the server\n')
            header = client.recv(100).decode('utf-8')
            file_name, file_size_str = header.strip().split('|')
            file_size = int(file_size_str)
                
            file_path = filedialog.asksaveasfilename()
                                
            with open(file_path, "wb") as file:
                    bytes_received = 0
                    while bytes_received < file_size:
                        file_data = client.recv(1024)
                        if not file_data:  
                            break
                        file.write(file_data)
                        bytes_received += len(file_data)
            file.close()
            print("File received and saved successfully.")
        elif m=='video':
             print('THis is a video file send by the server')
             fuction_conference()
        elif m == 'screen-sharing':
             print('This is an screen-sharing application')
             message = client.recv(2048).decode('utf-8')
             print(f'{message}')
            
             IP = message
             PORT = 9999
             time.sleep(10)
             sender = ScreenShareClient(IP,PORT)

             t = threading.Thread(target=sender.start_stream)
             t.start()
             

             try:
                  while True:
                          continue
             except KeyboardInterrupt:
                 print("Exited!!!")

    
    
    sender.stop_server()

             
        
            

# main function
def main():
    root.mainloop()
    
if __name__ == '__main__':
    main()