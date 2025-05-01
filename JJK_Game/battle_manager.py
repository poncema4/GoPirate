import sys
import os
sys.path.append(os.path.dirname(__file__))

import time
from character import Character
from user_interface import get_valid_input, clear_output, slow_print

class BattleManager:
    """
    Manages player selection, turns, and how the battle is progressing
    """

    # region Constructor
    def __init__(self, available_players: list[Character]) -> None:
        """
        Initializes the battle manager with empty list of players, and a turn counter
        """
        self.__available_players: list[Character] = available_players
        self.__players: list[Character] = []
        self.__turn: int = 0


    def __str__(self) -> str:
        alive_players: list[Character] = [p for p in self.__players if p.is_alive()]
        print(alive_players)
        result = ''
        for player in alive_players:
            poison_status: str = ''
            stun_status: str = ''

            if player.poison.is_active():
                poison_status = (f'Poison\n'
                                 f' - Damage: {player.poison.damage} hp\n'
                                 f' - Duration: {player.poison.duration} rounds\n')

            if player.stun.is_active():
                stun_status = 'Stunned\n'

            result += (f'{str(player)}\n'
                        f'{poison_status}'
                        f'{stun_status}\n')
        return result
    # endregion

    # region Methods
    def select_players(self) -> None:
        """
        Allows each player to choose their character.
        :return: None
        """
        print("Choose your character:")
        for i, character in enumerate(self.__available_players, start=1):
            print(f"{i}: " + character.get_description())
            
        for i in range(len(self.__previously_alive)):
            choice: int = get_valid_input(f"Player {i + 1} pick your character: ",
                                          "Invalid option, please choose again.",
                                          [character.name for character in self.__available_players])
            chosen: Character = self.__available_players[choice]
            self.__players.append(chosen)
            self.__available_players.remove(chosen)
            clear_output()

    def play_turn(self) -> None:
        """
        Determines whose turn it is depending on the order they chose their character
        :return: None
        """
        self.__turn += 1 # Increment the turn

        self.__previously_alive = {player for player in self.__players if player.is_alive()}

        for player in self.__players:
            print('-' * 60)
            # If the player is not alive skip their turn
            if not player.is_alive():
                continue
            # Remove the defense boost if it is active
            player.handle_defense_boost()
            # Deal poison damage if it is active
            player.handle_poison()
            # If the player was eliminated by poison or is stunned then skip their turn
            if not player.is_alive() or player.handle_stun():
                continue
            # Else let them choose an action
            self.handle_player_actions(player)
            # If one player remains then exit the loop
            if self.is_battle_over():
                break

    def handle_player_actions(self, player: Character) -> None:
        """
        Let's the user select an action for their turn and applies it.
        :param player: The player whose turn it is.
        :return: None
        """
        print(f"{player.name}'s turn!")
        choices: list[str] = ['Attack', 'Defend', 'Special Move']
        choice: int = get_valid_input('Choose your action: ',
                                      'Invalid option, please choose again.',
                                      choices)
        if choice == 0:
            target = self.choose_target(player)
            player.attack(target)
        elif choice == 1:
            player.defend()
        elif choice == 2:
            other_players: list[Character] = [p for p in self.__players if p is not player and p.is_alive()]
            if not player.special(other_players, self.__turn):
                self.handle_player_actions(player)

    def is_battle_over(self) -> bool:
        """
        Determines if the battle is over based on the number of players alive.
        :return: True if there is one player alive, false otherwise.
        """
        return sum(p.is_alive() for p in self.__players) == 1

    def choose_target(self, attacker: Character) -> Character:
        """
        Prompts the player to select a valid target out of the alive players to attack or use their special move on
        :param attacker: The player who is attacking.
        :return: The chosen target character
        """
        alive_players = [player for player in self.__players if player.is_alive() and player is not attacker]
        print("Choose a target: ")
        choice: int = get_valid_input("Enter target number: ",
                                      "Invalid choice. Please select a valid target.",
                                      alive_players)
        return alive_players[choice]

    def round_recap(self) -> None:
        """
        Prints a recap of the current state of the game, including player's HP, poison status, stun status,
        and whether any players died that round.
        :return: None
        """
        slow_print(f'Round {self.__turn} recap!')
        print('-' * 60)

        alive_players = {p for p in self.__players if p.is_alive()}
        dead_players = self.__previously_alive - alive_players  

        # Print alive players
        for i, player in enumerate(alive_players, start=1):
            print(f" - {player.name} - HP: {player.hp}")

        # Print dead players if any
        if dead_players:
            print("\nThe following players were eliminated this round: ")
            for player in dead_players:
                print(f" - {player.name}")

        input('\nPress enter to continue...\n')

    def start_battle(self) -> None:
        """
        Starts the battle and will continue until one player remains.
        :return: None
        """
        self.select_players()
        print("\nTime to show what real Jujutsu really is...")
        while not self.is_battle_over():
            print(f'Round {self.__turn + 1}')
            self.play_turn()
            time.sleep(2)
            clear_output()
            self.round_recap()

        winner = next(player for player in self.__players if player.is_alive())
        print(f"{winner.name} is the chosen one.")
    # endregion
