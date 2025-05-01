from dataclasses import dataclass
from typing import List, Dict
from JJK_Game.character import Character

@dataclass
class GameState:
    players: List[str]
    characters: Dict[str, Character]
    current_turn: int
    is_active: bool = False
    
    def next_turn(self):
        self.current_turn = (self.current_turn + 1) % len(self.players)
        
    def get_current_player(self) -> str:
        return self.players[self.current_turn]