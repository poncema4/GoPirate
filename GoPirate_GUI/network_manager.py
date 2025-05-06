import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import socket
import threading
from typing import Dict, Set
import json
from JJK_Game.battle_manager import BattleManager
from JJK_Game.character_factory import CharacterFactory

class NetworkManager:
    def __init__(self, host='localhost', port=12345):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        self.clients = {}  # {client_socket: client_name}
        self.client_count = 0
        self.message_handler = None

    def set_message_handler(self, handler):
        self.message_handler = handler

    def handle_client(self, client_socket: socket.socket, client_id: int):
        while True:
            try:
                message = client_socket.recv(1024).decode()
                if not message:
                    break

                # Handle JOIN messages specifically
                if message.startswith('JOIN:'):
                    client_name = message[5:]
                    self.clients[client_socket] = client_name
                    join_msg = f"System: {client_name} has joined the chat"
                    self.broadcast(join_msg)
                else:
                    # Broadcast regular chat messages
                    self.broadcast(message)

            except:
                break

        # Clean up when client disconnects
        if client_socket in self.clients:
            client_name = self.clients[client_socket]
            leave_msg = f"System: {client_name} has left the chat"
            del self.clients[client_socket]
            self.broadcast(leave_msg)
        client_socket.close()

    def broadcast(self, message: str):
        for client in self.clients:
            try:
                if isinstance(message, dict):
                    # Handle JSON messages
                    client.send((json.dumps(message) + '\n').encode())
                else:
                    # Handle plain text messages
                    client.send(message.encode())
            except:
                continue

    def run(self):
        while True:
            client_socket, _ = self.server_socket.accept()
            self.client_count += 1
            
            thread = threading.Thread(target=self.handle_client, 
                                   args=(client_socket, self.client_count))
            thread.daemon = True
            thread.start()