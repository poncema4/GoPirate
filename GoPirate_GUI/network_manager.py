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
        self.clients = {}
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
                if self.message_handler:
                    self.message_handler(message, client_id)
            except:
                break
        self.clients.pop(client_id, None)
        client_socket.close()

    def broadcast(self, message: str):
        for client in self.clients.values():
            try:
                client.send(message.encode())
            except:
                continue

    def send_to_client(self, client_id: int, message: str):
        if client_id in self.clients:
            try:
                self.clients[client_id].send(message.encode())
            except:
                pass

    def run(self):
        while True:
            client_socket, _ = self.server_socket.accept()
            self.client_count += 1
            self.clients[self.client_count] = client_socket
            
            # Send available characters to new client
            welcome_msg = "Welcome! Choose your character (1-5):\n1. Gojo\n2. Sukuna\n3. Megumi\n4. Nanami\n5. Nobara"
            client_socket.send(welcome_msg.encode())
            
            thread = threading.Thread(target=self.handle_client, 
                                   args=(client_socket, self.client_count))
            thread.daemon = True
            thread.start()