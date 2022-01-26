import colorama
from colorama import Fore, Style, Back

RED   = Fore.RED
GREEN = Fore.GREEN
BLUE  = Fore.BLUE
RESET = Style.RESET_ALL

def red(text: str):
    return RED + text + RESET

def green(text: str):
    return GREEN + text + RESET

def blue(text: str):
    return BLUE + text + RESET