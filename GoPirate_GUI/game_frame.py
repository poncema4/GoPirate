import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from JJK_Game.character_factory import CharacterFactory

class GameFrame(tk.Frame):
    def __init__(self, master, players):
        super().__init__(master, relief=tk.RAISED, borderwidth=1)
        self.output_area = None
        self.factory = CharacterFactory()
        self.players = players
        self.characters = []
        self.player_characters = {}  # Maps player names to their chosen characters
        self.state = 'start'
        self.current_turn = 0
        self.battle_in_progress = False
        self.current_player = None

        self.pack()
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(fill="both", expand=True, padx=5, pady=5)
        self.button_frame.grid_columnconfigure(0, weight=1)

        self.info_label = tk.Label(self, text="", font=('Arial', 12, 'bold'))
        self.info_label.pack()

        self.setup_ui()

    def clear_buttons(self):
        for child in self.button_frame.winfo_children():
            child.destroy()
        
    def setup_ui(self):
        self.clear_buttons()
        self.info_label.configure(text="Welcome to the game!")
        start_btn = ttk.Button(self.button_frame, text="Start Game", command=self.start_game)
        start_btn.pack()
        # # Game title
        # tk.Label(self, text="JJK Game Terminal", font=('Arial', 12, 'bold')).pack(pady=5)
        #
        # # Game output area
        # self.output_area = scrolledtext.ScrolledText(self, height=20, width=60)
        # self.output_area.pack(padx=5, pady=5)
        #
        # # Actions frame
        # actions_frame = ttk.Frame(self)
        # actions_frame.pack(fill=tk.X, padx=5, pady=5)
        #
        # # Target input for entering player numbers
        # self.target_input = ttk.Entry(actions_frame, width=10)
        # self.target_input.pack(side=tk.LEFT, padx=5)
        #
        # # Action buttons
        # self.attack_btn = ttk.Button(actions_frame, text="Attack", command=self.handle_attack)
        # self.attack_btn.pack(side=tk.LEFT, padx=5)
        #
        # self.defend_btn = ttk.Button(actions_frame, text="Defend", command=self.handle_defend)
        # self.defend_btn.pack(side=tk.LEFT, padx=5)
        #
        # self.special_btn = ttk.Button(actions_frame, text="Special", command=self.handle_special)
        # self.special_btn.pack(side=tk.LEFT, padx=5)
        #
        # # Start button
        # self.start_btn = ttk.Button(self, text="Start Game", command=self.start_game)
        # self.start_btn.pack(pady=5)
        #
        # self.disable_combat_buttons()

    def write_output(self, text):
        self.output_area.configure(state='normal')
        self.output_area.insert(tk.END, text + "\n")
        self.output_area.see(tk.END)
        self.output_area.configure(state='disabled')

    def render_character_selection(self):
        self.clear_buttons()
        self.info_label.configure(text="Choose your character:")

        character_names = ['Gojo', 'Sukuna', 'Megumi', 'Nanami', 'Nobara']
        self.characters = [self.factory.create_character(name) for name in character_names]

        # Scrollable frame
        canvas = tk.Canvas(self.button_frame, height=300)  # Fixed height
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

        for character in self.characters:
            btn = tk.Button(
                scrollable_frame,
                text=character.get_description(),
                anchor="w",
                justify="left",
                wraplength=600
            )
            btn.configure(command=lambda c=character: self.handle_character_selection(c.name))
            btn.pack(fill="x", padx=5, pady=2)

    def start_game(self):
        self.battle_in_progress = True
        self.state = 'select'
        self.render_character_selection()
        
        # Initialize game
        character_names = ['Gojo', 'Sukuna', 'Megumi', 'Nanami', 'Nobara']
        self.characters = [self.factory.create_character(name) for name in character_names]
        
        # Clear output and show character options
        self.output_area.configure(state='normal')
        self.output_area.delete(1.0, tk.END)
        self.output_area.configure(state='disabled')
        
        self.write_output("Choose your character:\n")
        for i, char in enumerate(self.characters, 1):
            self.write_output(f"{i}: {char.get_description()}")
        
        self.current_player = self.players[0]
        self.write_output(f"\n{self.current_player}'s turn to choose a character (1-{len(self.characters)})")

    def handle_character_selection(self, selection):

        try:
            idx = int(selection) - 1
            if 0 <= idx < len(self.characters):
                chosen = self.characters.pop(idx)
                self.player_characters[self.current_player] = chosen
                self.write_output(f"{self.current_player} selected {chosen.name}")
                
                if len(self.player_characters) < len(self.players):
                    # Next player's turn
                    self.current_player = self.players[len(self.player_characters)]
                    self.write_output(f"\n{self.current_player}'s turn to choose a character (1-{len(self.characters)})")
                else:
                    # All players have chosen, start battle
                    self.start_battle()
            else:
                self.write_output("Invalid selection. Try again.")
        except ValueError:
            self.write_output("Please enter a valid number.")

    def handle_attack(self):
        if not self.battle_in_progress or not self.is_current_turn():
            return
            
        target = self.get_target()
        if target:
            current_char = self.player_characters[self.current_player]
            current_char.attack(target)
            self.next_turn()

    def handle_defend(self):
        if not self.battle_in_progress or not self.is_current_turn():
            return
            
        current_char = self.player_characters[self.current_player]
        current_char.defend()
        self.next_turn()

    def handle_special(self):
        if not self.battle_in_progress or not self.is_current_turn():
            return
            
        target = self.get_target()
        if target:
            current_char = self.player_characters[self.current_player]
            if current_char.special([target], self.current_turn):
                self.next_turn()

    def get_target(self):
        target_num = self.target_input.get().strip()
        if not target_num.isdigit():
            self.write_output("Please enter a valid target number")
            return None
            
        try:
            target_idx = int(target_num) - 1
            valid_targets = [char for player, char in self.player_characters.items() 
                           if player != self.current_player and char.is_alive()]
            
            if 0 <= target_idx < len(valid_targets):
                return valid_targets[target_idx]
            else:
                self.write_output("Invalid target number")
                return None
        except ValueError:
            self.write_output("Please enter a valid number")
            return None

    def start_battle(self):
        self.write_output("\nTime to show what real Jujutsu really is...")
        self.current_turn = 0
        self.current_player = self.players[0]
        self.enable_combat_buttons()
        self.next_turn()

    def next_turn(self):
        # Handle status effects
        current_char = self.player_characters[self.current_player]
        current_char.handle_defense_boost()
        current_char.handle_poison()
        if current_char.handle_stun():
            self.advance_turn()
            return

        alive_players = [p for p in self.players if self.player_characters[p].is_alive()]
        if len(alive_players) <= 1:
            self.end_game()
            return

        self.write_output(f"\n{self.current_player}'s turn!")
        valid_targets = [char for player, char in self.player_characters.items() 
                        if player != self.current_player and char.is_alive()]
        
        if valid_targets:
            self.write_output("Available targets:")
            for i, target in enumerate(valid_targets, 1):
                self.write_output(f"{i}: {target}")

    def advance_turn(self):
        self.current_turn = (self.current_turn + 1) % len(self.players)
        while not self.player_characters[self.players[self.current_turn]].is_alive():
            self.current_turn = (self.current_turn + 1) % len(self.players)
        self.current_player = self.players[self.current_turn]
        self.next_turn()

    def end_game(self):
        winner = next(p for p in self.players if self.player_characters[p].is_alive())
        self.write_output(f"\n{winner} is the chosen one!")
        self.battle_in_progress = False
        self.disable_combat_buttons()
        self.start_btn.configure(state='normal')

    def is_current_turn(self):
        return self.battle_in_progress and self.current_player == self.players[self.current_turn]

    def enable_combat_buttons(self):
        self.attack_btn.configure(state='normal')
        self.defend_btn.configure(state='normal')
        self.special_btn.configure(state='normal')
        self.target_input.configure(state='normal')

    def disable_combat_buttons(self):
        self.attack_btn.configure(state='disabled')
        self.defend_btn.configure(state='disabled')
        self.special_btn.configure(state='disabled') 
        self.target_input.configure(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    root.title('JJK TEST')

    # Example player list
    players = ["Player 1", "Player 2"]

    # Create and pack the game frame
    frame = GameFrame(root, players)
    frame.pack(fill="both", expand=True)

    root.mainloop()