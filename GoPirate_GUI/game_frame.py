import json
import threading
import tkinter as tk
import socket
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from JJK_Game.character_factory import CharacterFactory


class GameFrame(tk.Frame):
    def __init__(self, master, player_name=None):
        super().__init__(master, relief=tk.RAISED, borderwidth=1)
        self.factory = CharacterFactory()
        self.player = player_name
        self.character = ''
        self.state = 'start'
        self.battle_in_progress = False
        self.current_player = None
        self.is_my_turn = False
        self.available_targets = []
        self.characters = []

        # Network setup
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # UI Setup
        self.pack(fill="both", expand=True)

        # Info label for turn/status info
        self.info_label = tk.Label(self, text="", font=('Arial', 12, 'bold'))
        self.info_label.pack(pady=5)

        # Button frame for action buttons
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Initial UI setup
        self.setup_ui()

    def clear_buttons(self):
        """Clear all buttons from the button frame"""
        for child in self.button_frame.winfo_children():
            child.destroy()

    def setup_ui(self):
        """Initialize the UI based on current game state"""
        self.clear_buttons()
        if not self.player:
            self.info_label.configure(text="Connecting to server...")
        else:
            self.info_label.configure(text=f"Welcome {self.player}!")

        if not self.battle_in_progress:
            start_btn = ttk.Button(self.button_frame, text="Start Game", command=self.start_game)
            start_btn.pack()

    def render_character_selection(self, descriptions: list[dict[str, str]]):
        """Show character selection UI"""
        self.clear_buttons()
        self.info_label.configure(text="Choose your character:")

        # Scrollable frame for character selection
        canvas = tk.Canvas(self.button_frame, height=300)
        scrollbar = tk.Scrollbar(self.button_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for description in descriptions:
            name = description['name']
            description = description['description']
            btn = tk.Button(
                scrollable_frame,
                text=description,
                anchor="w",
                justify="left",
                wraplength=600,
                command= lambda n=name : self.handle_character_selection(n)
            )
            btn.pack(fill="x", padx=5, pady=2)

    def render_action_buttons(self):
        """Show action buttons during player's turn"""
        self.clear_buttons()
        self.info_label.config(text=f"{self.player}'s turn: Choose an action")

        # Action buttons
        actions = [
            ("Attack", self.handle_attack),
            ("Defend", self.handle_defend),
            ("Special", self.handle_special)
        ]

        for text, command in actions:
            btn = ttk.Button(
                self.button_frame,
                text=text,
                command=command,
                state="normal" if self.is_my_turn else "disabled"
            )
            btn.pack(pady=5, fill="x")

    def render_target_selection(self, targets):
        """Show target selection UI"""
        self.clear_buttons()
        self.info_label.config(text=f"{self.player}, select your target:")
        self.available_targets = targets

        for target in targets:
            btn = ttk.Button(
                self.button_frame,
                text=target,
                command=lambda t=target: self.select_target(t)
            )
            btn.pack(pady=2, fill="x")

    def perform_action(self, action_type, target):
        """Handle action confirmation"""
        self.info_label.config(text=f"{self.player} used {action_type} on {target}")
        self.after(1500, self.end_turn)

    def end_turn(self):
        """Clean up after turn completion"""
        self.is_my_turn = False
        self.render_action_buttons()

    def start_game(self):
        """Initialize game start"""
        self.battle_in_progress = True
        self.state = 'select'
        self.send_message({'type': 'start'})

    def connect(self, name: str):
        try:
            self.sock.connect(('localhost', 5555))
            self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            self.receive_thread.start()
            self.send_message({'type': 'join', 'player_name': name})
        except ConnectionRefusedError:
            messagebox.showerror("Connection Error", "Could not connect to game server")
            self.master.destroy()
            return

    def handle_character_selection(self, selection):
        """Handle character selection"""
        self.character = selection
        self.send_message({
            'type': 'character_choice',
            'character': selection
        })
        self.info_label.config(text=f"You selected {selection}. Waiting for others...")
        self.clear_buttons()

    def receive_messages(self):
        """Thread for receiving server messages"""
        buffer = b''
        while True:
            try:
                data = self.sock.recv(1024)
                if not data:
                    break
                buffer += data
                while b'\n' in buffer:
                    message, _, buffer = buffer.partition(b'\n')
                    self.handle_server_message(json.loads(message))
            except (ConnectionAbortedError, ConnectionResetError):
                self.after(0, lambda: messagebox.showerror("Connection Error", "Disconnected from server"))
                break
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Connection error: {str(e)}"))
                break

    def handle_server_message(self, data):
        """Process messages from server"""
        if data['type'] == 'player_assignment':
            self.after(100, self.set_player_info, data['player_name'])
        elif data['type'] == 'character_selection':
            self.after(100, self.render_character_selection, data['descriptions'])
        elif data['type'] == 'action_selection':
            self.after(100, self.enable_turn)
        elif data['type'] == 'target_selection':
            self.after(100, self.render_target_selection, data['targets'])
        elif data['type'] == 'battle_over':
            self.after(100, self.handle_battle_end, data['winner'])

    def set_player_info(self, player_name):
        """Set player name from server"""
        self.player = player_name
        self.info_label.config(text=f"Logged in as {player_name}")
        self.setup_ui()

    def enable_turn(self):
        """Enable UI for player's turn"""
        self.is_my_turn = True
        self.render_action_buttons()

    def handle_attack(self):
        """Handle attack action"""
        if self.is_my_turn:
            self.send_message({'type': 'action', 'action': 'attack'})

    def handle_defend(self):
        """Handle defend action"""
        if self.is_my_turn:
            self.send_message({'type': 'action', 'action': 'defend'})

    def handle_special(self):
        """Handle special action"""
        if self.is_my_turn:
            self.send_message({'type': 'action', 'action': 'special'})

    def select_target(self, target):
        """Handle target selection"""
        self.send_message({'type': 'target', 'target': target})
        self.is_my_turn = False
        self.render_action_buttons()

    def handle_battle_end(self, winner):
        """Handle battle conclusion"""
        self.battle_in_progress = False
        self.is_my_turn = False
        self.info_label.config(text=f"Battle over! {winner} wins!")
        self.clear_buttons()
        restart_btn = ttk.Button(
            self.button_frame,
            text="Play Again",
            command=self.start_game
        )
        restart_btn.pack()

    def send_message(self, data):
        """Send message to server"""
        try:
            self.sock.sendall(json.dumps(data).encode() + b'\n')
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to send data: {str(e)}")

    def on_close(self):
        """Clean up on window close"""
        try:
            self.sock.close()
        except:
            pass
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.title('JJK Battle Client')

    # Get player name before starting
    player_name = simpledialog.askstring("Player Name", "Enter your player name:")
    if not player_name:
        sys.exit()

    frame = GameFrame(root, player_name)
    root.protocol("WM_DELETE_WINDOW", frame.on_close)
    root.mainloop()