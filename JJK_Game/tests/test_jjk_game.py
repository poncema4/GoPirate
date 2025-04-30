import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from status_effects import StatusEffect
from character_factory import CharacterFactory
from character import *
from characters.gojo import *
from characters.sukuna import *
from characters.megumi import *
from characters.nanami import *
from characters.nobara import *
from typing import cast
import pytest

# region Fixtures
@pytest.fixture
def characters() -> dict[str, Character]:
    character_names: list[str] = ['Gojo', 'Sukuna', 'Megumi', 'Nanami', 'Nobara']
    factory: CharacterFactory = CharacterFactory()
    character_dict: dict[str, Character] = {name: factory.create_character(name) for name in character_names}
    return character_dict


@pytest.fixture
def char_list(characters) -> list[Character]:
    return [c for c in characters.values()]


@pytest.fixture
def attacks() -> dict[str, Attack]:
    return {
        'Red': Red(),
        'Dismantle': Dismantle(),
        'Divine Dogs': DivineDogs(),
        'Ratio Technique': RatioTechnique(),
        'Hairpin': Hairpin()
    }


@pytest.fixture
def defenses() -> dict[str, Defend]:
    return {
        'Limitless': Limitless(),
        'Falling Blossom Emotion': FallingBlossomEmotion(),
        'Rabbit Escape': RabbitEscape(),
        'Block': Block(),
        'Straw Doll': StrawDoll()
    }


@pytest.fixture
def specials() -> dict[str, SpecialMove]:
    return {
        'Unlimited Void': UnlimitedVoid(),
        'Malevolent Shrine': MalevolentShrine(),
        'Mahoraga': Mahoraga(),
        'Overtime': Overtime(),
        'Resonance': Resonance()
    }


# endregion

# region Action Tests
# region Abstract Base Class Tests
def test_action_getters(attacks, defenses, specials):
    red: Action = attacks.get('Red')  # Attack
    limitless: Action = defenses.get('Limitless')  # Defend
    unlimited_void: Action = specials.get('Unlimited Void')  # Special

    # Name
    assert red.name == 'Red'
    assert limitless.name == 'Limitless'
    assert unlimited_void.name == 'Unlimited Void'

    # Description
    assert red.description == """
    Amplifies the repelling force of Limitless using reversed cursed energy, creating a powerful shockwave that violently repels anything in its path.
    """
    assert limitless.description == """
    Recursively divides the space between the attack and defender into a convergent series of fractional distances.
    """
    assert unlimited_void.description == """
    Traps opponents in an empty space with an overwhelming amount of information.
    Deals 25 damage to each player and has a 50% chance to stun each opponent.
    """

    # Voice Line
    assert red.voiceline == "Convergence, divergence... What do you think happens when one touches this void?"
    assert limitless.voiceline == ""
    assert unlimited_void.voiceline == ("It's ironic isn't it? When granted everything you can't do anything. " +
                                        "Domain Expansion. Unlimited Void.")


# endregion

# region Attack Tests
def test_attack_getters(attacks):
    # Damage
    assert attacks.get('Red').damage == 28
    assert attacks.get('Dismantle').damage == 35
    assert attacks.get('Divine Dogs').damage == 25
    assert attacks.get('Ratio Technique').damage == 28
    assert attacks.get('Hairpin').damage == 27


