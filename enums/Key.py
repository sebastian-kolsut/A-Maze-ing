from enum import IntEnum


class Key(IntEnum):
    """Enum for key codes used in the game."""
    K_B = 98
    K_D = 100
    K_G = 103
    K_L = 108
    K_J = 106
    K_I = 105
    K_K = 107
    K_W = 119
    K_S = 115
    K_A = 97
    K_N = 110
    K_ESCAPE = 65307
    K_BACKSPACE = 65288


class Numpad(IntEnum):
    """Enum for key codes of numpad used in the game."""
    EIGHT = 65431
    TWO = 65433
    SIX = 65432
    FOUR = 65430
    PLUS = 65451
    MINUS = 65453


class Arrow(IntEnum):
    """Enum for key codes of arrow keys used in the game."""
    LEFT = 65361
    UP = 65362
    RIGHT = 65363
    DOWN = 65364
