from hex.tools.game_over_state import GameOverState
from hex.tools.board import Board
from ..ai_heuristic import Heuristic
import numpy as np


LOSE = 1000
WHITE = 0
BLACK = 1
IMPLEMENTATION_OFFSET = 1
EMPTY = 0


class DijkstraHex(Heuristic):
    """
    Dijkstra's algorithm for Hex game heuristic.
    """

    def evaluate(self, player: int, board: Board, depth=0) -> int:
        """Evaluates board connectivity for Dijkstra's algorithm."""

        oopenent = 1 if player == 0 else 0
        is_over, winner = self._is_game_over(board)
        if is_over:
            if winner == player:
                return 10000 - depth
            else:
                return -10000 - depth
        return self.get_dijkstra_score(
            oopenent, board) - self.get_dijkstra_score(player, board)

    def get_dijkstra_score(self, player: int, board: Board) -> int:
        """
        Calculates the Dijkstra score for a player on the board.
        """
        dim = board.get_dim()
        scores = np.array([[LOSE for _ in range(dim)] for _ in range(dim)])
        # Start updating at one side of the board
        updated = np.array([[True for _ in range(dim)] for _ in range(dim)])

        # Alignment of color (black = left->right so (1,0))
        # Alignment of color (white = up->down so (0,1))
        alignment = (0, 1) if player == WHITE else (1, 0)

        for i in range(
                dim):  # Iterate over the first row or column based on alignment
            newcoord = tuple([i * j for j in alignment])
            # Convert (row, col) to a single index
            index = newcoord[0] * dim + newcoord[1]
            updated[newcoord[0]][newcoord[1]] = False
            space_value = board.get_space_value(
                index)  # Use the single index here
            if space_value == player + IMPLEMENTATION_OFFSET:  # If same color --> path starts at 0
                scores[newcoord[0]][newcoord[1]] = 0
            elif space_value == EMPTY:  # If empty --> costs 1 move to use this path
                scores[newcoord[0]][newcoord[1]] = 1
            else:  # If other color --> can't use this path
                scores[newcoord[0]][newcoord[1]] = LOSE

        scores = self.dijkstra_update(player, scores, updated, board)

        # Calculate results from the "other side" of the board
        if alignment == (0, 1):  # WHITE: up-to-down alignment
            results = [scores[dim - 1][i]
                       for i in range(dim)]  # Last row, all columns
        else:  # BLACK: left-to-right alignment
            results = [scores[i][dim - 1]
                       for i in range(dim)]  # Last column, all rows

        best_result = min(results)

        return best_result  # Return minimum distance to get current score

    def dijkstra_update(self, player, scores, updated, board: Board):
        """
        Updates the given Dijkstra scores array for the given color.
        """
        dim = board.get_dim()
        updating = True
        while updating:
            updating = False
            for i, row in enumerate(scores):  # Go over rows
                for j, point in enumerate(row):  # Go over points
                    if not updated[i][j]:
                        # Convert (i, j) to a single index for get_neighbors
                        index = i * dim + j
                        neighborcoords = board.get_neighbors(
                            index)  # Use single index here
                        for neighborcoord in neighborcoords:
                            # Convert the single index neighborcoord back to
                            # (row, col)
                            target_coord = (
                                neighborcoord //
                                dim,
                                neighborcoord %
                                dim)
                            path_cost = LOSE  # Default cost
                            target_value = board.get_space_value(
                                neighborcoord)  # Use single index here
                            if target_value == EMPTY:  # If empty --> costs 1 move to use this path
                                path_cost = 1
                            elif target_value == player + IMPLEMENTATION_OFFSET:  # If same color --> path starts at 0
                                path_cost = 0
                            if scores[target_coord[0]][target_coord[1]
                                                       ] > scores[i][j] + path_cost:  # If new best path
                                scores[target_coord[0]][target_coord[1]
                                                        ] = scores[i][j] + path_cost  # Update score
                                # Mark neighbor for update
                                updated[target_coord[0]
                                        ][target_coord[1]] = False
                                updating = True  # Ensure next loop is started
        return scores

    def _is_game_over(self, board: Board) -> tuple[bool, int]:
        """
        Check if the game is over and return the winner.

        Parameters
        ----------
        board : Board
            The current state of the game board.

        Returns
        -------
        tuple[bool, int]
            - bool: True if the game is over, False otherwise.
            - int: The winner (0 for white, 1 for black), or -1 if no winner.
        """
        board_value = board.has_connection()
        if board_value == GameOverState.WHITE_WON:
            return True, 0  # White won
        elif board_value == GameOverState.BLACK_WON:
            return True, 1  # Black won
        return False, -1  # No winner

    def __str__(self):
        return "Dijkstra"
