from action import *
from character import Character


# region Megumi
class DivineDogs(Attack):
    """
    Summons shikigami that act as swift and relentless hunting beasts that track and attack his enemies.
    """

    def __init__(self) -> None:
        super().__init__(25,
                         "Divine Dogs",
                         self.__doc__,
                         "Devour!")


class RabbitEscape(Defend):
    """
    Creates a shield for escape by surrounding himself with thousands of rabbit shikigami.
    """

    def __init__(self) -> None:
        super().__init__("Rabbit Escape", self.__doc__, 9, 14)


class Mahoraga(SpecialMove):
    """
    Summons the shadow Mahoraga who is able to adapt to techniques and deal massive damage.
    Deals 25 damage to each player negating defense and heals 20hp.
    """

    def __init__(self) -> None:
        super().__init__("Mahoraga",
                         self.__doc__,
                         "With this treasure, I summon Eight-Handled Sword, Divergent Sila, Divine General Mahoraga.",
                         5)

    def apply(self, targets: list[Character]) -> None:
        """
        Applies 25 damage to each player negating defense and heals 20hp.
        :param targets: The list of other characters
        :return: None
        """
        for target in targets:
            damage: int = 25 # Negates defense
            target.hp -= damage
            if not target.is_alive():
                print(f"{target.name} was eliminated by {self.name}.")
            else:
                print(f"{target.name} was damaged for {damage} damage.")


class Megumi(Character):
    """
    https://jujutsu-kaisen.fandom.com/wiki/Megumi_Fushiguro
    """

    def __init__(self) -> None:
        super().__init__("Megumi Fushiguro", 110, DivineDogs(), RabbitEscape(), Mahoraga())

    def special(self, targets: list[Character], turn: int) -> bool:
        if super().special(targets, turn):
            self.hp += 20
            return True
        else:
            return False

# endregion
