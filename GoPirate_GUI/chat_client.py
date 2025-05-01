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
        
        # Start message receiver
        self.receiver_thread = None
        
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
        if not command:
            return
            
        self.game_input.delete(0, tk.END)
        
        # Send player action to all clients
        self.send_message({
            'type': 'game_action',
            'player': self.player_name,
            'action': command
        })

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                if not message:
                    break
                    
                # Try to parse as JSON first
                try:
                    data = json.loads(message)
                    
                    if data['type'] == 'game_start':
                        self.game_started = True
                        if 'players' in data:
                            self.connected_players = set(data['players'])
                        self.start_game_session(list(self.connected_players))
                    
                    elif data['type'] == 'game_action':
                        if self.game_started:
                            player = data['player']
                            action = data['action']
                            self.handle_game_action(player, action)
                            
                except json.JSONDecodeError:
                    # Handle regular chat messages
                    self.chat_display.configure(state='normal')
                    if message.startswith('System:'):
                        # Extract player name from system messages
                        if "has joined" in message:
                            player = message.split(":")[1].split("has joined")[0].strip()
                            self.connected_players.add(player)
                        elif "has left" in message:
                            player = message.split(":")[1].split("has left")[0].strip()
                            self.connected_players.discard(player)
                        self.chat_display.insert(tk.END, f"{message}\n", 'system')
                    elif ':' in message:
                        sender, content = message.split(':', 1)
                        sender = sender.strip()
                        if sender != self.player_name:
                            self.chat_display.insert(tk.END, message + "\n", 'other')
                    self.chat_display.configure(state='disabled')
                    self.chat_display.see(tk.END)
                
            except ConnectionResetError:
                self.handle_disconnect()
                break
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def handle_disconnect(self):
        """Handle client disconnection"""
        self.chat_display.configure(state='normal')
        self.chat_display.insert(tk.END, "*** Connection to server lost ***\n", 'system')
        self.chat_display.configure(state='disabled')
        self.game_started = False
        self.connected_players.clear()
        # Disable game controls
        self.attack_button.configure(state='disabled')
        self.defend_button.configure(state='disabled')
        self.special_button.configure(state='disabled')
        self.game_input.configure(state='disabled')

    def handle_game_action(self, player: str, action: str):
        """Handle game actions from any player"""
        try:
            action_num = int(action)
            if not self.game_manager:
                return
                
            # Handle character selection or target selection
            if len(self.game_manager._BattleManager__players) < len(self.connected_players):
                # Character selection phase
                if 1 <= action_num <= len(self.game_manager._BattleManager__available_players):
                    chosen = self.game_manager._BattleManager__available_players[action_num - 1]
                    self.game_manager._BattleManager__players.append(chosen)
                    self.write_to_game(f"\n{player} selected {chosen.name}")
                    
                    if len(self.game_manager._BattleManager__players) == len(self.connected_players):
                        self.start_battle()
            else:
                # Handle combat actions
                current_player = self.game_manager._BattleManager__players[self.game_manager._BattleManager__turn]
                if player == self.player_name and current_player:
                    self.process_combat_action(current_player, action)
        except ValueError:
            pass

    # Add these new helper methods
    def process_combat_action(self, player: Character, action: str):
        """Process combat actions for the current player"""
        if not self.game_started or not player:
            return
            
        if action.lower() == "attack":
            target = self.get_valid_target(player)
            if target:
                player.attack(target)
                self.next_turn()
        elif action.lower() == "defend":
            player.defend()
            self.next_turn()
        elif action.lower() == "special":
            target = self.get_valid_target(player)
            if target:
                if player.special([target], self.game_manager._BattleManager__turn):
                    self.next_turn()

    def next_turn(self):
        """Advance to next turn"""
        self.game_manager._BattleManager__turn = (self.game_manager._BattleManager__turn + 1) % len(self.game_manager._BattleManager__players)
        while not self.game_manager._BattleManager__players[self.game_manager._BattleManager__turn].is_alive():
            self.game_manager._BattleManager__turn = (self.game_manager._BattleManager__turn + 1) % len(self.game_manager._BattleManager__players)
        
        self.write_to_game(f"\n{self.game_manager._BattleManager__players[self.game_manager._BattleManager__turn].name}'s turn!")

    def get_valid_target(self, attacker: Character) -> Optional[Character]:
        """Get valid target for attacks/special moves"""
        try:
            target_num = int(self.game_input.get())
            valid_targets = [p for p in self.game_manager._BattleManager__players if p.is_alive() and p != attacker]
            if 1 <= target_num <= len(valid_targets):
                return valid_targets[target_num - 1]
        except ValueError:
            pass
        return None

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

    def handle_chat_input(self, event):
        message = self.chat_input.get().strip()
        if message:
            try:
                # Format message with player name
                formatted_message = f"{self.player_name}: {message}"
                
                # Send message to server
                self.client_socket.send(formatted_message.encode())
                
                # Display own message in green
                self.chat_display.configure(state='normal')
                self.chat_display.insert(tk.END, f"You: {message}\n", 'self')
                self.chat_display.configure(state='disabled')
                self.chat_display.see(tk.END)
                
                # Clear input
                self.chat_input.delete(0, tk.END)
            except Exception as e:
                self.show_error(f"Failed to send message: {str(e)}")
                
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
        # Disable start button
        self.start_button.configure(state='disabled')
        
        # Initialize JJK Game components
        character_names = ['Gojo', 'Sukuna', 'Megumi', 'Nanami', 'Nobara']
        factory = CharacterFactory()
        available_characters = [factory.create_character(name) for name in character_names]
        
        # Clear and update game display
        self.game_display.configure(state='normal')
        self.game_display.delete(1.0, tk.END)
        
        # Initialize game state
        self.game_manager = BattleManager(available_characters)
        self.game_started = True
        
        # Show character selection
        self.write_to_game("Choose your character:\n\n")
        for i, char in enumerate(available_characters, 1):
            self.write_to_game(f"{i}: {char.get_description()}\n")
        
        # Enable input for character selection
        self.game_input.configure(state='normal')
        
        # Notify other players game has started
        self.send_message({
            'type': 'game_start',
            'characters': character_names
        })

    def run(self):
        if self.connect_to_server():
            self.root.mainloop()
        else:
            tk.messagebox.showerror("Error", "Could not connect to server")
            self.root.destroy()

if __name__ == "__main__":
    client = UnifiedClient()
    client.run()