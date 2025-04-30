from action import *
from character import Character
import random


# region Nobara
class Hairpin(Attack):
    """
    Plants multiple nails into a surface and detonates them simultaneously, causing large-scale destruction.
    """

    def __init__(self) -> None:
        super().__init__(27,
                         "Hairpin",
                         self.__doc__,
                         "Hairpin!—Hope you like surprises.")


class StrawDoll(Defend):
    """
    Transmits damage into a straw doll to avoid taking a direct hit.
    """

    def __init__(self) -> None:
        super().__init__("Straw Doll", self.__doc__, 14, 14)


class Resonance(SpecialMove):
    """
    Drives a nail into a straw doll linked to her opponents, transmitting poison damage to them.
    Randomly poisons alive players for 1-3 moves.
    """

    def __init__(self) -> None:
        super().__init__("Resonance",
                         self.__doc__,
                         "No matter where you run, Resonance will find you.",
                         4)

    def poison_duration_rng(self, n: int) -> list[int]:
        """
        Creates a random list of numbers 1-3.
        :param n: The length of the list.
        :return: List of random ints.
        """
        return [random.randint(1, 3) for _ in range(n)]

    def poison_targets(self, poison_list: list[int], targets: list[Character]) -> None:
        """
        Poisons the given targets based on the given list of ints.
        :param poison_list: List of ints containing durations to poison targets
        :param targets: The list of other characters.
        :return: None
        """
        for poison_duration, target in zip(poison_list, targets):
            target.poison.duration = poison_duration
            print(f'{target.name} was poisoned by {self.name} for {poison_duration} turns.')

    def apply(self, defenders: list[Character]) -> None:
        """
        Randoml poisons targets.
        :param defenders: The list of other chracters.
        :return: None
        """
        poison_list: list[int] = self.poison_duration_rng(len(defenders))
        self.poison_targets(poison_list, defenders)


class Nobara(Character):
    """
    https://jujutsu-kaisen.fandom.com/wiki/Nobara_Kugisaki
                         SpecialMove("Straw Doll Technique", self.straw_doll, 2))
    """

    def __init__(self) -> None:
        super().__init__("Nobara Kugisaki", 130, Hairpin(), StrawDoll(), Resonance())

# endregion
