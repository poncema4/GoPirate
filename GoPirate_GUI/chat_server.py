import sys
import os
sys.path.append(os.path.dirname(__file__))

import tkinter as tk
from tkinter import ttk, scrolledtext
from network_manager import NetworkManager
import threading
import socket
import json
from typing import Dict, Any

class ChatServer:
    def __init__(self, host='localhost', port=12345):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        
        self.clients = {}  # Dictionary to store client sockets and names
        self.lock = threading.Lock()
        
        # GUI Setup
        self.root = tk.Tk()
        self.root.title("Chat Server")
        self.setup_gui()
        
    def setup_gui(self):
        self.log_display = scrolledtext.ScrolledText(self.root, height=20, width=50)
        self.log_display.pack(padx=10, pady=10)
        self.log_message("Server started, waiting for connections...")
        
    def log_message(self, message):
        self.log_display.configure(state='normal')
        self.log_display.insert(tk.END, f"{message}\n")
        self.log_display.configure(state='disabled')
        self.log_display.see(tk.END)
        
    def broadcast(self, message, sender=None):
        with self.lock:
            for client in self.clients:
                if client != sender:
                    try:
                        client.send(message.encode())
                    except:
                        pass
                        
    def handle_client(self, client_socket, addr):
        while True:
            try:
                message = client_socket.recv(1024).decode()
                if not message:
                    break
                    
                if message.startswith('JOIN:'):
                    # Handle new client joining
                    client_name = message[5:]
                    self.clients[client_socket] = client_name
                    welcome_msg = f"System: {client_name} has joined the chat"
                    self.broadcast(welcome_msg, client_socket)
                    self.log_message(f"New client joined: {client_name}")
                else:
                    # Broadcast regular messages
                    self.broadcast(message, client_socket)
                    self.log_message(message)
                    
            except:
                break
                
        # Clean up disconnected client
        if client_socket in self.clients:
            client_name = self.clients[client_socket]
            del self.clients[client_socket]
            self.broadcast(f"System: {client_name} has left the chat")
            self.log_message(f"Client disconnected: {client_name}")
            
        client_socket.close()
        
    def start(self):
        # Start accepting clients in a separate thread
        threading.Thread(target=self.accept_clients, daemon=True).start()
        # Start GUI main loop
        self.root.mainloop()
        
    def accept_clients(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            threading.Thread(target=self.handle_client, 
                           args=(client_socket, addr),
                           daemon=True).start()

class UnifiedServer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GoPirate Server")
        
        # Create network manager first
        self.network_manager = NetworkManager()
        
        # Then setup UI
        self.setup_ui()
        
    def setup_ui(self):
        # Create server log display
        self.log_display = scrolledtext.ScrolledText(self.root, state='disabled', height=5, width=20)
        self.log_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add server status label
        self.status_label = ttk.Label(self.root, text="Server Running...")
        self.status_label.pack(pady=5)
        
        # Start server in separate thread
        threading.Thread(target=self.network_manager.run, daemon=True).start()
        
    def log_message(self, message: str):
        self.log_display.configure(state='normal')
        self.log_display.insert(tk.END, f"{message}\n")
        self.log_display.configure(state='disabled')
        self.log_display.see(tk.END)
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    server = UnifiedServer()
    server.run()
    chat_server = ChatServer()
    chat_server.start()