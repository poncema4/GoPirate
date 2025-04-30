from action import *
from character import Character
import random

# region Nanami
class RatioTechnique(Attack):
    """
    Divides anything he touches into a 7:3 ratio, marking the weaker portion as a critical weak point for a guaranteed enhanced strike.
    """

    def __init__(self) -> None:
        super().__init__(28,
                         "Ratio",
                         self.__doc__,
                         "Even with just a blunt sword, a decisive hit at the weak point is lethal.")


class Block(Defend):
    """
    Basically hardening of cursed energy to negate damage.
    """

    def __init__(self) -> None:
        super().__init__("Block", self.__doc__, 10, 12)


class Overtime(SpecialMove):
    """
    A self-imposed restriction that temporarily increases power and speed.
    Has a 25% chance to stun each opponent or will deal 20 damage.
    """

    def __init__(self) -> None:
        super().__init__("Overtime",
                         self.__doc__,
                         "I dislike working overtime... but when I do, I give it my all.",
                         3)

    def create_stun_rng(self, n: int) -> list[bool]:
        """
        Creates a list of random bools with a 25% to be True and 75% chance to be False.
        :param n: The length of the list
        :return: List of bools.
        """
        return [True if random.randint(0, 3) == 1 else False for _ in range(n)]

    def stun_and_damage_targets(self, stun_list: list[bool], targets: list[Character]) -> None:
        """
        Either damages a player for 20 damage or stuns the player.
        :param stun_list: List of bools determining whether or not to stun the player.
        :param targets: The list of other characters.
        :return: None
        """
        for i in range(0, len(stun_list)):
            target: Character = targets[i]
            if stun_list[i]:
                target.stun.duration = 1
                print(f'{target.name} was stunned by {self.name}.')
            else:
                damage: int = max(0, 20 - target.defense)
                target.hp -= damage
                if not target.is_alive():
                    print(f"{target.name} was eliminated by {self.name}.")
                else:
                    print(f"{target.name} was damaged for {damage} damage.")

    def apply(self, targets: list[Character]) -> None:
        """
        Either damages a player for 20 damage or stuns them.
        :param targets: The list of other characters.
        :return: None
        """
        stun_list: list[bool] = self.create_stun_rng(len(targets))
        self.stun_and_damage_targets(stun_list, targets)


class Nanami(Character):
    """
    https://jujutsu-kaisen.fandom.com/wiki/Kento_Nanami
    """

    def __init__(self) -> None:
        super().__init__("Kento Nanami", 120, RatioTechnique(), Block(), Overtime())


# endregion
