from hex.tools.board import Board
from hex.tools.game_over_state import GameOverState
from ..ai_heuristic import Heuristic
import time


class HexBoardHeuristic(Heuristic):
    def evaluate(self, player: int, board: Board, depth=0) -> int:
        """
        Evaluate the board state for the given player.

        Args:
            player (int): The player to evaluate for (0 or 1)
            board (Board): The current game board

        Returns:
            int: A heuristic score representing the board's favorability
                 for the given player
        """
        # Check if the game is over
        is_over, winner = self._is_game_over(board)
        if is_over:
            return 10000 - depth if winner == player else -10000 - depth

        # Check if there are no legal moves
        if not board.get_legal_moves():
            return 0  # Neutral score for no moves

        # Dynamic weight adjustments based on game phase
        total_moves = len(board.get_legal_moves())
        dim = board.get_dim()
        early_game = total_moves > dim * dim * 0.7
        mid_game = dim * dim * 0.3 < total_moves <= dim * dim * 0.7
        late_game = total_moves <= dim * dim * 0.3

        # Adjust weights dynamically
        bridge_weight = 1 if early_game else 1 if mid_game else 1
        path_weight = 2 if early_game else 3 if mid_game else 4
        control_weight = 2 if early_game else 0 if mid_game else 0
        isolation_penalty_weight = 1 if early_game else 2 if mid_game else 3

        # Core evaluation
        bridge_score = self._calculate_bridge_potential(board, player) * bridge_weight
        control_score = self._calculate_board_control(board, player) * control_weight
        path_continuation_score = self._prioritize_path_continuation(board, player) * path_weight
        opponent_penalty = self._evaluate_opponent_threat(board, player)
        isolation_penalty = self._penalize_isolated_stones(board, player) * isolation_penalty_weight

        # Combine scores
        return bridge_score + control_score + path_continuation_score - opponent_penalty- isolation_penalty

    def _calculate_bridge_potential(self, board: Board, player: int) -> int:
        """
        Calculate the bridge potential for the given player.

        Args:
            board (Board): The current game board
            player (int): The player to evaluate for

        Returns:
            int: A score representing the bridge potential
        """
        dim = board.get_dim()
        player_stone = player + 1
        score = 0

        for row in range(dim):
            for col in range(dim):
                index = row * dim + col
                if board.get_space_value(index) == player_stone:
                    for neighbor in board.get_neighbors(index):
                        if board.get_space_value(neighbor) == 0:  # Empty space
                            for bridge_neighbor in board.get_neighbors(neighbor):
                                if bridge_neighbor != index and board.get_space_value(bridge_neighbor) == player_stone:
                                    score += 3  # Reward for potential bridge
                        elif board.get_space_value(neighbor) == 0:  # Virtual connection
                            score += 2  # Reward for creating virtual connection opportunities
        return score

    def _calculate_board_control(self, board: Board, player: int) -> int:
        """
        Calculate the board control for the given player, focusing on critical areas.

        Args:
            board (Board): The current game board
            player (int): The player to evaluate for

        Returns:
            int: A score representing the player's control of critical areas
        """
        dim = board.get_dim()
        player_stone = player + 1
        opponent_stone = 3 - player_stone
        score = 0

        # Define critical areas: center and edges
        center = (dim // 2, dim // 2)
        critical_positions = [center]

        # Add edge positions to critical areas
        for i in range(dim):
            critical_positions.append((0, i))  # Top edge
            critical_positions.append((dim - 1, i))  # Bottom edge
            critical_positions.append((i, 0))  # Left edge
            critical_positions.append((i, dim - 1))  # Right edge

        for row in range(dim):
            for col in range(dim):
                position = row * dim + col
                space_value = board.get_space_value(position)

                if space_value == player_stone:
                    # Reward for controlling critical areas
                    if (row, col) in critical_positions:
                        score += 3  # Reduced weight for critical zones
                    else:
                        score += 1  # General control

                elif space_value == opponent_stone:
                    # Penalize for opponent controlling critical areas
                    if (row, col) in critical_positions:
                        score -= 3  # Reduced penalty for critical zones

        return score

    def _prioritize_path_continuation(self, board: Board, player: int) -> int:
        """
        Reward moves that continue the player's existing path toward their winning edge.

        Args:
            board (Board): The current game board
            player (int): The player to evaluate for

        Returns:
            int: A score representing the benefit of continuing the player's path
        """
        dim = board.get_dim()
        player_stone = player + 1
        score = 0

        for index in range(dim * dim):
            if board.get_space_value(index) == player_stone:
                row, col = divmod(index, dim)

                # Reward proximity to the player's winning edge
                if player == 0:  # White (top-to-bottom)
                    distance_to_goal = dim - 1 - row
                else:  # Black (left-to-right)
                    distance_to_goal = dim - 1 - col
                score += (dim - distance_to_goal) * 3  # Higher reward for being closer

                # Reward connections to neighboring tiles that lead toward the winning edge
                for neighbor in board.get_neighbors(index):
                    neighbor_row, neighbor_col = divmod(neighbor, dim)
                    if board.get_space_value(neighbor) == player_stone:
                        # Ensure the connection is in the correct direction
                        if player == 0 and neighbor_row > row:  # White moving downward
                            score += 20
                        elif player == 1 and neighbor_col > col:  # Black moving rightward
                            score += 20
                        # Reward meaningful connections that extend the path
                        if abs(neighbor_row - row) + abs(neighbor_col - col) == 1:
                            score += 20

        return score

    def _evaluate_opponent_threat(self, board: Board, player: int) -> int:
        """
        Evaluate how close the opponent is to winning and penalize accordingly.

        Args:
            board (Board): The current game board
            player (int): The player to evaluate for

        Returns:
            int: A penalty score based on the opponent's proximity to winning
        """
        opponent = 1 - player
        player_distance = self._calculate_distance_to_win(board, player)
        opponent_distance = self._calculate_distance_to_win(board, opponent)

        # Penalize more if the opponent is closer to winning than the player
        if opponent_distance < player_distance:
            return (player_distance - opponent_distance) * 10
        return 0

    def _calculate_distance_to_win(self, board: Board, player: int) -> int:
        """
        Calculate the shortest distance for the player to win.

        Args:
            board (Board): The current game board
            player (int): The player to evaluate for

        Returns:
            int: The shortest distance to win
        """
        dim = board.get_dim()
        player_stone = player + 1
        visited = set()
        queue = []

        # Initialize the queue with the player's starting edge
        if player == 0:  # White (top-to-bottom)
            for col in range(dim):
                index = col  # Top row indices
                if board.get_space_value(index) in {0, player_stone}:
                    queue.append((index, 0))  # (index, distance)
        else:  # Black (left-to-right)
            for row in range(dim):
                index = row * dim  # Left column indices
                if board.get_space_value(index) in {0, player_stone}:
                    queue.append((index, 0))  # (index, distance)

        # Perform BFS to find the shortest path to the winning edge
        while queue:
            index, distance = queue.pop(0)
            if index in visited:
                continue
            visited.add(index)

            # Check if we've reached the winning edge
            if player == 0 and index // dim == dim - 1:  # White
                return distance
            if player == 1 and index % dim == dim - 1:  # Black
                return distance

            # Add neighbors to the queue
            for neighbor in board.get_neighbors(index):
                if neighbor not in visited and board.get_space_value(neighbor) != 3 - player_stone:
                    queue.append((neighbor, distance + 1))

        # If no path is found, return a large value
        return dim * dim

    def _penalize_isolated_stones(self, board: Board, player: int) -> int:
        """
        Penalize isolated stones that are not connected to any other stones.

        Args:
            board (Board): The current game board
            player (int): The player to evaluate for

        Returns:
            int: A penalty score for isolated stones
        """
        dim = board.get_dim()
        player_stone = player + 1
        penalty = 0

        for index in range(dim * dim):
            if board.get_space_value(index) == player_stone:
                connected = False
                for neighbor in board.get_neighbors(index):
                    if board.get_space_value(neighbor) == player_stone:
                        connected = True
                        break
                if not connected:
                    penalty += 5  # Penalize isolated stones

        return penalty

    def _is_game_over(self, board: Board) -> tuple[bool, int]:
        """
        Check if the game is over and return the winner.
        Args:
            board (Board): The current game board
        Returns:
            tuple[bool, int]: A tuple containing a boolean indicating if the game is over
                              and the winner (0 for player 0, 1 for player 1, -1 for no winner)
        """
        if board.has_connection() == GameOverState.NO_WINNER:
            return False, -1
        elif board.has_connection() == GameOverState.WHITE_WON:
            return True, 0
        elif board.has_connection() == GameOverState.BLACK_WON:
            return True, 1
        else:
            raise ValueError("Invalid game state")

    def __str__(self):
        return "Path oriented"
