import time
from hex.tools.board import Board
from hex.tools.game_over_state import GameOverState
from ..exploration_algorithm import Exploration_algorithm
from ..ai_heuristic import Heuristic

WIN = 1000000


class Minimax(Exploration_algorithm):
    def __init__(self, heuristic: Heuristic, depth: int, time_limit: float):
        super().__init__(heuristic, depth, time_limit)
        self.__heuristic = heuristic
        self.__max_depth = depth
        self.__time_limit = time_limit
        self.__move_stats = {}  # Dictionary to store move statistics

    def get_move(self, player, board):
        """
        Get the best move for the given player using the minimax algorithm.

        Parameters
        ----------
        player : int
            The player for whom the move is being calculated (0 for white, 1 for black).
        board : Board
            The current state of the game board.

        Returns
        -------
        tuple[str, int]
            The best move for the player as a tuple (column, row).
        """
        best_move = None
        best_value = -WIN
        start = time.time()
        self.__move_stats = {}  # Reset stats for this call

        for move in board.get_legal_moves():
            board.add_move(move, player)
            move_value = self.minimax(
                board, self.__max_depth - 1, player, 1 - player, start)
            board.remove_move(move, player)

            # Update stats dictionary
            self.__move_stats[move] = move_value

            if move_value > best_value:
                best_value = move_value
                best_move = move

            if time.time() - start >= self.__time_limit:
                if best_move is None:
                    best_move = move
                break
        print(self.__move_stats)
        return best_move

    def minimax(
            self,
            board: Board,
            depth: int,
            o_player: int,
            c_player: int,
            start_time: float):
        """
        Perform the minimax search to evaluate the best move.

        Parameters
        ----------
        board : Board
            The current state of the game board.
        depth : int
            The remaining depth to explore.
        o_player : int
            The original player (maximizing player).
        c_player : int
            The current player (alternates between maximizing and minimizing).
        start_time : float
            The starting time of the search to enforce the time limit.

        Returns
        -------
        int
            The evaluation score of the board.
        """
        if time.time() - start_time >= self.__time_limit:
            # Return extreme values if time runs out
            return -WIN if c_player == o_player else WIN

        if depth == 0:
            # Use the heuristic to evaluate the board if the depth limit is
            # reached
            return self.__heuristic.evaluate(o_player, board, depth)

        if c_player == o_player:  # Maximizing player
            max_value = -WIN
            for move in board.get_legal_moves():
                board.add_move(move, c_player)
                move_value = self.minimax(
                    board, depth - 1, o_player, 1 - c_player, start_time)
                max_value = max(max_value, move_value)
                board.remove_move(move, c_player)
            return max_value
        else:  # Minimizing player
            min_value = WIN
            for move in board.get_legal_moves():
                board.add_move(move, c_player)
                move_value = self.minimax(
                    board, depth - 1, o_player, 1 - c_player, start_time)
                min_value = min(min_value, move_value)
                board.remove_move(move, c_player)
            return min_value

    def get_stats(self):
        """
        Get the statistics of the moves evaluated in the last call to get_move.

        Returns
        -------
        dict
            A dictionary where keys are moves and values are their evaluation scores.
        """
        return self.__move_stats

    def set_heuristic(self, heuristic: Heuristic):
        self.__heuristic = heuristic

    def set_depth(self, depth: int):
        self.__max_depth = depth

    def __str__(self):
        return "Minimax"
