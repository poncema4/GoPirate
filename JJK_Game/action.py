from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from JJK_Game.user_interface import slow_print
import time

if TYPE_CHECKING:
    from character import Character


class Action(ABC):
    """
    Abstract Base Class representing actions that characters can use during the game.
    """

    # region Constructor
    def __init__(self, name: str, description: str, voiceline: str):
        """
        Super constructor for all actions. Takes in a name, description, and voiceline.
        :param name: The name of this action.
        :param description: A short description of this action.
        :param voiceline: The line to be printed when this action is used.
        """
        self._name: str = name
        self._description: str = description
        self._voiceline: str = voiceline

    # endregion

    # region Properties
    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def voiceline(self) -> str:
        return self._voiceline

    # endregion

    # region Methods
    @abstractmethod
    def apply(self, *args, **kwargs) -> None:
        """
        Abstract method that needs to be implemented by subclasses.
        Represents the action to be performed by the attacker on the defender.
        """
        pass

    # endregion


class Attack(Action):
    """
    Represents a basic attack action, where the attacker deals damage to the defender.
    """

    # region Constructor
    def __init__(self, damage: int, name: str, description: str, voiceline: str) -> None:
        """
        Constructors a new Attack instance with a damage ammount, name, description, and voiceline.
        :param damage: The amount of damage that the defender will take.
        :param name: The name of this Attack.
        :param description: A short description from the show.
        :param voiceline: The string to be spoken upon this attack being used.
        """
        super().__init__(name, description, voiceline)
        self.__damage: int = damage

    # endregion

    # region Properties
    @property
    def damage(self) -> int:
        return self.__damage

    # endregion

    # region Methods
    def apply(self, attacker: Character, defender: Character) -> None:
        """
        Computes the amount of damage dealt after defense and checks if the defender is defeated.

        @param attacker: The character using their attack.
        @param defender: The character receiving the attack.
        """
        damage = max(self.__damage - defender.defense, 0)
        defender.hp -= damage
        slow_print(f"{attacker.name} attacks {defender.name} for {damage} damage!")
        slow_print(f"{defender.name} has {defender.hp} HP remaining.")
        if not defender.is_alive():
            print(f"{defender.name} has been defeated!")
        time.sleep(1)
    # endregion


class Defend(Action):
    """
    Represents a defensive action, where the attacker temporarily doubles their defense.
    """

    # region Constructor
    def __init__(self, name: str, description: str, base_defense: int, boost: int):
        """
        Constructors a new Defend instance with a name, description, base_defense, and boost.
        :param name: The name of the Defend action.
        :param description: A short description of the Defend action from the show.
        :param base_defense: The number of hp to negate from an attack when not defending.
        :param boost: The number of hp to negate in addition to base_defense form an attack when defending.
        """
        super().__init__(name, description, '')
        self.__base_defense: int = base_defense
        self.__boost: int = boost
        self.__current_defense: int = base_defense

    # endregion

    # region Properties
    @property
    def boost(self) -> int:
        return self.__boost

    @property
    def base_defense(self) -> int:
        return self.__base_defense

    @property
    def current_defense(self) -> int:
        return self.__current_defense

    @current_defense.setter
    def current_defense(self, defense: int) -> None:
        self.__current_defense = defense

    # endregion

    # region Methods
    def is_boost_active(self) -> bool:
        """
        Does this Defend have a defense boost applied?

        :return: True if a defense boost is applied, False otherwise.
        """
        return self.__current_defense > self.__base_defense

    def apply(self) -> None:
        """
        Apply the defense boost the character

        :return: None
        """
        self.__current_defense += self.__boost
    # endregion


class SpecialMove(Action, ABC):
    """
    Represents a special move with a cooldown that can be used during the game.
    """

    # region Constructor
    def __init__(self, name: str, description: str, voiceline: str, cooldown: int) -> None:
        """
        Initializes a special move with a name description, voiceline, and cooldown
        :param name: The name of the special move
        :param description: A short description of what it does in the show and what it does in the game
        :param voiceline: The line to be spoken when this special move is used
        :param cooldown: The number of turns you must wait in between using this special move.
        """
        super().__init__(name, description, voiceline)
        self.__cooldown: int = cooldown
        self.__last_used: int = 0

    # endregion

    # region Properties
    @property
    def cooldown(self) -> int:
        return self.__cooldown

    @cooldown.setter
    def cooldown(self, value) -> None:
        self.__cooldown = value

    @property
    def last_used(self) -> int:
        return self.__last_used

    @last_used.setter
    def last_used(self, value) -> None:
        self.__last_used = value

    # endregion

    # region Methods
    def is_available(self, turn: int) -> bool:
        """
        Returns whether this special move is available or not
        :param turn: The current turn count
        :return: True if the special move is available, False otherwise.
        """
        return turn - self.last_used >= self.__cooldown

    @abstractmethod
    def apply(self, defenders: list[Character]) -> None:
        """
        Applies this special to the given list of characters.

        :param defenders: The list of characters to apply the special to.
        """
        pass
    # endregion
