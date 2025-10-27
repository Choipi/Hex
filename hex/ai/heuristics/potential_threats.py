import random
from hex.tools.board import Board
from hex.tools.game_over_state import GameOverState
from ..ai_heuristic import Heuristic


# Constants for players
WHITE = 1
BLACK = 2


class PotentialThreatsHeuristic(Heuristic):
    """
    A heuristic evaluation function based on potential and threats.
    This heuristic evaluates the board by calculating the player's potential
    to win and the threats posed by the opponent.
    """

    def evaluate(self, player: int, board: Board, depth=0) -> int:
        """
        Evaluate the board state for the given player.

        Args:
            player (int): The player to evaluate for (1 for WHITE, 2 for BLACK)
            board (Board): The current game board

        Returns:
            int: A heuristic score representing the board's favorability
                 for the given player
        """
        # Check if the game is over
        is_over, winner = self._is_game_over(board)
        if is_over:
            return 10000 - depth if winner == player else -10000 - depth

        # Determine the opponent
        opponent = WHITE if player == BLACK else BLACK

        # Calculate potential and threats for both players
        player_potential = self._calculate_potential(board, player)
        opponent_potential = self._calculate_potential(board, opponent)
        player_threats = self._calculate_threats(board, player)
        opponent_threats = self._calculate_threats(board, opponent)

        # Weights for tuning
        W1 = 4.0  # Weight for player's potential
        W2 = 3.0  # Weight for blocking opponent's potential
        W3 = 2.0  # Weight for player's threats
        W4 = 2.0  # Weight for blocking opponent's threats

        # Combine the scores
        player_score = W1 * player_potential - W2 * opponent_potential + \
            W3 * player_threats - W4 * opponent_threats

        return player_score

    def _calculate_potential(self, board: Board, player: int) -> int:
        """
        Calculate the potential for the given player.

        Args:
            board (Board): The current game board
            player (int): The player to calculate potential for

        Returns:
            int: The potential score for the player
        """
        size = board.get_dim()
        potential = 0

        for x in range(size):
            for y in range(size):
                position = (chr(ord('a') + x), y + 1)
                if board.get_space_value(position) == player:
                    # Add established connections
                    potential += self._count_connections(
                        board, position, player)
                elif board.get_space_value(position) == 0:  # Empty space
                    # Add possible connections
                    potential += self._count_possible_connections(
                        board, position, player)

        return potential

    def _calculate_threats(self, board: Board, player: int) -> int:
        """
        Calculate the threats for the given player.

        Args:
            board (Board): The current game board
            player (int): The player to calculate threats for

        Returns:
            int: The threats score for the player
        """
        size = board.get_dim()
        threats = 0

        for x in range(size):
            for y in range(size):
                position = (chr(ord('a') + x), y + 1)
                if board.get_space_value(position) == 0:  # Empty space
                    # Add possible connections for empty spaces
                    threats += self._count_possible_connections(
                        board, position, player)

        return threats

    def _count_connections(
            self,
            board: Board,
            position: tuple,
            player: int) -> int:
        """
        Count established connections for the given player.

        Args:
            board (Board): The current game board
            position (tuple): The position to evaluate
            player (int): The player to evaluate for

        Returns:
            int: The number of established connections
        """
        connections = 0
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1)]

        for dx, dy in directions:
            neighbor = (chr(ord(position[0]) + dx), position[1] + dy)
            if self._is_valid_position(
                    board, neighbor) and board.get_space_value(neighbor) == player:
                connections += 1

        return connections

    def _count_possible_connections(
            self,
            board: Board,
            position: tuple,
            player: int) -> int:
        """
        Count possible connections for the given player.

        Args:
            board (Board): The current game board
            position (tuple): The position to evaluate
            player (int): The player to evaluate for

        Returns:
            int: The number of possible connections
        """
        possible_connections = 0
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1)]

        for dx, dy in directions:
            neighbor = (chr(ord(position[0]) + dx), position[1] + dy)
            if self._is_valid_position(
                    board, neighbor) and board.get_space_value(neighbor) == player:
                possible_connections += 1

        return possible_connections

    def _is_valid_position(self, board: Board, position: tuple) -> bool:
        """
        Check if a position is within the board bounds.

        Args:
            board (Board): The current game board
            position (tuple): The position to check

        Returns:
            bool: True if the position is valid, False otherwise
        """
        size = board.get_dim()
        return 'a' <= position[0] < chr(
            ord('a') + size) and 1 <= position[1] <= size

    def _is_game_over(self, board):
        return super()._is_game_over(board)

    def __str__(self):
        return "Potential threats"
