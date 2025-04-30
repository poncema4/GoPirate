import os
import time

def clear_output() -> None:
    """
    Clears the output from the console.
    Accounts for Windows and Unix systems.
    :return: None
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def slow_print(s: str, delay: float = 0.02) -> None:
    for c in s:
        print(c, end='', flush=True)
        time.sleep(delay)
    print()

def get_valid_input(message: str, error_message: str, choices: list) -> int:
    """
    Given a list of choices, assures the user picks a valid option without causing an exception.
    :param message: The initial message i.e. 'Choose a ...'
    :param error_message: The message to show when something invalid was chosen
    :param choices: The list of choices for the user to pick from
    :return: The index of the user's choice in the list of choices.
    """
    print(message)
    while True:
        for i, choice in enumerate(choices):
            slow_print(f"    {i + 1}: {choice}")
        try:
            user_input = int(input("")) - 1
            if 0 <= user_input < len(choices):
                return user_input
            else:
                slow_print(error_message)
        except ValueError:
            slow_print(error_message)
