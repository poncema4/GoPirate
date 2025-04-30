from action import *
from character import Character
import random


# region GOJO
class Red(Attack):
    """
    Amplifies the repelling force of Limitless using reversed cursed energy, creating a powerful shockwave that violently repels anything in its path.
    """

    def __init__(self):
        super().__init__(28, "Red", self.__doc__,
                         "Convergence, divergence... What do you think happens when one touches this void?")


class Limitless(Defend):
    """
    Recursively divides the space between the attack and defender into a convergent series of fractional distances.
    """

    def __init__(self):
        super().__init__("Limitless", self.__doc__, 8, 15)


class UnlimitedVoid(SpecialMove):
    """
    Traps opponents in an empty space with an overwhelming amount of information.
    Deals 25 damage to each player and has a 50% chance to stun each opponent.
    """

    def __init__(self):
        super().__init__("Unlimited Void",
                         self.__doc__,
                         "It's ironic isn't it? When granted everything you can't do anything. " +
                         "Domain Expansion. Unlimited Void.",
                         5)

    def create_stun_rng(self, n: int) -> list[bool]:
        """
        Randomly creates a list of size n with each element having a 50% to be True of False
        :param n: The size of the list.
        :return: List of bools
        """
        return [True if random.randint(0, 1) == 1 else False for _ in range(n)]

    def stun_targets(self, stun_list: list[bool], targets: list[Character]) -> None:
        """
        Applies stuns to the targets based on the givne stun list.
        :param stun_list: The list of bools determining whether or not to stun the player
        :param targets: The list of other characters
        :return: None
        """
        for to_stun, target in zip(stun_list, targets):
            if to_stun:
                target.stun.duration = 1
                print(f'{target.name} was stunned.')

    def apply(self, targets: list[Character]) -> None:
        """
        Deals 25 damage to each player and applies stuns randomly.
        :param targets: The list of other characters
        :return: None
        """
        for target in targets:
            damage: int = max(0, 25 - target.defense)
            target.hp -= damage
            if not target.is_alive():
                print(f'{target.name} was eliminated by {self._name}.')
            else:
                print(f'{target.name} was damaged for {damage} damage.')

        stun_list: list[bool] = self.create_stun_rng(len(targets))
        self.stun_targets(stun_list, targets)


class Gojo(Character):
    """
    https://jujutsu-kaisen.fandom.com/wiki/Satoru_Gojo
    """

    def __init__(self) -> None:
        super().__init__("Satoru Gojo", 120, Red(), Limitless(), UnlimitedVoid())

# endregion
