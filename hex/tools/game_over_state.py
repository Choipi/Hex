from enum import Enum

class GameOverState(Enum):
    """ States the game can be when it has finished. """
    NO_WINNER = 0
    WHITE_WON = 1
    BLACK_WON = 2
