from battle_manager import BattleManager
from character_factory import CharacterFactory
from character import Character

if __name__ == "__main__":
    character_names: list[str] = ['Gojo', 'Sukuna', 'Megumi', 'Nanami', 'Nobara']
    factory: CharacterFactory = CharacterFactory()
    characters: list[Character] = [factory.create_character(name) for name in character_names]
    BattleManager(characters).start_battle()
