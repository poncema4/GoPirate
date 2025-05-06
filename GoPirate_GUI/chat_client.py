import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import socket
import threading
import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Chat_Bot.chat_bot import Chatbot
from JJK_Game.battle_manager import BattleManager
from JJK_Game.character_factory import CharacterFactory, Character
from typing import Optional

class UnifiedClient:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GoPirate Client")
        self.game_manager = None
        self.game_started = False
        self.players = []
        
        # Network setup
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.player_name = None
        self.username = None
        self.connected_players = set()
        self.in_game = False  # Track if game is in progress
        
        # Main container using grid
        self.setup_layout()
        self.setup_game_panel()
        self.setup_chatbot_panel()
        self.setup_multiplayer_chat()
        self.setup_text_tags()
        self.start_button.configure(state='disabled')  # Initially disable start button
        
        # Start message receiver
        self.receiver_thread = None
        self.combat_action = None
        self.current_turn = 0
        self.in_character_selection = False
        self.selected_chars = []
        self.available_chars = []
        self.battle_started = False
        
        # Add character selection tracking
        self.character_selection_order = []
        self.selected_characters = {}
        self.my_character = None  # Track this client's selected character
        self.selected_characters = {}  # Map of player names to their chosen characters
        self.character_selection_order = []  # Track selection order
        self.available_characters = []  # List of characters still available

    def setup_layout(self):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=2)
        self.root.grid_columnconfigure(1, weight=1)
        
        # Left panel for game and chatbot
        self.left_panel = ttk.Frame(self.root)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.left_panel.grid_rowconfigure(0, weight=2)
        self.left_panel.grid_rowconfigure(1, weight=1)
        
        # Right panel for multiplayer chat
        self.right_panel = ttk.Frame(self.root)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
    def setup_game_panel(self):
        game_frame = ttk.LabelFrame(self.left_panel, text="JJK Game")
        game_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Make game display read-only
        self.game_display = scrolledtext.ScrolledText(game_frame, state='disabled')
        self.game_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        controls_frame = ttk.Frame(game_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.start_button = ttk.Button(controls_frame, text="Start Game", command=self.start_game)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # Add buttons for game actions
        self.attack_button = ttk.Button(controls_frame, text="Attack", command=self.handle_attack, state='disabled')
        self.attack_button.pack(side=tk.LEFT, padx=5)
        
        self.defend_button = ttk.Button(controls_frame, text="Defend", command=self.handle_defend, state='disabled')
        self.defend_button.pack(side=tk.LEFT, padx=5)
        
        self.special_button = ttk.Button(controls_frame, text="Special", command=self.handle_special, state='disabled')
        self.special_button.pack(side=tk.LEFT, padx=5)
        
        self.game_input = ttk.Entry(controls_frame)
        self.game_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.game_input.bind('<Return>', self.handle_game_input)

    def setup_chatbot_panel(self):
        chatbot_frame = ttk.LabelFrame(self.left_panel, text="Customer Service Bot")
        chatbot_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Initialize chatbot
        self.chatbot = Chatbot()
        
        # Make chatbot display read-only
        self.chatbot_display = scrolledtext.ScrolledText(chatbot_frame, height=10, state='disabled')
        self.chatbot_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Input frame for better organization
        input_frame = ttk.Frame(chatbot_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Input entry with Send button
        self.chatbot_input = ttk.Entry(input_frame)
        self.chatbot_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.chatbot_input.bind('<Return>', self.handle_chatbot_input)
        
        send_button = ttk.Button(input_frame, text="Send", command=lambda: self.handle_chatbot_input(None))
        send_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Add welcome message to match terminal version
        self.chatbot_display.configure(state='normal')
        welcome_msg = "Welcome to the PirateEase Chatbot!\nType 'bye' to exit or 'help' for assistance.\n\n"
        self.chatbot_display.insert(tk.END, welcome_msg, 'bot')
        self.chatbot_display.configure(state='disabled')

    def setup_multiplayer_chat(self):
        chat_frame = ttk.LabelFrame(self.right_panel, text="Player Chat")
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Make chat display read-only
        self.chat_display = scrolledtext.ScrolledText(chat_frame, state='disabled')
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure tags for different message types - make self messages green
        self.chat_display.tag_configure('self', foreground='green')
        self.chat_display.tag_configure('other', foreground='blue')
        self.chat_display.tag_configure('system', foreground='red')
        
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.chat_input = ttk.Entry(input_frame)
        self.chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.chat_input.bind('<Return>', self.handle_chat_input)
        
        send_button = ttk.Button(input_frame, text="Send", command=lambda: self.handle_chat_input(None))
        send_button.pack(side=tk.RIGHT, padx=(5, 0))

    def connect_to_server(self, host='localhost', port=12345):
        try:
            self.client_socket.connect((host, port))
            self.player_name = self.get_player_name()
            self.username = self.player_name
            
            # Send player name to server for registration
            self.client_socket.send(f"JOIN:{self.player_name}".encode())
            
            # Start receiver thread
            self.receiver_thread = threading.Thread(target=self.receive_messages, daemon=True)
            self.receiver_thread.start()
            
            # Enable start button if enough players
            self.update_start_button()
            return True
            
        except ConnectionRefusedError:
            self.show_error("Could not connect to server. Make sure server is running.")
            return False
        except Exception as e:
            self.show_error(f"Connection error: {str(e)}")
            return False

    def get_player_name(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Enter Name")
        dialog.transient(self.root)
        dialog.grab_set()  # Make dialog modal
        
        name = None
        
        # Center the dialog
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        
        label = ttk.Label(dialog, text="Enter your name:")
        label.pack(pady=10)
        
        name_var = tk.StringVar()
        entry = ttk.Entry(dialog, textvariable=name_var)
        entry.pack(padx=20, pady=10)
        entry.focus()
        
        def submit():
            nonlocal name
            if name_var.get().strip():
                name = name_var.get().strip()
                dialog.destroy()
        
        def on_enter(event):
            submit()
        
        entry.bind('<Return>', on_enter)
        
        ttk.Button(dialog, text="Join", command=submit).pack(pady=10)
        
        # Wait for dialog
        dialog.wait_window()
        return name or "Player"  # Return "Player" if no name entered

    def send_message(self, message: dict):
        try:
            # Add newline to separate messages
            data = json.dumps(message) + '\n'
            self.client_socket.send(data.encode())
        except Exception as e:
            self.show_error(f"Failed to send message: {str(e)}")

    def setup_text_tags(self):
        self.chat_display.tag_configure('system', foreground='red', justify='center')
        self.chat_display.tag_configure('chat', foreground='blue')
        self.chat_display.tag_configure('self', foreground='green')  # Changed to green
        self.chatbot_display.tag_configure('bot', foreground='blue')
        self.chatbot_display.tag_configure('user', foreground='green')

    def start_game_session(self, players):
        self.players = players
        character_names = ['Gojo', 'Sukuna', 'Megumi', 'Nanami', 'Nobara']
        factory = CharacterFactory()
        available_characters = [factory.create_character(name) for name in character_names]
        
        self.game_manager = BattleManager(available_characters)
        self.game_started = True
        
        # Enable game controls
        self.attack_button.configure(state='normal')
        self.defend_button.configure(state='normal')
        self.special_button.configure(state='normal')
        
        # Update game display
        self.write_to_game(f"Game started with players: {', '.join(players)}\n")
        self.write_to_game("Choose your character:\n")
        for i, char in enumerate(available_characters, 1):
            self.write_to_game(f"{i}: {char.get_description()}\n")

    def write_to_game(self, message: str):
        self.game_display.configure(state='normal')
        self.game_display.insert(tk.END, message)
        self.game_display.configure(state='disabled')
        self.game_display.see(tk.END)

    def handle_attack(self):
        if not self.game_started:
            return
        # Send attack action to server
        self.send_message({
            'type': 'game_action',
            'action': 'attack'
        })

    def handle_defend(self):
        if not self.game_started:
            return
        # Send defend action to server
        self.send_message({
            'type': 'game_action',
            'action': 'defend'
        })

    def handle_special(self):
        if not self.game_started:
            return
        # Send special action to server
        self.send_message({
            'type': 'game_action',
            'action': 'special'
        })

    def handle_game_input(self, event):
        if not self.game_started:
            return
            
        command = self.game_input.get().strip()
        self.game_input.delete(0, tk.END)
        
        if not command:
            return
            
        try:
            choice = int(command)
            if self.in_character_selection and not self.my_character:
                # Only allow selection if player hasn't chosen yet
                if 1 <= choice <= len(self.available_chars):
                    chosen = self.available_chars[choice - 1]
                    self.my_character = chosen
                    self.write_to_game(f"\nYou selected {chosen.name}")
                    
                    # Send selection to server
                    self.send_message({
                        'type': 'select_char',
                        'player': self.player_name,
                        'choice': choice
                    })
                    # Disable input until battle starts
                    self.game_input.configure(state='disabled')
            
            elif self.battle_started and self.is_players_turn():
                if self.combat_action:
                    if self.combat_action == "defend":
                        # Defense doesn't need a target
                        self.send_message({
                            'type': 'combat',
                            'action': 'defend',
                            'player': self.player_name
                        })
                        self.combat_action = None
                        self.game_input.configure(state='disabled')
                    else:
                        # Attack and Special need valid target
                        targets = [c for p, c in self.selected_characters.items() 
                                if p != self.player_name and c.is_alive()]
                        if 1 <= choice <= len(targets):
                            target = targets[choice - 1]
                            self.send_message({
                                'type': 'combat',
                                'action': self.combat_action,
                                'player': self.player_name,
                                'target': target.name
                            })
                            self.combat_action = None
                            self.game_input.configure(state='disabled')
                        else:
                            self.write_to_game("\nInvalid target number!")

        except ValueError:
            # Handle action commands only during battle and player's turn
            cmd = command.lower()
            if cmd in ['attack', 'defend', 'special'] and self.battle_started and self.is_players_turn():
                if cmd == 'defend':
                    self.handle_defend()
                else:
                    self.combat_action = cmd
                    targets = [c for p, c in self.selected_characters.items() 
                             if p != self.player_name and c.is_alive()]
                    self.write_to_game("\nAvailable targets:")
                    for i, target in enumerate(targets, 1):
                        self.write_to_game(f"\n{i}: {target.name} (HP: {target.hp})")
                    self.write_to_game("\nEnter target number: ")

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                if not message:
                    break

                if message.startswith('System:'):
                    if 'has joined' in message:
                        player = message.split(':')[1].split('has joined')[0].strip()
                        self.connected_players.add(player)
                        self.update_start_button()
                    elif 'has left' in message:
                        player = message.split(':')[1].split('has left')[0].strip()
                        self.connected_players.discard(player)
                        self.update_start_button()
                    self.handle_system_message(message)
                else:
                    try:
                        data = json.loads(message)
                        self.handle_game_message(data)
                    except json.JSONDecodeError:
                        sender, content = message.split(':', 1)
                        self.handle_chat_message(sender.strip(), content.strip())

            except ConnectionResetError:
                self.handle_disconnect()
                break

    def handle_disconnect(self):
        """Handle client disconnection"""
        self.chat_display.configure(state='normal')
        self.chat_display.insert(tk.END, "*** Connection to server lost ***\n", 'system')
        self.chat_display.configure(state='disabled')
        self.game_started = False
        self.connected_players.clear()
        self.update_start_button()  # Re-check start button state
        # Disable game controls
        self.attack_button.configure(state='disabled')
        self.defend_button.configure(state='disabled')
        self.special_button.configure(state='disabled')
        self.game_input.configure(state='disabled')

    def handle_game_action(self, player: str, action: str):
        try:
            action_num = int(action)
            if not self.game_manager:
                return
                
            # Character selection phase
            if len(self.game_manager._BattleManager__players) < len(self.connected_players):
                if 1 <= action_num <= len(self.game_manager._BattleManager__available_players):
                    chosen = self.game_manager._BattleManager__available_players[action_num - 1]
                    self.game_manager._BattleManager__players.append(chosen)
                    self.write_to_game(f"\n{player} selected {chosen.name}\n")
                    
                    # Start battle once all players have chosen
                    if len(self.game_manager._BattleManager__players) == len(self.connected_players):
                        self.broadcast_game_state("battle_start")
                        self.start_battle()

            # Combat phase
            else:
                current_player = self.game_manager._BattleManager__players[self.game_manager._BattleManager__turn % len(self.game_manager._BattleManager__players)]
                if current_player and player == self.player_name:
                    target_idx = action_num - 1
                    if 0 <= target_idx < len(self.game_manager._BattleManager__players):
                        target = self.game_manager._BattleManager__players[target_idx]
                        self.process_combat_action(current_player, target)
                        self.broadcast_game_state("turn_end")
                        
        except ValueError:
            # Handle non-numeric game inputs
            if action.lower() in ["attack", "defend", "special"]:
                if player == self.get_current_player():
                    self.queue_combat_action(action.lower())

    def broadcast_game_state(self, state_type: str):
        game_state = {
            'type': 'game_state',
            'state': state_type,
            'players': [p.name for p in self.game_manager._BattleManager__players],
            'current_turn': self.game_manager._BattleManager__turn,
            'hp_values': [p.hp for p in self.game_manager._BattleManager__players]
        }
        self.send_message(game_state)

    def get_current_player(self) -> str:
        if not self.game_manager or not self.game_manager._BattleManager__players:
            return ""
        current_idx = self.game_manager._BattleManager__turn % len(self.game_manager._BattleManager__players)
        return self.game_manager._BattleManager__players[current_idx].name

    def queue_combat_action(self, action: str):
        self.combat_action = action
        self.write_to_game(f"\nSelect target (1-{len(self.game_manager._BattleManager__players)}): ")

    def process_combat_action(self, attacker: Character, target: Character):
        if self.combat_action == "attack":
            attacker.attack(target)
        elif self.combat_action == "defend":
            attacker.defend()
        elif self.combat_action == "special":
            attacker.special([target], self.game_manager._BattleManager__turn)
        self.combat_action = None
        self.next_turn()

    def handle_chat_message(self, sender: str, content: str):
        self.chat_display.configure(state='normal')
        if sender == self.player_name:
            self.chat_display.insert(tk.END, f"You: {content}\n", 'self')
        else:
            self.chat_display.insert(tk.END, f"{sender}: {content}\n", 'other')
        self.chat_display.configure(state='disabled')
        self.chat_display.see(tk.END)

    def handle_system_message(self, message: str):
        self.chat_display.configure(state='normal')
        self.chat_display.insert(tk.END, f"{message}\n", 'system')
        self.chat_display.configure(state='disabled')
        self.chat_display.see(tk.END)

    def handle_game_state(self, state_data: dict):
        if state_data['type'] == 'game_start':
            if not self.game_started:
                self.start_game()
        
        elif state_data['type'] == 'character_selected':
            player = state_data['player']
            char_name = state_data['character']
            self.write_to_game(f"\n{player} selected {char_name}")
            
            if state_data.get('battle_start'):
                self.in_character_selection = False
                self.start_battle()
                
        elif state_data['type'] == 'combat_action':
            self.handle_combat_action(state_data)
            
    def handle_combat_action(self, action_data: dict):
        if not self.game_manager:
            return
            
        attacker = self.get_player_by_name(action_data['player'])
        if not attacker:
            return
            
        action = action_data['action']
        if action == 'defend':
            attacker.defend()
            self.write_to_game(f"\n{attacker.name} defends!")
        else:
            target = self.get_player_by_name(action_data['target'])
            if not target:
                return
                
            if action == 'attack':
                attacker.attack(target)
            elif action == 'special':
                attacker.special([target], self.current_turn)
                
        self.current_turn += 1
        self.update_game_display()

    def handle_chat_input(self, event):
        message = self.chat_input.get().strip()
        if message:
            try:
                # Send message to server
                self.client_socket.send(f"{self.player_name}: {message}".encode())
                
                # Clear input
                self.chat_input.delete(0, tk.END)
            except Exception as e:
                self.show_error(f"Failed to send message: {str(e)}")

    def is_players_turn(self) -> bool:
        if not self.game_manager or not self.game_manager._BattleManager__players:
            return False
        current_player = self.game_manager._BattleManager__players[self.current_turn % len(self.game_manager._BattleManager__players)]
        return current_player.name == self.player_name

    def get_player_by_name(self, name: str) -> Optional[Character]:
        if not self.game_manager:
            return None
        for player in self.game_manager._BattleManager__players:
            if player.name == name:
                return player
        return None

    def update_game_display(self):
        if not self.game_manager:
            return
            
        self.write_to_game("\nCurrent Status:\n")
        for player in self.game_manager._BattleManager__players:
            self.write_to_game(f"{player.name}: {player.hp} HP\n")
            
        current_player = self.game_manager._BattleManager__players[self.current_turn % len(self.game_manager._BattleManager__players)]
        self.write_to_game(f"\n{current_player.name}'s turn!\n")

    def start_battle(self):
        self.write_to_game("\nBattle begins!\n")
        self.attack_button.configure(state='normal')
        self.defend_button.configure(state='normal') 
        self.special_button.configure(state='normal')
        self.update_game_display()

    def add_chat_message(self, sender: str, content: str, is_self: bool = False):
        self.chat_display.configure(state='normal')
        tag = 'self' if is_self else 'chat'
        self.chat_display.insert(tk.END, f"{sender}: {content}\n", tag)
        self.chat_display.configure(state='disabled')
        self.chat_display.see(tk.END)

    def add_system_message(self, message: str):
        self.chat_display.configure(state='normal')
        self.chat_display.insert(tk.END, f"*** {message} ***\n", 'system')
        self.chat_display.configure(state='disabled')
        self.chat_display.see(tk.END)

    def show_error(self, message: str):
        tk.messagebox.showerror("Error", message)

    def handle_chatbot_input(self, event):
        message = self.chatbot_input.get().strip()
        if message:
            # Clear input first
            self.chatbot_input.delete(0, tk.END)
            
            if message.lower() == 'bye':
                # Handle bye message
                self.chatbot_display.configure(state='normal')
                self.chatbot_display.insert(tk.END, f"You: {message}\n", 'user')
                self.chatbot_display.insert(tk.END, "Bot: Goodbye!\n\n", 'bot')
                self.chatbot_display.configure(state='disabled')
                return
                
            elif message.lower() == 'help':
                # Handle help message
                self.chatbot_display.configure(state='normal')
                self.chatbot_display.insert(tk.END, f"You: {message}\n", 'user')
                help_msg = "Bot: You can ask me about your order status, refund requests, product availability, or connect you to a live agent.\n\n"
                self.chatbot_display.insert(tk.END, help_msg, 'bot')
                self.chatbot_display.configure(state='disabled')
                return
            
            # Display user message
            self.chatbot_display.configure(state='normal')
            self.chatbot_display.insert(tk.END, f"You: {message}\n", 'user')
            
            try:
                # Get chatbot response 
                response = self.chatbot.process_query(message)
                
                # Display bot response
                self.chatbot_display.insert(tk.END, f"Bot: {response}\n\n", 'bot')
                
            except Exception as e:
                print(f"Chatbot error: {str(e)}")
                self.chatbot_display.insert(tk.END, "Bot: I apologize, but I'm having trouble processing your request. Please try again.\n\n", 'bot')
            
            self.chatbot_display.configure(state='disabled')
            self.chatbot_display.see(tk.END)

    def start_game(self):
        """Start the game if enough players are connected"""
        if len(self.connected_players) < 2 or len(self.connected_players) > 5:
            self.show_error("Need 2-5 players to start")
            return
            
        # Disable start button once game begins
        self.start_button.configure(state='disabled')
        self.game_started = True
        self.in_character_selection = True
        
        # Initialize game components
        character_names = ['Gojo', 'Sukuna', 'Megumi', 'Nanami', 'Nobara']
        factory = CharacterFactory()
        self.available_chars = [factory.create_character(name) for name in character_names]
        self.selected_chars = []
        self.character_selection_order = []
        
        # Start character selection phase
        self.send_message({
            'type': 'game_start',
            'players': list(self.connected_players)
        })

        # Show character selection UI
        self.write_to_game("\nTime to show what real Jujutsu really is...\n")
        self.write_to_game("\nChoose your character:\n")
        for i, char in enumerate(self.available_chars, 1):
            self.write_to_game(f"{i}: {char.get_description()}\n")

    def handle_character_selection(self, data: dict):
        player = data['player']
        char_idx = data['choice'] - 1
        
        if char_idx < 0 or char_idx >= len(self.available_characters):
            return
            
        chosen = self.available_characters[char_idx]
        self.selected_characters[player] = chosen
        self.character_selection_order.append(player)
        self.write_to_game(f"\n{player} selected {chosen.name}")
        
        # Start battle when all players have chosen
        if len(self.selected_characters) == len(self.connected_players):
            self.start_battle_phase()

    def start_battle_phase(self):
        self.in_character_selection = False
        self.current_turn = 0
        
        # Set up players in selection order
        self.game_manager._BattleManager__players = [
            self.selected_characters[player] for player in self.character_selection_order
        ]
        
        # Enable combat controls if it's player's turn
        if self.is_players_turn():
            self.enable_combat_controls()
            
        self.update_game_display()

    def enable_combat_controls(self):
        self.attack_button.configure(state='normal')
        self.defend_button.configure(state='normal')
        self.special_button.configure(state='normal')
        self.game_input.configure(state='normal')

    def update_start_button(self):
        """Enable start button only if enough players are connected and game hasn't started"""
        if len(self.connected_players) >= 2 and not self.game_started:
            self.start_button.configure(state='normal')
        else:
            self.start_button.configure(state='disabled')

    def run(self):
        if self.connect_to_server():
            self.root.mainloop()
        else:
            tk.messagebox.showerror("Error", "Could not connect to server")
            self.root.destroy()

    def handle_game_message(self, data: dict):
        """Handle incoming game messages"""
        msg_type = data.get('type')
        if msg_type == 'game_start':
            self.init_game()
        elif msg_type == 'char_select':
            # Handle another player's character selection
            player = data['player']
            char_idx = data['choice']
            if player != self.player_name:  # Only process others' selections
                self.handle_char_select(player, char_idx)
        elif msg_type == 'battle_start':
            self.start_battle_phase()
        elif msg_type == 'combat':
            self.handle_combat_update(data)
        elif msg_type == 'game_over':
            self.handle_game_over(data['winner'])

    def init_game(self):
        """Initialize game state"""
        if not self.game_started:
            self.game_started = True
            self.in_character_selection = True
            
            # Match JJK_Game setup
            character_names = ['Gojo', 'Sukuna', 'Megumi', 'Nanami', 'Nobara']
            factory = CharacterFactory()
            self.available_chars = [factory.create_character(name) for name in character_names]
            self.game_manager = BattleManager(self.available_chars)
            
            # Show character selection
            self.write_to_game("\nTime to show what real Jujutsu really is...\n")
            self.write_to_game("Choose your character:\n")
            for i, char in enumerate(self.available_chars, 1):
                self.write_to_game(f"{i}: {char.get_description()}\n")

    def handle_char_select(self, player: str, choice: int):
        """Handle character selection"""
        if not 0 <= choice < len(self.available_chars):
            return
            
        # Get character without removing yet
        char = self.available_chars[choice]
        
        # Only remove if not already taken
        if char not in self.selected_chars:
            self.available_chars.pop(choice)
            self.selected_chars.append(char)
            self.selected_characters[player] = char
            if player not in self.character_selection_order:
                self.character_selection_order.append(player)
            
            # Different messages for self vs other players
            if player == self.player_name:
                self.write_to_game(f"\nYou selected {char.name}")
            else:
                self.write_to_game(f"\n{player} has chosen {char.name}")
            
            # Start battle when all players have chosen
            if len(self.selected_characters) == len(self.connected_players):
                self.battle_started = True
                self.start_battle_phase()
                self.enable_combat_controls()

    def start_battle_phase(self):
        """Start the battle after character selection"""
        self.in_character_selection = False
        self.battle_started = True
        self.current_turn = 0
        
        # Initialize battle manager with selected characters in order
        self.game_manager = BattleManager([char for char in self.selected_chars])
        self.game_manager._BattleManager__players = self.selected_chars
        
        # Enable controls for first player
        if self.player_name == self.character_selection_order[0]:
            self.enable_combat_controls()
            self.game_input.configure(state='normal')
        else:
            self.disable_combat_controls()
            
        self.write_to_game("\nBattle begins!\n")
        self.write_to_game("-" * 60 + "\n")
        self.update_battle_display()

    def enable_combat_controls(self):
        """Enable combat buttons for current player's turn"""
        if self.is_players_turn():
            self.attack_button.configure(state='normal')
            self.defend_button.configure(state='normal')
            self.special_button.configure(state='normal')
            self.game_input.configure(state='normal')

    def disable_combat_controls(self):
        """Disable combat buttons when not player's turn"""
        self.attack_button.configure(state='disabled')
        self.defend_button.configure(state='disabled')
        self.special_button.configure(state='disabled') 
        self.game_input.configure(state='disabled')

    def next_turn(self):
        """Advance to next player's turn"""
        self.current_turn += 1
        
        # Enable/disable controls based on whose turn it is
        if self.is_players_turn():
            self.enable_combat_controls()
        else:
            self.disable_combat_controls()
            
        self.update_battle_display()
        
        # Check for game over
        alive_players = [p for p in self.game_manager._BattleManager__players if p.is_alive()]
        if len(alive_players) == 1:
            self.handle_game_over(alive_players[0].name)

    def handle_combat_update(self, data: dict):
        """Handle combat actions and updates"""
        action = data['action']
        player = self.get_player_by_name(data['player'])
        
        if not player:
            return
            
        if action == 'attack':
            target = self.get_player_by_name(data['target'])
            if target:
                player.attack(target)
                self.write_to_game(f"\n{player.name} attacked {target.name}!")
        elif action == 'defend':
            player.defend()
            self.write_to_game(f"\n{player.name} is defending!")
        elif action == 'special':
            targets = [self.get_player_by_name(t) for t in data['targets']]
            targets = [t for t in targets if t is not None]
            if targets:
                player.special(targets, self.current_turn)
                self.write_to_game(f"\n{player.name} used their special move!")
            
        # Handle status effects and turn advancement
        player.handle_defense_boost()
        player.handle_poison()
        stunned = player.handle_stun()
        
        self.next_turn()
        if stunned:
            self.write_to_game(f"\n{player.name} is stunned and skips their turn!")
            self.next_turn()

    def update_battle_display(self):
        """Update the game display with current battle state"""
        self.write_to_game("\nCurrent Status:\n")
        self.write_to_game("-" * 60 + "\n")
        
        # Show alive players
        for player in self.game_manager._BattleManager__players:
            if player.is_alive():
                status = f"{player.name} - HP: {player.hp}"
                if player.poison.is_active():
                    status += f" (Poisoned: {player.poison.duration} turns)"
                if player.stun.is_active():
                    status += " (Stunned)"
                self.write_to_game(f" - {status}\n")
                
        # Show current turn
        current = self.game_manager._BattleManager__players[self.current_turn]
        self.write_to_game(f"\n{current.name}'s turn!\n")

    def handle_game_over(self, winner: str):
        """Handle game over state"""
        self.write_to_game(f"\n{winner} is the chosen one!\n")
        self.game_started = False
        self.battle_started = False
        self.disable_combat_controls()
        
if __name__ == "__main__":
    client = UnifiedClient()
    client.run()