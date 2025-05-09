import socket
import json
from threading import Thread, Lock
from JJK_Game.battle_manager import BattleManager
from JJK_Game.character_factory import CharacterFactory

HOST = 'localhost'
PORT = 5555
MAX_PLAYERS = 5


class GameServer:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen(MAX_PLAYERS)

        self.clients = []
        self.client_threads = []
        self.messages = []
        self.player_names = {}
        self.lock = Lock()

        self.available_characters = [
            CharacterFactory().create_character(c)
            for c in ['Gojo', 'Megumi', 'Nanami', 'Nobara', 'Sukuna']
        ]
        self.battle_manager = BattleManager(self.available_characters)
        self.game_started = False

    def start(self):
        print(f"[Server] Listening on {HOST}:{PORT}...")
        Thread(target=self.accept_clients, daemon=True).start()

        while not self.game_started:
            with self.lock:
                for msg in list(self.messages):
                    if msg.get("type") == "start":
                        self.game_started = True
                        self.messages.remove(msg)
                        break

        self.broadcast({"type": "status", "msg": "Game is starting..."})
        self.handle_character_selection()
        self.run_battle()

    def accept_clients(self):
        print(f"[Server] Accepting up to {MAX_PLAYERS} players...")

        while len(self.clients) < MAX_PLAYERS:
            client_socket, _ = self.server_socket.accept()
            self.clients.append(client_socket)
            thread = Thread(target=self.handle_client, args=(client_socket,), daemon=True)
            self.client_threads.append(thread)
            thread.start()

    def handle_client(self, client_socket):
        buffer = b''
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                buffer += data

                while b'\n' in buffer:
                    line, _, buffer = buffer.partition(b'\n')
                    msg = json.loads(line)

                    if msg.get("type") == "join":
                        self.player_names[client_socket] = msg["player_name"]
                        print(f"[Server] Player joined: {msg['player_name']}")
                        continue

                    msg["__client"] = client_socket
                    with self.lock:
                        self.messages.append(msg)

            except Exception as e:
                print(f"[Server] Client disconnected: {self.player_names.get(client_socket, client_socket)}")
                break

    def send_json(self, sock, data):
        try:
            sock.sendall(json.dumps(data).encode() + b'\n')
        except:
            pass

    def broadcast(self, message):
        for client in self.clients:
            self.send_json(client, message)

    def wait_for_message(self, client_socket, expected_type):
        while True:
            with self.lock:
                for msg in list(self.messages):
                    if msg.get("type") == expected_type and msg["__client"] == client_socket:
                        self.messages.remove(msg)
                        return msg

    def handle_character_selection(self):
        for client in self.clients:
            descriptions = [{'name': c.name, 'description': c.get_description()} for c in self.available_characters]
            self.send_json(client, {
                'type': 'character_selection',
                'descriptions': descriptions,
            })

            msg = self.wait_for_message(client, 'character_choice')
            char_name = msg['character']
            chosen = self.battle_manager.assign_character(char_name)
            print(f"[Server] {self.player_names[client]} selected {char_name}")

    def run_battle(self):
        self.battle_manager.start_battle()

        while not self.battle_manager.is_battle_over():
            player = self.battle_manager.get_current_player()
            if not player:
                break
            client = self.clients[self.battle_manager._BattleManager__players.index(player)]

            if self.battle_manager.handle_status_effects(player):
                self.battle_manager.advance_turn()
                continue

            self.send_json(client, {'type': 'action_selection'})
            action_msg = self.wait_for_message(client, 'action')
            action = action_msg['action']

            target = None
            if action in ('attack', 'special'):
                targets = self.battle_manager.get_alive_targets(exclude=player)
                self.send_json(client, {
                    'type': 'target_selection',
                    'targets': targets
                })
                target_msg = self.wait_for_message(client, 'target')
                target = self.battle_manager.get_target_by_name(target_msg['target'])

            self.battle_manager.apply_action(player, action, target)
            self.battle_manager.advance_turn()
            self.broadcast_state()

        self.broadcast({
            'type': 'battle_over',
            'winner': self.battle_manager.get_winner()
        })

    def broadcast_state(self):
        self.broadcast({
            'type': 'game_state',
            'state': self.battle_manager.get_battle_state()
        })