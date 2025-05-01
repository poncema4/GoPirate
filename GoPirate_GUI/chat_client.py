import tkinter as tk
from tkinter import ttk, scrolledtext
import socket
import threading
import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Chat_Bot.chat_bot import Chatbot
from JJK_Game.battle_manager import BattleManager
from JJK_Game.character_factory import CharacterFactory

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
        
        self.game_display = scrolledtext.ScrolledText(game_frame)
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
        
        self.chatbot = Chatbot()
        self.chatbot_display = scrolledtext.ScrolledText(chatbot_frame)
        self.chatbot_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.chatbot_input = ttk.Entry(chatbot_frame)
        self.chatbot_input.pack(fill=tk.X, padx=5, pady=5)
        self.chatbot_input.bind('<Return>', self.handle_chatbot_input)

    def setup_multiplayer_chat(self):
        chat_frame = ttk.LabelFrame(self.right_panel, text="Player Chat")
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.chat_display = scrolledtext.ScrolledText(chat_frame)
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.chat_input = ttk.Entry(chat_frame)
        self.chat_input.pack(fill=tk.X, padx=5, pady=5)
        self.chat_input.bind('<Return>', self.handle_chat_input)

    def connect_to_server(self, host='localhost', port=12345):
        try:
            self.client_socket.connect((host, port))
            self.player_name = self.get_player_name()
            
            # Send initial join message
            join_msg = {
                'type': 'join',
                'name': self.player_name
            }
            self.send_message(join_msg)
            
            # Start receiver thread
            self.receiver_thread = threading.Thread(target=self.receive_messages, daemon=True)
            self.receiver_thread.start()
            
            # Show welcome message
            self.add_system_message(f"Welcome {self.player_name}!")
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
        self.chat_display.tag_configure('right', justify='right')
        self.chat_display.tag_configure('left', justify='left')
        self.chat_display.tag_configure('center', justify='center')
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
        if command:
            self.game_input.delete(0, tk.END)
            # Send game input to server
            self.send_message({
                'type': 'game_input',
                'content': command,
                'player': self.player_name
            })

    def receive_messages(self):
        while True:
            try:
                data = self.client_socket.recv(4096).decode()  # Increased buffer size
                messages = data.split('\n')
                
                for data in messages:
                    if not data:
                        continue
                        
                    try:
                        message = json.loads(data)
                        
                        if message['type'] == 'chat':
                            sender = message.get('sender', '')
                            content = message.get('content', '')
                            if sender == self.player_name:
                                self.add_chat_message("You", content, True)
                            else:
                                self.add_chat_message(sender, content, False)
                        
                        elif message['type'] == 'join':
                            name = message.get('name', '')
                            self.add_system_message(f"{name} has joined!")
                        
                        elif message['type'] == 'game_update':
                            self.write_to_game(f"{message.get('content', '')}\n")
                        
                        elif message['type'] == 'game_start':
                            players = message.get('players', [])
                            self.start_game_session(players)
                        
                        elif message['type'] == 'system':
                            self.add_system_message(message.get('content', ''))
                        
                        elif message['type'] == 'error':
                            self.show_error(message.get('content', ''))
                            
                    except json.JSONDecodeError:
                        print(f"Invalid JSON received: {data}")
                        
            except ConnectionResetError:
                self.add_system_message("Connection to server lost!")
                break
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def add_chat_message(self, sender: str, content: str, is_self: bool):
        self.chat_display.configure(state='normal')
        if is_self:
            self.chat_display.insert(tk.END, f"You: {content}\n", 'right')
        else:
            self.chat_display.insert(tk.END, f"{sender}: {content}\n", 'left')
        self.chat_display.configure(state='disabled')
        self.chat_display.see(tk.END)

    def add_system_message(self, message: str):
        self.chat_display.configure(state='normal')
        self.chat_display.insert(tk.END, f"*** {message} ***\n", 'center')
        self.chat_display.configure(state='disabled')
        self.chat_display.see(tk.END)

    def show_error(self, message: str):
        tk.messagebox.showerror("Error", message)

    def handle_chat_input(self, event):
        message = self.chat_input.get().strip()
        if message:
            # Only handle player chat messages here
            self.send_message({
                'type': 'chat',
                'content': message,
                'sender': self.player_name
            })
            self.chat_input.delete(0, tk.END)

    def handle_chatbot_input(self, event):
        message = self.chatbot_input.get().strip()
        if message:
            # Display user message
            self.chatbot_display.configure(state='normal')
            self.chatbot_display.insert(tk.END, f"You: {message}\n", 'user')
            self.chatbot_display.configure(state='disabled')
            self.chatbot_display.see(tk.END)
            
            # Get chatbot response
            response = self.chatbot.process_query(message)
            
            # Display bot response
            self.chatbot_display.configure(state='normal')
            self.chatbot_display.insert(tk.END, f"Bot: {response}\n", 'bot')
            self.chatbot_display.configure(state='disabled')
            self.chatbot_display.see(tk.END)
            
            self.chatbot_input.delete(0, tk.END)

    def start_game(self):
        self.send_message({'type': 'game_start'})

    def run(self):
        if self.connect_to_server():
            self.root.mainloop()
        else:
            tk.messagebox.showerror("Error", "Could not connect to server")
            self.root.destroy()

if __name__ == "__main__":
    client = UnifiedClient()
    client.run()