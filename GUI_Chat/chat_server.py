import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

# Shared list - store the messages
chat_messages = []
lock = threading.Lock() # lock for thread-safe access to chat_messages

# Create a server socket (TCP)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 12345))
server_socket.listen(1)

clients = [] # 3 list - keep track of number of players

# Handle communcation - client
def broadcast(message, sender=None):
    """Broadcast message to all clients except sender."""
    with lock:
        for client in clients:
            if client != sender:
                client.sendall(message.encode())

def handle_client(conn, addr):
    while True:
        try:
            message = conn.recv(1024).decode()
            if not message:
                break
            with lock:
                chat_messages.append(message) 
            update_chat_window()
            broadcast(message, conn)
        except:
            break
    if conn in clients:
        clients.remove(conn)
    conn.close()

# Accept new client connection
def accept_connections():
    while True:
        conn, addr = server_socket.accept()
        clients.append(conn)
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

# Send a message
def send_message():
    message = input_field.get()
    if message:
        formatted_message = f"server: {message}"
        with lock:
            chat_messages.append(formatted_message)
        update_chat_window()
        broadcast(formatted_message)
        input_field.delete(0, tk.END) # Clears the input field after sending

# Update chat window
def update_chat_window():
    chat_display.config(state=tk.NORMAL)
    chat_display.delete(1.0, tk.END)
    with lock:
        for message in chat_messages:
            chat_display.insert(tk.END, message + "\n")
    chat_display.config(state=tk.DISABLED)

# GUI setup
root = tk.Tk()
root.title("Chat Server")

# Scrollable text
chat_display = scrolledtext.ScrolledText(root, state=tk.DISABLED, width=50, height=30)
chat_display.pack(padx=10, pady=10)

# Input field for sending messages
input_field = tk.Entry(root, width=40)
input_field.pack(side = tk.LEFT, padx=(10, 0), pady=(0, 5))

if __name__ == "__main__":
    # Start the server thread
    threading.Thread(target=accept_connections, daemon=True).start()

    # Send button
    send_button = tk.Button(root, text="Send", command=send_message)
    send_button.pack(side=tk.LEFT, padx=(5, 10), pady=(0, 5))

    # Start the GUI main loop
    root.mainloop()
    # Close the server socket when the GUI is closed
    server_socket.close()