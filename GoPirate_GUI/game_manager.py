import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'JJK_Game')))

from JJK_Game.battle_manager import BattleManager
from JJK_Game.character_factory import CharacterFactory
from JJK_Game.character import Character
from JJK_Game.user_interface import get_valid_input, slow_print
from queue import Queue
from typing import List

class GameManager:
    def __init__(self, output_callback):
        self.output_queue = Queue()
        self.output_callback = output_callback
        self.character_names = ['Gojo', 'Sukuna', 'Megumi', 'Nanami', 'Nobara']
        self.factory = CharacterFactory()
        self.characters = []
        self.battle_manager = None
        self.current_player = None
        self.awaiting_input = False
        self.game_started = False
        
    def start_game(self):
        self.characters = [self.factory.create_character(name) for name in self.character_names]
        self.battle_manager = BattleManager(self.characters)
        self.game_started = True
        self.output("Welcome to Jujutsu Kaisen Battle Game!")
        self.output("Choose your characters to begin...")
        self.select_players()
        
    def select_players(self):
        self.output("Enter the number of players (1-5):")
        self.awaiting_input = True
        
    def handle_input(self, user_input: str):
        if not self.game_started:
            return
            
        if self.awaiting_input:
            try:
                num_players = int(user_input)
                if 1 <= num_players <= 5:
                    self.output(f"Selected {num_players} players")
                    self.display_character_selection()
                else:
                    self.output("Invalid number. Please enter 1-5.")
            except ValueError:
                self.output("Please enter a valid number.")
                
    def display_character_selection(self):
        self.output("\nAvailable characters:")
        for i, char in enumerate(self.characters, 1):
            self.output(f"{i}. {char.get_description()}")
            
    def output(self, message: str):
        self.output_callback(message + "\n")