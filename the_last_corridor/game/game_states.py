"""
Definição dos Estados do Jogo THE LAST CORRIDOR.
Controla o fluxo entre Menu, Labirinto, Jumpscare, Boot e Desktop Virtual.
"""

from enum import Enum, auto


class GameState(Enum):
    MAIN_MENU = auto()
    MAZE = auto()
    MAZE_PAUSE = auto()
    FINAL_JUMPSCARE = auto()
    INTERMISSION_CRY = auto()
    PHASE2 = auto()
    ORB_JUMPSCARE = auto()
    BOOT_SEQUENCE = auto()
    DESKTOP = auto()
    SETTINGS = auto()
    CREATOR_PANEL = auto()
    JUMPSCARE_TEST = auto()
    VICTORY = auto()
