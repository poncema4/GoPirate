from JJK_Game.character import Character
from JJK_Game.characters.gojo import Gojo
from JJK_Game.characters.sukuna import Sukuna
from JJK_Game.characters.megumi import Megumi
from JJK_Game.characters.nanami import Nanami
from JJK_Game.characters.nobara import Nobara


class CharacterFactory:
    """
    Factory class to create different character types dynamically.
    """

    # region Constructor
    def __init__(self):
        """
        Creates a dictionary attribute mapping names to character classes.
        """
        self.__character_classes = {
            "Gojo": Gojo,
            "Sukuna": Sukuna,
            "Megumi": Megumi,
            "Nanami": Nanami,
            "Nobara": Nobara
        }
    # endregion

    # region Methods
    def create_character(self, name: str) -> Character:
        """
        Creates a character instance based on the given name.

        :param name: The name of the character class.
        :return: An instance of the specified character.
        :raises ValueError: If the character name is invalid.
        """
        if name in self.__character_classes:
            return self.__character_classes[name]()
        else:
            raise ValueError(f"Character '{name}' does not exist in the factory.")
    # endregion