def test_attack_action(capsys, characters) -> None:
    # Set up attackers
    attacker1: Character = characters.get('Gojo')
    assert attacker1.attack_damage == 28
    attacker2: Character = characters.get('Nobara')
    assert attacker2.attack_damage == 27
    # Set up defenders
    defender1: Character = characters.get('Sukuna')
    assert defender1.defense == 7
    assert defender1.hp == 140
    defender2: Character = characters.get('Megumi')
    assert defender2.defense == 9
    defender2.hp = 1
    assert defender2.hp == 1

    initial_hp_1: int = defender1.hp
    initial_hp_2: int = defender2.hp
    attacker1.attack(defender1)
    attacker2.attack(defender2)

    damage1: int = max(attacker1._attack_move.damage - defender1.defense, 0)
    damage2: int = max(attacker2._attack_move.damage - defender2.defense, 0)

    assert defender1.hp == initial_hp_1 - damage1
    assert defender2.hp == initial_hp_2 - damage2

    captured: str = capsys.readouterr().out

    expected_output_1 = f"{attacker1.name} attacks {defender1.name} for {damage1} damage!\n"
    expected_output_1 += f"{defender1.name} has {defender1.hp} HP remaining.\n"

    expected_output_2 = f"{attacker2.name} attacks {defender2.name} for {damage2} damage!\n"
    expected_output_2 += f"{defender2.name} has {defender2.hp} HP remaining.\n"
    expected_output_2 += f"{defender2.name} has been defeated!\n"

    assert expected_output_1 in captured
    assert expected_output_2 in captured


# endregion

# region Defend Tests
def test_defender_getters(defenses) -> None:
    limitless: Defend = defenses.get('Limitless')
    falling_blossom_emotion: Defend = defenses.get('Falling Blossom Emotion')
    rabbit_escape: Defend = defenses.get('Rabbit Escape')
    block: Defend = defenses.get('Block')
    straw_doll: Defend = defenses.get('Straw Doll')

    # Boost
    assert limitless.boost == 15
    assert falling_blossom_emotion.boost == 10
    assert rabbit_escape.boost == 14
    assert block.boost == 12
    assert straw_doll.boost == 14

    # Base Defense
    assert limitless.base_defense == 8
    assert falling_blossom_emotion.base_defense == 7
    assert rabbit_escape.base_defense == 9
    assert block.base_defense == 10
    assert straw_doll.base_defense == 14

    # Current Defense
    assert limitless.current_defense == 8
    assert falling_blossom_emotion.current_defense == 7
    assert rabbit_escape.current_defense == 9
    assert block.current_defense == 10
    assert straw_doll.current_defense == 14


def test_defend_setters(defenses):
    limitless: Defend = defenses.get('Limitless')
    falling_blossom_emotion: Defend = defenses.get('Falling Blossom Emotion')
    rabbit_escape: Defend = defenses.get('Rabbit Escape')

    # Current Defense
    limitless.current_defense = 1
    falling_blossom_emotion.current_defense = 2
    rabbit_escape.current_defense = 3

    assert limitless.current_defense == 1
    assert falling_blossom_emotion.current_defense == 2
    assert rabbit_escape.current_defense == 3


def test_defend_is_boost_active(defenses):
    limitless: Defend = defenses.get('Limitless')
    falling_blossom_emotion: Defend = defenses.get('Falling Blossom Emotion')
    rabbit_escape: Defend = defenses.get('Rabbit Escape')

    # Not active at the start
    assert not limitless.is_boost_active()
    assert not falling_blossom_emotion.is_boost_active()
    assert not rabbit_escape.is_boost_active()

    # Active after defending
    assert limitless.apply() is None
    assert falling_blossom_emotion.apply() is None
    assert rabbit_escape.apply() is None

    assert limitless.is_boost_active()
    assert falling_blossom_emotion.is_boost_active()
    assert rabbit_escape.is_boost_active()

    # Not active after it is reset
    limitless.current_defense = limitless.base_defense
    falling_blossom_emotion.current_defense = falling_blossom_emotion.base_defense
    rabbit_escape.current_defense = rabbit_escape.base_defense

    assert not limitless.is_boost_active()
    assert not falling_blossom_emotion.is_boost_active()
    assert not rabbit_escape.is_boost_active()


