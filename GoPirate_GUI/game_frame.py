import tkinter as tk
from tkinter import scrolledtext
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from JJK_Game.battle_manager import BattleManager
from JJK_Game.character_factory import CharacterFactory
from JJK_Game.character import Character
from io import StringIO

class GameFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, relief=tk.RAISED, borderwidth=1)
        self.setup_ui()
        self.stdout_backup = sys.stdout
        self.game_output = StringIO()
        
    def setup_ui(self):
        # Game title
        tk.Label(self, text="JJK Game Terminal", font=('Arial', 12, 'bold')).pack(pady=5)
        
        # Game output area
        self.output_area = scrolledtext.ScrolledText(self, height=20, width=60)
        self.output_area.pack(padx=5, pady=5)
        
        # Input area
        self.input_area = tk.Entry(self)
        self.input_area.pack(fill=tk.X, padx=5, pady=5)
        
        # Start button
        tk.Button(self, text="Start New Game", command=self.start_game).pack(pady=5)
        
    def start_game(self):
        self.output_area.delete(1.0, tk.END)
        sys.stdout = self.game_output = StringIO()
        
        # Start game in a separate thread to prevent GUI freezing
        import threading
        game_thread = threading.Thread(target=self._run_game)
        game_thread.start()
        
        # Start monitoring the output
        self.monitor_output()
        
    def _run_game(self):
        character_names = ['Gojo', 'Sukuna', 'Megumi', 'Nanami', 'Nobara']
        factory = CharacterFactory()
        characters = [factory.create_character(name) for name in character_names]
        BattleManager(characters).start_battle()
        
    def monitor_output(self):
        if self.game_output:
            content = self.game_output.getvalue()
            if content != self.output_area.get(1.0, tk.END).strip():
                self.output_area.delete(1.0, tk.END)
                self.output_area.insert(tk.END, content)
                self.output_area.see(tk.END)
        self.after(100, self.monitor_output)
