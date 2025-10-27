from .ai_heuristic import Heuristic
from hex.tools.board import Board
import time


class Exploration_algorithm:
    def __init__(self, heuristic: Heuristic, depth: int, time_limit: float):
        self.__depth = depth
        self.__heuristic = heuristic
        self.__time_limit = time_limit

    def get_move(self, player: int, board: Board) -> tuple[str, int]:
        pass

    def set_heuristic(self, heuristic: Heuristic):
        self.__heuristic = heuristic

    def set_depth(self, depth: int):
        self.__depth = depth