def test_defend_action(capsys, characters) -> None:
    # Set up attackers
    attacker1: Character = characters.get('Nanami')
    assert attacker1.attack_damage == 28
    attacker2: Character = characters.get('Sukuna')
    assert attacker2.attack_damage == 35
    # Set up defenders
    defender1: Character = characters.get('Gojo')
    assert defender1.defense == 8
    assert defender1.hp == 120
    assert defender1._defense_move.boost == 15
    defender2: Character = characters.get('Nobara')
    assert defender2.defense == 14
    assert defender2.hp == 130
    assert defender2._defense_move.boost == 14

    defender1.defend()
    defender2.defend()
    assert defender1.defense == defender1._defense_move.base_defense + defender1._defense_move.boost
    assert defender2.defense == defender2._defense_move.base_defense + defender2._defense_move.boost
    assert defender1._defense_move.is_boost_active()
    assert defender2._defense_move.is_boost_active()

    initial_hp_1 = defender1.hp
    initial_hp_2 = defender2.hp
    attacker1.attack(defender1)
    attacker2.attack(defender2)

    damage1 = max(attacker1.attack_damage - defender1.defense, 0)
    damage2 = max(attacker2.attack_damage - defender2.defense, 0)

    assert defender1.hp == initial_hp_1 - damage1
    assert defender2.hp == initial_hp_2 - damage2

    captured = capsys.readouterr()

    expected_output_1 = f"{defender1.name} strengthens themselves, adding {defender1._defense_move.boost} defense.\n"
    expected_output_2 = f"{defender2.name} strengthens themselves, adding {defender2._defense_move.boost} defense.\n"

    assert expected_output_1 in captured.out
    assert expected_output_2 in captured.out

    defender1.defend()
    defender2.defend()

    captured = capsys.readouterr()

    expected_already_defending_1 = f"{defender1.name} is already defending this turn.\n"
    expected_already_defending_2 = f"{defender2.name} is already defending this turn.\n"

    assert expected_already_defending_1 in captured.out
    assert expected_already_defending_2 in captured.out


# endregion

# region Special Moves
# region Getters and Setters
def test_special_move_getters(specials):
    unlimited_void: SpecialMove = specials.get('Unlimited Void')
    mahoraga: SpecialMove = specials.get('Mahoraga')

    # Cooldown
    assert unlimited_void.cooldown == 5
    assert mahoraga.cooldown == 5

    # Last Used
    assert unlimited_void.last_used == 0
    assert mahoraga.last_used == 0


def test_special_move_setters(specials):
    unlimited_void: SpecialMove = specials.get('Unlimited Void')
    mahoraga: SpecialMove = specials.get('Mahoraga')

    # Cooldown
    unlimited_void.cooldown = 10
    mahoraga.cooldown = 20

    assert unlimited_void.cooldown == 10
    assert mahoraga.cooldown == 20

    # Last Used
    unlimited_void.last_used = 1
    mahoraga.last_used = 2

    assert unlimited_void.last_used == 1
    assert mahoraga.last_used == 2


# endregion

# region Methods
def test_special_move_is_available(specials):
    unlimited_void: SpecialMove = specials.get('Unlimited Void')
    resonance: SpecialMove = specials.get('Resonance')

    # Not available at the start
    assert not unlimited_void.is_available(0)
    assert not resonance.is_available(0)

    # Available after the set cooldown
    assert unlimited_void.is_available(5)
    assert resonance.is_available(4)

    # Not available after it is used
    unlimited_void.last_used = 5
    resonance.last_used = 4

    assert not unlimited_void.is_available(6)
    assert not resonance.is_available(5)

    # Available again after the cooldown has passed
    assert unlimited_void.is_available(10)
    assert resonance.is_available(8)


# endregion

