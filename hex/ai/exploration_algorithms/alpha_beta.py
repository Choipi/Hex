from random import choice
from hex.tools.board import Board
from hex.tools.game_over_state import GameOverState
from ..exploration_algorithm import Exploration_algorithm
from ..ai_heuristic import Heuristic
import time

INF = 1000000


class Alpha_Beta_pruning(Exploration_algorithm):

    def __init__(self, heuristic: Heuristic, depth: int, time_limit: float):
        super().__init__(heuristic, depth, time_limit)
        self.__heuristic = heuristic
        self.__depth = depth
        self.__time_limit = time_limit
        self.best_move = -1

    def get_move(self, player: int, board: Board):
        max_depth = self.__depth
        start = time.time()
        _, best_move = self.alphabeta_nega(
            player, -INF, INF, max_depth, board, start)
        if best_move is None:
            best_move = choice(board.get_legal_moves())
        return best_move

    def alphabeta_nega(
            self,
            player: int,
            alpha: int,
            beta: int,
            depth: int,
            board: Board,
            start_time: float):
        """
        Implements the Alpha-Beta pruning algorithm with negamax optimization for decision-making in a two-player game.
        Args:
            player (int): The current player (0 or 1).
            alpha (int): The alpha value representing the best score that the maximizing player can guarantee.
            beta (int): The beta value representing the best score that the minimizing player can guarantee.
            depth (int): The maximum depth to explore in the game tree.
            board (Board): The current state of the game board.
            start_time (float): The starting time of the algorithm to enforce time constraints.
        Returns:
            tuple: A tuple containing:
                - best_score (int): The best score achievable for the current player.
                - best_move (Any): The move associated with the best score.
        """
        if time.time() - start_time > self.__time_limit:
            return None, None
        next_player = 1 if player == 0 else 0
        best_move = None
        best_value = -INF  # reset best_value

        if depth <= 0 or board.has_connection() != GameOverState.NO_WINNER:
            best_value = self.__heuristic.evaluate(player, board, depth)
            best_move = None
            return best_value, best_move
        else:
            moves = board.get_legal_moves()
            for move in moves:
                board.add_move(move, player)
                new_value, _ = self.alphabeta_nega(
                    next_player, -beta, -alpha, depth - 1, board, start_time)

                if new_value is None:
                    board.remove_move(move, player)
                    return best_value, best_move

                new_value = -new_value

                if new_value > best_value:
                    best_value = new_value
                    best_move = move
                board.remove_move(move, player)

                alpha = max(alpha, best_value)
                if alpha >= beta:
                    break
        return best_value, best_move

    def set_heuristic(self, heuristic: Heuristic):
        self.__heuristic = heuristic

    def set_depth(self, depth: int):
        self.__depth = depth

    def __str__(self):
        return f"Alpha-Beta Pruning with depth {self.__depth} and time limit {self.__time_limit}"
