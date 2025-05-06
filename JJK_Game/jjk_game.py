from battle_manager import BattleManager
from character_factory import CharacterFactory
from character import Character
from typing import Optional, Dict, List, Tuple

class JJKGame:
    def __init__(self):
        self.character_names: list[str] = ['Gojo', 'Sukuna', 'Megumi', 'Nanami', 'Nobara']
        self.factory: CharacterFactory = CharacterFactory()
        self.available_characters: list[Character] = [self.factory.create_character(name) for name in self.character_names]
        self.selected_characters: Dict[str, Character] = {}  # player_name -> character
        self.battle_manager: Optional[BattleManager] = None
        self.selection_order: list[str] = []  # Maintain player order
        self.current_turn: int = 0

    def get_available_characters(self) -> List[Tuple[int, str, str]]:
        """Get list of available characters with their descriptions"""
        return [(i, char.name, char.get_description()) 
                for i, char in enumerate(self.available_characters)]

    def select_character(self, player_name: str, choice_idx: int) -> Optional[Character]:
        """Let a player select their character"""
        if choice_idx < 0 or choice_idx >= len(self.available_characters):
            return None
            
        # Get character before removing from available list
        chosen = self.available_characters[choice_idx]
        # Remove character from available pool
        self.available_characters.pop(choice_idx)
        # Track selection
        self.selected_characters[player_name] = chosen
        if player_name not in self.selection_order:
            self.selection_order.append(player_name)
        return chosen

    def start_battle(self) -> None:
        """Initialize battle after all players have chosen"""
        if len(self.selection_order) < 2:
            return None
            
        # Set up battle manager with characters in selection order
        characters = [self.selected_characters[player] for player in self.selection_order]
        self.battle_manager = BattleManager(characters)
        # Initialize battle manager's player list
        self.battle_manager._BattleManager__players = characters
        self.current_turn = 0

    def handle_action(self, player: str, action: str, target_idx: Optional[int] = None) -> tuple[bool, str, dict]:
        """Handle a player's combat action"""
        if not self.battle_manager:
            return False, "Battle not started", {}

        # Verify turn order
        current_player = self.selection_order[self.current_turn % len(self.selection_order)]
        if player != current_player:
            return False, "Not your turn", {}

        char = self.selected_characters[player]
        result = False
        msg = "Invalid action"
        
        # Handle different action types
        if action == "attack" and target_idx is not None:
            targets = [c for p, c in self.selected_characters.items() 
                      if p != player and c.is_alive()]
            if 0 <= target_idx < len(targets):
                char.attack(targets[target_idx])
                result = True
                msg = f"{char.name} attacked {targets[target_idx].name}"
                
        elif action == "defend":
            char.defend()
            result = True
            msg = f"{char.name} took a defensive stance"
            
        elif action == "special" and target_idx is not None:
            targets = [c for p, c in self.selected_characters.items() 
                      if p != player and c.is_alive()]
            if 0 <= target_idx < len(targets):
                if char.special([targets[target_idx]], self.current_turn):
                    result = True
                    msg = f"{char.name} used their special move"

        # Advance turn if action was successful
        if result:
            self.current_turn += 1
            # Handle status effects for next player
            next_char = self.selected_characters[self.get_current_player()]
            next_char.handle_defense_boost()
            next_char.handle_poison()
            if next_char.handle_stun():
                self.current_turn += 1

        return result, msg, self.get_game_state()

    def get_current_player(self) -> str:
        """Get the name of the current player"""
        if not self.selection_order:
            return ""
        return self.selection_order[self.current_turn % len(self.selection_order)]

    def get_game_state(self) -> dict:
        """Get current game state for display"""
        state = {
            "players": {},
            "current_turn": self.get_current_player(),
            "available_characters": self.get_available_characters(),
            "battle_started": self.battle_manager is not None,
            "game_over": False
        }
        
        for player, char in self.selected_characters.items():
            state["players"][player] = {
                "name": char.name,
                "hp": char.hp,
                "is_alive": char.is_alive(),
                "defense": char.defense,
                "poisoned": char.poison.is_active(),
                "stunned": char.stun.is_active()
            }
        
        # Check win condition
        alive_players = [p for p, c in self.selected_characters.items() if c.is_alive()]
        if len(alive_players) == 1:
            state["game_over"] = True
            state["winner"] = alive_players[0]
            
        return state

if __name__ == "__main__":
    # This will now be handled by the GUI
    pass
