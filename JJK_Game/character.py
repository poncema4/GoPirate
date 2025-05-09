from JJK_Game.action import Attack, Defend, SpecialMove
from JJK_Game.status_effects import Stun, Poison
from JJK_Game.user_interface import slow_print
import time


class Character:
    """
    Base character class with information, stats and a special move.
    """

    # region Constructor and Overrides
    def __init__(self, name: str, hp: int, attack_move: Attack, defense_move: Defend,
                 special_move: SpecialMove) -> None:
        """
        Initializes a character with the given name, hit points, attack, defense, and special move.

        :param name: The name of the character.
        :param hp: The hit points of the character.
        :param attack_move: The attack class for this player
        :param defense_move: The defense class for this player
        :param special_move: The special move class for this player
        """
        # Attributes
        self._name: str = name
        self._hp: int = hp
        # Actions
        self._attack_move: Attack = attack_move
        self._defense_move: Defend = defense_move
        self._special_move: SpecialMove = special_move
        # Effects
        self._stun: Stun = Stun(0)
        self._poison: Poison = Poison(10, 0)

    def __str__(self) -> str:
        return f"{self._name} (HP: {self._hp})"

    # endregion

    # region Properties
    @property
    def name(self):
        return self._name

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = value

    @property
    def attack_damage(self) -> int:
        return self._attack_move.damage

    @property
    def defense(self):
        return self._defense_move.current_defense

    @property
    def special_move(self):
        return self._special_move

    @property
    def stun(self) -> Stun:
        return self._stun

    @property
    def poison(self) -> Poison:
        return self._poison

    # endregion

    # region Methods
    def is_alive(self) -> bool:
        """
        Determines if the player is still alive.
        :return: True if the player's hit points are greater than 0, False otherwise.
        """
        return self.hp > 0

    def get_description(self) -> str:
        """
        Gets the description of this character including name, hp, attack, defense, and special move.
        :return: String containing the description of this character.
        """
        return (
            f"{str(self)}\n"
            f"Attack: {self._attack_move.name}\n"
            f"  - {self._attack_move.description.strip()}\n"
            f"  - Damage: {self._attack_move.damage} HP\n"
            f"Defense: {self._defense_move.name}\n"
            f"  - {self._defense_move.description.strip()}\n"
            f"  - Base: {self._defense_move.base_defense} HP\n"
            f"  - Boost: {self._defense_move.boost} HP\n"
            f"Special Move: {self.special_move.name}\n"
            f"  - {self.special_move.description.strip()}\n"
            f"  - Cooldown: {self.special_move.cooldown} turns\n"
        )

    def attack(self, target: 'Character') -> None:
        """
        Deals damage to the given target based on this character's attack class.
        :param target: Character receiving the attack.
        :return: None
        """
        slow_print(self._attack_move.voiceline)
        self._attack_move.apply(self, target)

    def defend(self) -> None:
        """
        Applies this character's defense boost to their defense class.
        :return: None
        """
        if not self._defense_move.is_boost_active():
            self._defense_move.apply()
            slow_print(f"{self._name} strengthens themselves, adding {self._defense_move.boost} defense.")
        else:
            slow_print(f"{self._name} is already defending this turn.")
        time.sleep(1)

    def handle_defense_boost(self) -> None:
        """
        Reverts this character's defense to it's base value if a boost was active.
        @return: None
        """
        # If a defense boost is applied
        if self._defense_move.is_boost_active():
            # reset it
            self._defense_move.current_defense = self._defense_move.base_defense

    def special(self, targets: list['Character'], turn: int) -> bool:
        """
        Applies this character's special move to the given list of targets if they are not on cooldown.
        @param targets: List of targets to be effected by the special.
        @param turn: The current tally of turns that have passed.
        @return: True if the special was applied, False otherwise.
        """
        if self._special_move.is_available(turn):
            slow_print(self._special_move.voiceline)
            self._special_move.apply(targets)
            self._special_move.last_used = turn
        else:
            slow_print(f"{self._special_move.name} is on cooldown! Choose another action.")
            return False
        time.sleep(1)
        return True

    def handle_poison(self) -> None:
        """
        Directs this player's poison class to deal damage if this player is poisoned.
        @return: None
        """
        self._poison.handle(self)

    def handle_stun(self) -> bool:
        """
        Directs this player's stun class to deactive the stun if it is active.
        @return: True if a stun was active, false otherwise.
        """
        if self._stun.is_active():
            self._stun.handle(self)
            return True
        else:
            return False
    # endregion