# region Implementations
def test_unlimited_void(capsys, char_list, characters, specials):
    unlimited_void: UnlimitedVoid = cast(UnlimitedVoid, specials.get('Unlimited Void'))
    gojo: Character = characters.get('Gojo')
    stun_list: list[bool] = [False, True, False, True, False]
    char_list[0].hp = 1
    original_hps: list[int] = [c.hp for c in char_list]

    # Properties
    assert unlimited_void.name == 'Unlimited Void'
    assert unlimited_void.description == """
    Traps opponents in an empty space with an overwhelming amount of information.
    Deals 25 damage to each player and has a 50% chance to stun each opponent.
    """
    assert unlimited_void.cooldown == 5
    assert unlimited_void.voiceline == ("It's ironic isn't it? When granted everything you can't do anything. " +
                                        "Domain Expansion. Unlimited Void.")

    # Stun Effect
    unlimited_void.stun_targets(stun_list, char_list)
    captured: str = capsys.readouterr().out
    for is_stunned, c in zip(stun_list, char_list):
        if is_stunned:
            assert c.stun.is_active()
            assert f'{c.name} was stunned.' in captured
        else:
            assert not c.stun.is_active()

    # Availability and Cooldown
    assert unlimited_void.is_available(100)
    assert not unlimited_void.is_available(0)
    assert not gojo.special(char_list, 0)
    captured: str = capsys.readouterr().out
    assert 'Unlimited Void is on cooldown! Choose another action.' in captured

    # Damage
    assert gojo.special(char_list, 100)
    captured: str = capsys.readouterr().out
    for c, og_hp in zip(char_list, original_hps):
        if og_hp + c.defense > 25:
            assert c.hp == og_hp - 25 + c.defense
            assert f'{c.name} was damaged for {25 - c.defense} damage.' in captured
        else:
            assert c.hp <= 0
            assert f'{c.name} was eliminated by Unlimited Void.' in captured

    # Voice Line
    assert unlimited_void.voiceline in captured


def test_malevolent_shrine(capsys, char_list, characters, specials):
    malevolent_shrine: MalevolentShrine = cast(MalevolentShrine, specials.get('Malevolent Shrine'))
    sukuna: Character = characters.get('Sukuna')
    char_list[0].hp = 1
    original_hps: list[int] = [c.hp for c in char_list]

    # Properties
    assert malevolent_shrine.name == 'Malevolent Shrine'
    assert malevolent_shrine.description == """
    Creates an open barrier where dismantle and cleave continually cut everything within a massive radius.
    Deals 30 damage to each player negating defense.
    """
    assert malevolent_shrine.cooldown == 6
    assert malevolent_shrine.voiceline == 'This is divine punishment. Domain Expansion. Malevolent Shrine.'

    # Availability and Cooldown
    assert malevolent_shrine.is_available(100)
    assert not malevolent_shrine.is_available(0)
    assert not sukuna.special(char_list, 0)
    captured: str = capsys.readouterr().out
    assert 'Malevolent Shrine is on cooldown! Choose another action.' in captured

    # Damage
    assert sukuna.special(char_list, 100)
    captured: str = capsys.readouterr().out
    for og_hp, c in zip(original_hps, char_list):
        if og_hp > 30:
            assert c.hp == og_hp - 30
            assert f'{c.name} was damaged for 30 damage.' in captured
        else:
            assert c.hp <= 0
            assert f'{c.name} was eliminated by Malevolent Shrine.' in captured
    assert not char_list[0].is_alive()

    # Voice Line
    assert malevolent_shrine.voiceline in captured


def test_mahoraga(capsys, characters, char_list, specials):
    mahoraga: Mahoraga = cast(Mahoraga, specials.get('Mahoraga'))
    megumi = characters.get('Megumi')
    megumi_og_hp: int = megumi.hp
    other_characters: list[Character] = [
        c for c in char_list if not isinstance(c, Megumi)
    ]
    other_characters[0].hp = 1
    original_hps: list[int] = [c.hp for c in other_characters]

    # Properties
    assert mahoraga.name == 'Mahoraga'
    assert mahoraga.description == """
    Summons the shadow Mahoraga who is able to adapt to techniques and deal massive damage.
    Deals 25 damage to each player negating defense and heals 20hp.
    """
    assert mahoraga.cooldown == 5
    assert mahoraga.voiceline == "With this treasure, I summon Eight-Handled Sword, Divergent Sila, Divine General Mahoraga."

    # Availability and Cooldown
    assert mahoraga.is_available(100)
    assert not mahoraga.is_available(0)
    assert not megumi.special(other_characters, 0)
    captured: str = capsys.readouterr().out
    assert 'Mahoraga is on cooldown! Choose another action.' in captured

    # Damage
    megumi.special(other_characters, 100)
    captured: str = capsys.readouterr().out
    for og_hp, c in zip(original_hps, other_characters):
        if og_hp > 25:
            assert c.hp == og_hp - 25
            assert f'{c.name} was damaged for 25 damage.' in captured
        else:
            assert c.hp <= 0
            assert f'{c.name} was eliminated by Mahoraga.' in captured
    assert not char_list[0].is_alive()

    # Regeneration
    assert megumi.hp == megumi_og_hp + 20

    # Voice Line
    assert mahoraga.voiceline in captured


