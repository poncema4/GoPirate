from typing import List, Optional, Dict
from JJK_Game.character import Character


class BattleManager:
    def __init__(self, available_players: List[Character]):
        self.__available_players: List[Character] = available_players.copy()
        self.__players: List[Character] = []
        self.__turn: int = 0
        self.__current_turn_index: int = 0
        self.__previously_alive: set = set()

    def get_available_characters(self) -> List[str]:
        return [c.name for c in self.__available_players]

    def assign_character(self, character_name: str) -> Optional[Character]:
        for c in self.__available_players:
            if c.name == character_name:
                self.__available_players.remove(c)
                self.__players.append(c)
                return c
        return None

    def is_battle_ready(self) -> bool:
        return len(self.__players) >= 2

    def start_battle(self):
        self.__turn = 0
        self.__current_turn_index = 0
        self.__previously_alive = set(p for p in self.__players if p.is_alive())

    def is_battle_over(self) -> bool:
        return sum(p.is_alive() for p in self.__players) <= 1

    def get_current_player(self) -> Optional[Character]:
        if not self.__players:
            return None
        for _ in range(len(self.__players)):
            player = self.__players[self.__current_turn_index]
            if player.is_alive():
                return player
            self.__current_turn_index = (self.__current_turn_index + 1) % len(self.__players)
        return None

    def advance_turn(self):
        self.__turn += 1
        self.__current_turn_index = (self.__current_turn_index + 1) % len(self.__players)
        self.__previously_alive = set(p for p in self.__players if p.is_alive())

    def handle_status_effects(self, player: Character) -> bool:
        player.handle_defense_boost()
        player.handle_poison()
        return player.handle_stun()

    def apply_action(self, actor: Character, action: str, target: Optional[Character] = None) -> str:
        if action == 'attack' and target:
            return actor.attack(target)
        elif action == 'defend':
            return actor.defend()
        elif action == 'special':
            others = [p for p in self.__players if p != actor and p.is_alive()]
            actor.special(others, self.__turn)
            return actor.special_move.voiceline
        return ''

    def get_alive_targets(self, exclude: Optional[Character] = None) -> List[str]:
        return [p.name for p in self.__players if p.is_alive() and p != exclude]

    def get_target_by_name(self, name: str) -> Optional[Character]:
        for p in self.__players:
            if p.name == name and p.is_alive():
                return p
        return None

    def get_battle_state(self) -> Dict:
        return {
            "turn": self.__turn,
            "players": [
                {
                    "name": p.name,
                    "hp": p.hp,
                    "alive": p.is_alive(),
                    "poison": {
                        "active": p.poison.is_active(),
                        "damage": p.poison.damage,
                        "duration": p.poison.duration
                    },
                    "stunned": p.stun.is_active()
                }
                for p in self.__players
            ]
        }

    def get_winner(self) -> Optional[str]:
        for p in self.__players:
            if p.is_alive():
                return p.name
        return None
