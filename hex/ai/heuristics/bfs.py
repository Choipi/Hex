import numpy as np
from collections import deque
from hex.tools.board import Board
from hex.tools.game_over_state import GameOverState
from ..ai_heuristic import Heuristic


class BfsHeuristic(Heuristic):
    """
    A heuristic evaluation function for Hex boards using the two-distance algorithm.

    This heuristic calculates the shortest path from one edge to the opposite edge
    for each player and combines them to evaluate board positions.

    The lower the distance, the better the position for that player.
    """

    def evaluate(self, player: int, board: Board, depth) -> int:
        """
        Evaluate the board position for the given player.

        Parameters
        ----------
        player: int
            The player to evaluate for (0 for white, 1 for black)
        board: Board
            The Hex board to evaluate

        Returns
        -------
        int
            A value indicating how good the position is for the player.
            Higher values are better for the player.
        """
        # Check if game is over
        is_over, winner = self._is_game_over(board)
        if is_over:
            return 1000 - depth if winner == player else -1000 - depth

        # Calculate distances for both players
        white_distance = self._calculate_distance(0, board)
        black_distance = self._calculate_distance(1, board)

        # Normalize the distances based on board size
        dim = board.get_dim()
        normalized_white =  white_distance#1.0 - (white_distance / (2 * dim))
        normalized_black = black_distance#1.0 - (black_distance / (2 * dim))

        # Convert to integer score with appropriate scaling
        if player == 0:  # White
            score = int(100 * (normalized_white - normalized_black))
        else:  # Black
            score = int(100 * (normalized_black - normalized_white))

        return score

    def _calculate_distance(self, player: int, board: Board) -> int:
        """
        Calculate the shortest path distance for a player from one edge to the opposite edge.

        Parameters
        ----------
        player: int
            The player to calculate distance for (0 for white, 1 for black)
        board: Board
            The Hex board to evaluate

        Returns
        -------
        int
            The shortest path distance. 0 means the player has won.
        """
        # Convert player value to board representation (1 for white, 2 for
        # black)
        player_value = player + 1
        dim = board.get_dim()

        # Create a distance grid
        distances = np.full((dim, dim), float('inf'))

        # Initialize queue for BFS
        queue = deque()

        # For white player: connect left edge to right edge (horizontal)
        if player == 2:
            # Initialize distances for the left edge cells
            for i in range(dim):
                pos = ('a', i + 1)
                space_value = board.get_space_value(pos)
                if space_value in (0, player_value):
                    distances[i][0] = 0 if space_value == player_value else 1
                    queue.append((i, 0, distances[i][0]))

            # BFS to find shortest paths
            while queue:
                row, col, dist = queue.popleft()

                # If we've reached the right edge, we're done
                if col == dim - 1:
                    return dist

                # Check neighbors
                for dr, dc in self._get_neighbors(row, col):
                    new_row, new_col = row + dr, col + dc
                    if 0 <= new_row < dim and 0 <= new_col < dim:
                        pos = (chr(ord('a') + new_col), new_row + 1)
                        cell_value = board.get_space_value(pos)
                        new_dist = dist if cell_value == player_value else dist + 1

                        if new_dist < distances[new_row][new_col] and cell_value != 3 - player_value:
                            distances[new_row][new_col] = new_dist
                            queue.append((new_row, new_col, new_dist))

        # For black player: connect top edge to bottom edge (vertical)
        else:
            # Initialize distances for the top edge cells
            for j in range(dim):
                pos = (chr(ord('a') + j), 1)
                space_value = board.get_space_value(pos)
                if space_value in (0, player_value):
                    distances[0][j] = 0 if space_value == player_value else 1
                    queue.append((0, j, distances[0][j]))

            # BFS to find shortest paths
            while queue:
                row, col, dist = queue.popleft()

                # If we've reached the bottom edge, we're done
                if row == dim - 1:
                    return dist

                # Check neighbors
                for dr, dc in self._get_neighbors(row, col):
                    new_row, new_col = row + dr, col + dc
                    if 0 <= new_row < dim and 0 <= new_col < dim:
                        pos = (chr(ord('a') + new_col), new_row + 1)
                        cell_value = board.get_space_value(pos)
                        new_dist = dist if cell_value == player_value else dist + 1

                        if new_dist < distances[new_row][new_col] and cell_value != 3 - player_value:
                            distances[new_row][new_col] = new_dist
                            queue.append((new_row, new_col, new_dist))

        # If no path is found, return the maximum distance
        return 2 * dim  # A value larger than any possible path

    def _get_neighbors(self, row, col):
        """
        Get the neighboring cells in a Hex grid.
        In a hex grid, each cell has 6 neighbors.

        Parameters
        ----------
        row: int
            Row of the cell
        col: int
            Column of the cell

        Returns
        -------
        list
            List of (row_diff, col_diff) for each neighbor
        """
        # Hex grid neighbors (6 directions)
        return [
            (-1, 0),  # North
            (-1, 1),  # Northeast
            (0, 1),   # East
            (1, 0),   # South
            (1, -1),  # Southwest
            (0, -1)   # West
        ]

    def __str__(self):
        return "BFS heuristic"