def test_overtime(capsys, char_list, characters, specials):
    overtime: Overtime = cast(Overtime, specials.get('Overtime'))
    nanami: Character = characters.get('Nanami')
    stun_list: list[bool] = [False, True, False, True, False]
    char_list[0].hp = 1
    original_hps: list[int] = [c.hp for c in char_list]

    # Properties
    assert overtime.name == 'Overtime'
    assert overtime.description == """
    A self-imposed restriction that temporarily increases power and speed.
    Has a 25% chance to stun each opponent or will deal 20 damage.
    """
    assert overtime.cooldown == 3
    assert overtime.voiceline == "I dislike working overtime... but when I do, I give it my all."

    # Availability and Cooldown
    assert overtime.is_available(100)
    assert not overtime.is_available(0)
    assert not nanami.special(char_list, 0)
    captured: str = capsys.readouterr().out
    assert 'Overtime is on cooldown! Choose another action.' in captured

    # Stun and Damage
    overtime.stun_and_damage_targets(stun_list, char_list)
    captured: str = capsys.readouterr().out
    for is_stunned, og_hp, c in zip(stun_list, original_hps, char_list):
        if is_stunned:
            assert c.stun.is_active()
            assert f'{c.name} was stunned by Overtime.' in captured
        elif og_hp + c.defense > 20:
            assert c.hp == og_hp - 20 + c.defense
            assert f'{c.name} was damaged for {20 - c.defense} damage.' in captured
        else:
            assert c.hp <= 0
            assert f'{c.name} was eliminated by Overtime.' in captured

    # Voice Line
    nanami.special(char_list, 100)
    captured: str = capsys.readouterr().out
    assert overtime.voiceline in captured


def test_resonance(capsys, char_list, characters, specials):
    resonance: Resonance = cast(Resonance, specials.get('Resonance'))
    nobara: Character = characters.get('Nobara')
    poison_list: list[int] = [1, 2, 3, 1, 2]

    # Properties
    assert resonance.name == 'Resonance'
    assert resonance.description == """
    Drives a nail into a straw doll linked to her opponents, transmitting poison damage to them.
    Randomly poisons alive players for 1-3 moves.
    """
    assert resonance.cooldown == 4
    assert resonance.voiceline == "No matter where you run, Resonance will find you."

    # Availability and Cooldown
    assert resonance.is_available(100)
    assert not resonance.is_available(0)
    assert not nobara.special(char_list, 0)
    captured: str = capsys.readouterr().out
    assert 'Resonance is on cooldown! Choose another action.' in captured

    # Poison
    resonance.poison_targets(poison_list, char_list)
    captured: str = capsys.readouterr().out
    for poison_duration, c in zip(poison_list, char_list):
        assert c.poison.is_active()
        assert c.poison.duration == poison_duration
        assert f'{c.name} was poisoned by Resonance for {poison_duration} turns.' in captured

    # Voice Line
    nobara.special(char_list, 100)
    captured: str = capsys.readouterr().out
    assert resonance.voiceline in captured


# endregion
# endregion
# endregion

# region Status Effects Tests
# region Abstract Base Class
# region Getters and Setters
def test_status_effect_getters():
    poison: StatusEffect = Poison(10, 3)
    stun: StatusEffect = Stun(1)

    # Duration
    assert poison.duration == 3
    assert stun.duration == 1


def test_status_effect_setters():
    poison: StatusEffect = Poison(10, 3)
    stun: StatusEffect = Stun(1)

    # Duration
    poison.duration = 10
    assert poison.duration == 10

    stun.duration = 10
    assert stun.duration == 10


