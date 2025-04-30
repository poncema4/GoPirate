import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from typing import List

client_message: List[str] = []
lock = threading.Lock()

# Connect with the server
client_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 12345))

def receive_msg() -> None:
    """Receive messages from the server and update the chat window."""
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            with lock:
                client_message.append(message)
            update_chat_window()
        except:
            break

def send_message() -> None:
    """Send a message to the server."""
    message = input_field.get()
    if message:
        formatted_message = f"client: {message}"
        client_socket.sendall(formatted_message.encode())
        with lock:
            client_message.append(formatted_message)
        update_chat_window()
        input_field.delete(0, tk.END)

def update_chat_window() -> None:
    """Update the chat window with the latest messages."""
    chat_display.config(state=tk.NORMAL)
    chat_display.delete(1.0, tk.END)  # Clear the chat display
    with lock:
        for message in client_message:
            chat_display.insert(tk.END, message + "\n")
    chat_display.config(state=tk.DISABLED)  # Make it read-only again

# GUI setup
root = tk.Tk()
root.title("Chat Client")

# Scrollable text
chat_display = scrolledtext.ScrolledText(root, state=tk.DISABLED, width=50, height=30)
chat_display.pack(padx=10, pady=10)

# Input field for sending messages
input_field = tk.Entry(root, width=40)
input_field.pack(side = tk.LEFT, padx=(10, 0), pady=(0, 5))

if __name__ == "__main__":
    # Start the thread to receive messages from the server
    threading.Thread(target=receive_msg, daemon=True).start()

    # Button to send messages
    send_button = tk.Button(root, text="Send", command=send_message)
    send_button.pack(side=tk.LEFT, padx=(5, 10), pady=(0, 5))

    root.mainloop()