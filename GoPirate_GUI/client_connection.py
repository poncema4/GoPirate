import socket
import threading
from queue import Queue
import sys
import os

class ClientConnection:
    def __init__(self, host='localhost', port=12345):
        self.message_queue = Queue()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        self.setup_connection()
        
    def setup_connection(self):
        def receive_messages():
            while True:
                try:
                    message = self.client_socket.recv(1024).decode()
                    if message:
                        self.message_queue.put(message)
                except:
                    break
                    
        threading.Thread(target=receive_messages, daemon=True).start()
        
    def send_message(self, message):
        try:
            formatted_message = f"Client: {message}"
            self.client_socket.send(formatted_message.encode())
            self.message_queue.put(formatted_message)
        except:
            pass
            
    def get_new_messages(self):
        messages = []
        while not self.message_queue.empty():
            messages.append(self.message_queue.get())
        return messages