# endregion

# region Methods
def test_status_effect_is_active():
    poison: StatusEffect = Poison(10, 3)
    stun: StatusEffect = Stun(1)

    assert poison.is_active()
    assert stun.is_active()

    poison.duration = 0
    stun.duration = -1

    assert not poison.is_active()
    assert not stun.is_active()


# endregion

# endregion

# region Poison
# region Methods
def test_poison_handle_poison(capsys, characters):
    poison: Poison = Poison(10, 0)
    gojo: Character = characters.get('Gojo')
    captured: str

    # If the given player is not poisoned then nothing happens
    initial_hp: int = gojo.hp
    assert poison.handle(gojo) is None
    captured = capsys.readouterr().out
    assert captured == ''
    assert gojo.hp == initial_hp

    # If the given player is damaged then they take damage and a message is printed
    poison.duration = 3
    assert poison.is_active()
    poison.handle(gojo)
    captured = capsys.readouterr().out
    assert gojo.hp == initial_hp - poison.damage
    assert poison.duration == 3 - 1
    assert 'Satoru Gojo is poisoned! They take 10 damage.\n' in captured

    # If the given player is killed by poison it prints a message
    gojo.hp = 1
    assert poison.is_active()
    poison.handle(gojo)
    captured = capsys.readouterr().out
    assert gojo.hp == 1 - poison.damage
    assert poison.duration == 2 - 1
    assert 'Satoru Gojo was eliminated by poison!\n' in captured

    # If the poison duration goes to 0 a message is printed
    gojo.hp = 11
    assert poison.is_active()
    poison.handle(gojo)
    captured = capsys.readouterr().out
    assert gojo.hp == 11 - poison.damage
    assert poison.duration == 1 - 1
    assert 'Satoru Gojo is no longer poisoned!\n' in captured


# endregion
# endregion

# region Stun
# region Methods
def test_stun_handle_stun(capsys, characters):
    stun: Stun = Stun(1)
    gojo: Character = characters.get('Gojo')
    captured: str

    # Stunned test
    # Removes the stun
    assert stun.is_active()
    stun.handle(gojo)
    captured = capsys.readouterr().out
    assert 'Satoru Gojo is stunned and their turn is skipped!\n' in captured
    assert 'Satoru Gojo is no longer stunned!\n' in captured
    assert stun.duration == 1 - 1 == 0
    assert not stun.is_active()


# endregion
# endregion
# endregion

# region Character Tests
# region Getters and Setters
def test_character_getters(characters):
    gojo: Character = characters.get('Gojo')
    sukuna: Character = characters.get('Sukuna')
    megumi: Character = characters.get('Megumi')
    nanami: Character = characters.get('Nanami')
    nobara: Character = characters.get('Nobara')

    # Name
    assert gojo.name == 'Satoru Gojo'
    assert sukuna.name == 'Ryomen Sukuna'
    assert megumi.name == 'Megumi Fushiguro'
    assert nanami.name == 'Kento Nanami'
    assert nobara.name == 'Nobara Kugisaki'

    # Hp
    assert gojo.hp == 120
    assert sukuna.hp == 140
    assert megumi.hp == 110
    assert nanami.hp == 120
    assert nobara.hp == 130

    # Attack Damage
    assert gojo.attack_damage == 28
    assert sukuna.attack_damage == 35
    assert megumi.attack_damage == 25
    assert nanami.attack_damage == 28
    assert nobara.attack_damage == 27

    # Defense
    assert gojo.defense == 8
    assert sukuna.defense == 7
    assert megumi.defense == 9
    assert nanami.defense == 10
    assert nobara.defense == 14

    assert gojo.defend() is None
    assert sukuna.defend() is None
    assert megumi.defend() is None
    assert nanami.defend() is None
    assert nobara.defend() is None

    assert gojo.defense == 8 + 15
    assert sukuna.defense == 7 + 10
    assert megumi.defense == 9 + 14
    assert nanami.defense == 10 + 12
    assert nobara.defense == 14 + 14

    # Special Move
    assert isinstance(gojo.special_move, UnlimitedVoid)
    assert isinstance(sukuna.special_move, MalevolentShrine)
    assert isinstance(megumi.special_move, Mahoraga)
    assert isinstance(nanami.special_move, Overtime)
    assert isinstance(nobara.special_move, Resonance)

    # Stun
    assert isinstance(gojo.stun, Stun)
    assert isinstance(sukuna.stun, Stun)
    assert isinstance(megumi.stun, Stun)
    assert isinstance(nanami.stun, Stun)
    assert isinstance(nobara.stun, Stun)

    # Poison
    assert isinstance(gojo.poison, Poison)
    assert isinstance(sukuna.poison, Poison)
    assert isinstance(megumi.poison, Poison)
    assert isinstance(nanami.poison, Poison)
    assert isinstance(nobara.poison, Poison)


