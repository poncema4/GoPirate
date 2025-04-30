from action import *
from character import Character


# region SUKUNA
class Dismantle(Attack):
    """
    Slashes opponents with cursed energy capable of cutting through anything with precision.
    """

    def __init__(self):
        super().__init__(35,
                         "Dismantle",
                         self.__doc__,
                         "You are nothing but a fish on my chopping board.")


class FallingBlossomEmotion(Defend):
    """
    An application of cursed energy that automatically repels anything it touches.
    """

    def __init__(self):
        super().__init__('Falling Blossom Emotion', self.__doc__, 7, 10)


class MalevolentShrine(SpecialMove):
    """
    Creates an open barrier where dismantle and cleave continually cut everything within a massive radius.
    Deals 30 damage to each player negating defense.
    """

    def __init__(self):
        super().__init__("Malevolent Shrine",
                         self.__doc__,
                         "This is divine punishment. " +
                         "Domain Expansion. Malevolent Shrine.",
                         6)

    def apply(self, targets: list[Character]) -> None:
        """
        Damages each target for 30 damage negating defense.
        :param targets: The list of other characters.
        :return: None
        """
        for target in targets:
            damage: int = 30 # Negates defense
            target.hp -= damage
            if not target.is_alive():
                print(f"{target.name} was eliminated by {self.name}.")
            else:
                print(f"{target.name} was damaged for {damage} damage.")


class Sukuna(Character):
    """
    https://jujutsu-kaisen.fandom.com/wiki/Sukuna
    """

    def __init__(self) -> None:
        super().__init__("Ryomen Sukuna", 140, Dismantle(), FallingBlossomEmotion(), MalevolentShrine())
