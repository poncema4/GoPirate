from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from character import Character


class StatusEffect(ABC):
    """
    Abstract class for storing and handling status effects.
    """

    # region Constructor
    def __init__(self, duration: int) -> None:
        """
        Super constructor for status effects. Takes a duration.
        :param duration: The number of moves this status effect will be applied for.
        """
        self._duration: int = duration

    # endregion

    # region Properties
    @property
    def duration(self) -> int:
        return self._duration

    @duration.setter
    def duration(self, duration: int) -> None:
        self._duration = duration

    # endregion

    # region Methods
    @abstractmethod
    def handle(self, player: 'Character') -> None:
        """
        Handles the status effect for the given player.

        @param player: The player to alter.
        @return: None
        """
        pass

    def is_active(self) -> bool:
        """
        Checks if this effect is active.
        @return: True if the effect is active, False otherwise.
        """
        return self._duration > 0
    # endregion


class Poison(StatusEffect):
    """
    Class for managing poison damage and duration.
    """

    # region Constructor
    def __init__(self, damage: int, duration: int) -> None:
        """
        Initializes a Poison instance with a damage and duraiton.
        :param damage: The amount of damage to deal per round this poison is active.
        :param duration: The number of rounds this poison is active for.
        """
        super().__init__(duration)
        self.damage: int = damage
    # endregion

    # region Methods
    def handle(self, player: 'Character') -> None:
        """
        If the poison effect is active, applies poison damage to the given player and decreases the duration.
        @param player: The player to alter.
        @return: None
        """
        if not self.is_active():
            return

        player.hp -= self.damage
        print(f'{player.name} is poisoned! They take {self.damage} damage.')

        if not player.is_alive():
            print(f'{player.name} was eliminated by poison!')

        self.duration -= 1
        if self.duration <= 0:
            self.is_poisoned = False
            print(f'{player.name} is no longer poisoned!')
    # endregion


class Stun(StatusEffect):
    """
    Class for managing stun duration.
    """

    # region Constructor
    def __init__(self, duration: int) -> None:
        """
        Initializes a Stun instance with a duration.
        :param duration: The number of rounds to stun the player for.
        """
        super().__init__(duration)
    # endregion

    # region Methods
    def handle(self, player: 'Character') -> None:
        """
        If the stun effect is active, decreases the duration and returns true.
        @param player: the player to gather information from.
        @return: True if the stun was active, False otherwise.
        """
        print(f'{player.name} is stunned and their turn is skipped!')
        self.duration -= 1
        if self.duration <= 0:
            print(f'{player.name} is no longer stunned!')
    # endregion