def test_character_setters(characters):
    gojo: Character = characters.get('Gojo')
    sukuna: Character = characters.get('Sukuna')
    megumi: Character = characters.get('Megumi')
    nanami: Character = characters.get('Nanami')
    nobara: Character = characters.get('Nobara')

    # Hp
    gojo.hp = 1
    sukuna.hp = 2
    megumi.hp = 3
    nanami.hp = 4
    nobara.hp = 5

    assert gojo.hp == 1
    assert sukuna.hp == 2
    assert megumi.hp == 3
    assert nanami.hp == 4
    assert nobara.hp == 5


# endregion

# region Methods
def test_character_str(char_list):
    assert str(char_list[0]) == 'Satoru Gojo (HP: 120)'
    assert str(char_list[1]) == 'Ryomen Sukuna (HP: 140)'
    assert str(char_list[2]) == 'Megumi Fushiguro (HP: 110)'
    assert str(char_list[3]) == 'Kento Nanami (HP: 120)'
    assert str(char_list[4]) == 'Nobara Kugisaki (HP: 130)'


def test_character_is_alive(characters):
    gojo: Character = characters.get('Gojo')
    sukuna: Character = characters.get('Sukuna')

    # Alive at the start
    assert gojo.is_alive()
    assert sukuna.is_alive()

    # Not alive when hp is 0 or less
    gojo.hp = 0
    sukuna.hp = -1
    assert not gojo.is_alive()
    assert not sukuna.is_alive()


def test_character_get_description(characters):
    assert (characters.get('Gojo').get_description() ==
            ('Satoru Gojo (HP: 120)\n'
             'Attack: Red\n'
             '  - Amplifies the repelling force of Limitless using reversed cursed energy, '
             'creating a powerful shockwave that violently repels anything in its path.\n'
             '  - Damage: 28 HP\n'
             'Defense: Limitless\n'
             '  - Recursively divides the space between the attack and defender into a '
             'convergent series of fractional distances.\n'
             '  - Base: 8 HP\n'
             '  - Boost: 15 HP\n'
             'Special Move: Unlimited Void\n'
             '  - Traps opponents in an empty space with an overwhelming amount of '
             'information.\n'
             '    Deals 25 damage to each player and has a 50% chance to stun each '
             'opponent.\n'
             '  - Cooldown: 5 turns\n'))

    assert (characters.get('Sukuna').get_description() ==
            ('Ryomen Sukuna (HP: 140)\n'
             'Attack: Dismantle\n'
             '  - Slashes opponents with cursed energy capable of cutting through anything '
             'with precision.\n'
             '  - Damage: 35 HP\n'
             'Defense: Falling Blossom Emotion\n'
             '  - An application of cursed energy that automatically repels anything it '
             'touches.\n'
             '  - Base: 7 HP\n'
             '  - Boost: 10 HP\n'
             'Special Move: Malevolent Shrine\n'
             '  - Creates an open barrier where dismantle and cleave continually cut '
             'everything within a massive radius.\n'
             '    Deals 30 damage to each player negating defense.\n'
             '  - Cooldown: 6 turns\n'))


