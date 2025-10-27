from ..exploration_algorithm import Exploration_algorithm
from hex.tools.board import Board
from hex.tools.game_over_state import GameOverState
from ..ai_heuristic import Heuristic
from random import choice


class Random_exploration(Exploration_algorithm):
    def __init__(self, heuristic: Heuristic, depth: int, time_limit: float):
        super().__init__(heuristic, depth, time_limit)
        self.__heuristic = heuristic
        self.__depth = depth
        self.__time_limit = time_limit

    def get_move(self, player: int, board: Board) -> tuple[str, int]:
        return choice(board.get_legal_moves())

    def __str__(self):
        return "Random Exploration"
