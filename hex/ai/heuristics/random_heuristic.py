from hex.tools.board import Board
from ..ai_heuristic import Heuristic
import random


class Random_Heuristic(Heuristic):

    def evaluate(self, player: int, board: Board, depth=0):
        is_game_over, winner = self._is_game_over(board)
        if is_game_over:
            if player == winner:
                return 100
            else:
                return -100
        else:
            return random.choice(range(-50, 50))

    def __str__(self):
        return "Random"