def test_character_handle_defense_boost(characters):
    gojo: Character = characters.get('Gojo')
    sukuna: Character = characters.get('Sukuna')

    # Does not change defense if defense boost is not active
    assert not gojo._defense_move.is_boost_active()
    assert not sukuna._defense_move.is_boost_active()

    gojo_initial_defense: int = gojo.defense
    sukuna_initial_defense: int = sukuna.defense

    gojo.handle_defense_boost()
    sukuna.handle_defense_boost()

    assert gojo.defense == gojo_initial_defense
    assert sukuna.defense == sukuna_initial_defense

    # Resets defense if boost is active
    gojo.defend()
    sukuna.defend()

    gojo_initial_defense: int = gojo.defense
    sukuna_initial_defense: int = sukuna.defense

    gojo.handle_defense_boost()
    sukuna.handle_defense_boost()

    assert gojo.defense < gojo_initial_defense
    assert sukuna.defense < sukuna_initial_defense
    assert gojo.defense == gojo._defense_move.base_defense
    assert sukuna.defense == sukuna._defense_move.base_defense


def test_character_handle_poison(capsys, characters):
    gojo: Character = characters.get('Gojo')
    initial_hp: int = gojo.hp
    captured: str

    # If the player is not poisoned nothing happens
    assert not gojo.poison.is_active()
    gojo.handle_poison()
    assert gojo.hp == initial_hp

    # If the player is poisoned they take damage and a message is printed
    gojo.poison.duration = 3
    gojo.poison.damage = 10
    assert gojo.poison.is_active()
    gojo.handle_poison()
    captured = capsys.readouterr().out
    assert gojo.hp == initial_hp - 10
    assert gojo.poison.duration == 3 - 1
    assert 'Satoru Gojo is poisoned! They take 10 damage.\n' in captured

    # If the player is killed by poison it prints a message
    gojo.hp = 1
    assert gojo.poison.is_active()
    gojo.handle_poison()
    captured = capsys.readouterr().out
    assert gojo.hp == 1 - 10
    assert gojo.poison.duration == 3 - 2
    assert 'Satoru Gojo was eliminated by poison!\n' in captured

    # If the poison duration goes to 0 a message is printed
    gojo.hp = 11
    assert gojo.poison.is_active()
    gojo.handle_poison()
    captured = capsys.readouterr().out
    assert gojo.hp == 11 - 10
    assert gojo.poison.duration == 3 - 3
    assert 'Satoru Gojo is no longer poisoned!\n' in captured


def test_character_handle_stun(capsys, characters):
    gojo: Character = characters.get('Gojo')
    sukuna: Character = characters.get('Sukuna')
    captured: str

    # Stunned test
    # Removes the stun and returns True
    gojo.stun.duration = 1
    assert gojo.stun.is_active()
    assert gojo.handle_stun()
    captured = capsys.readouterr().out
    assert 'Satoru Gojo is stunned and their turn is skipped!\n' in captured
    assert 'Satoru Gojo is no longer stunned!\n' in captured
    assert gojo.stun.duration == 1 - 1
    assert not gojo.stun.is_active()

    # Not stunned test
    # Returns false and prints nothing
    assert not sukuna.stun.is_active()
    assert not sukuna.handle_stun()
    captured = capsys.readouterr().out
    assert captured == ''
# endregion

# region Character Factory Tests
def test_character_factory(capsys):
    factory: CharacterFactory = CharacterFactory()

    assert isinstance(factory.create_character('Gojo'), Gojo)
    assert isinstance(factory.create_character('Sukuna'), Sukuna)
    assert isinstance(factory.create_character('Megumi'), Megumi)
    assert isinstance(factory.create_character('Nanami'), Nanami)
    assert isinstance(factory.create_character('Nobara'), Nobara)

    with pytest.raises(ValueError) as exc_info:
        factory.create_character('Brysen')
    assert str(exc_info.value) == "Character 'Brysen' does not exist in the factory."

    with pytest.raises(ValueError) as exc_info:
        factory.create_character('Marco')
    assert str(exc_info.value) == "Character 'Marco' does not exist in the factory."

# endregion
# endregion
