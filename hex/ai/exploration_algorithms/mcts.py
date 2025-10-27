from typing import Union, Optional, List, Dict, Tuple
import math
import random
import time
from copy import deepcopy

from hex.tools.game_over_state import GameOverState


class MCTSNode:
    """A node in the Monte Carlo Tree Search

    Attributes
    ----------
    state: Board
        The game state at this node
    parent: Optional[MCTSNode]
        The parent node, or None if this is the root
    move: Optional[Tuple[str, int]]
        The move that led to this state, or None if this is the root
    children: List[MCTSNode]
        Child nodes
    visits: int
        Number of times this node has been visited
    wins: Dict[int, float]
        Wins for each player (0 for white, 1 for black)
    untried_moves: List[Tuple[str, int]]
        List of moves not yet explored from this node
    player: int
        The player to move in this state
    """

    def __init__(self, state, parent=None, move=None, player=0):
        self.state = state.duplicate_board()
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.wins = {0: 0, 1: 0}
        self.untried_moves = state.get_legal_moves()
        self.player = player  # Player who is about to move

    def select_child(self, exploration_weight=1.41):
        """Select the child with the highest UCB score."""
        for child in self.children:
            if child.state.has_connection() == (
                    GameOverState.WHITE_WON if self.player == 0 else GameOverState.BLACK_WON):
                return child  # Prioritize winning moves

        log_parent_visits = math.log(self.visits) if self.visits > 0 else 0

        def ucb_score(child):
            exploitation = child.wins[self.player] \
                / child.visits if child.visits > 0 else 0
            # Reduce exploration weight for high win rates
            adjusted_exploration_weight = exploration_weight \
                * (1 - exploitation)
            exploration = adjusted_exploration_weight \
                * math.sqrt(log_parent_visits / child.visits) if child.visits > 0 else float('inf')
            return exploitation + exploration

        return max(self.children, key=ucb_score)

    def expand(self):
        """Expand the tree by adding a new child node"""
        if not self.untried_moves:
            return None

        move = random.choice(self.untried_moves)
        self.untried_moves.remove(move)

        # Create a new state by applying the move
        next_state = self.state.duplicate_board()
        next_state.add_move(move, self.player)

        # Next player is the opponent
        next_player = 1 if self.player == 0 else 0

        # Create a new child node
        child = MCTSNode(next_state, parent=self,
                         move=move, player=next_player)
        self.children.append(child)
        return child

    def update(self, result):
        """Update the node statistics"""
        self.visits += 1
        for player in [0, 1]:
            self.wins[player] += result[player]


class MonteCarloTreeSearch:
    """Monte Carlo Tree Search algorithm for Hex game

    Attributes
    ----------
    exploration_weight: float
        The exploration weight for the UCB formula
    time_limit: float
        The time limit for the search in seconds
    max_iterations: int
        The maximum number of iterations for the search
    """

    def __init__(
            self,
            exploration_weight=1.41,
            time_limit=1.0,
            max_iterations=100000):
        """Initialize the MCTS algorithm

        Parameters
        ----------
        exploration_weight: float
            The exploration weight for the UCB formula
        time_limit: float
            The time limit for the search in seconds
        max_iterations: int
            The maximum number of iterations for the search
        """
        self.exploration_weight = exploration_weight
        self.time_limit = time_limit
        self.max_iterations = max_iterations
        self.root = None

    def get_move(self, player, board):
        """Get the best move for the given player and board."""
        # Check for immediate winning moves
        for move in board.get_legal_moves():
            temp_board = board.duplicate_board()
            temp_board.add_move(move, player)
            if temp_board.has_connection() == (
                    GameOverState.WHITE_WON if player == 0 else GameOverState.BLACK_WON):
                return move  # Return the winning move immediately

        # Initialize the root node with the current board state
        self.root = MCTSNode(board, player=player)

        # Run the MCTS search
        result = self.search()
        # print(self.get_stats())
        return result

    def select(self):
        """Select a leaf node using the UCB formula"""
        node = self.root

        # Selection phase - select until we reach a leaf node
        while node.untried_moves == [] and node.children != []:
            node = node.select_child(self.exploration_weight)

        return node

    def expand(self, node):
        """Expand the node by adding a child"""
        return node.expand()

    def simulate(self, node, max_depth=500):
        """Simulate a random game from the node and return the result."""
        state = node.state.duplicate_board()
        player = node.player
        depth = 0

        while state.has_connection() == GameOverState.NO_WINNER and depth < max_depth:
            legal_moves = state.get_legal_moves()
            if not legal_moves:
                break
            move = random.choice(legal_moves)
            state.add_move(move, player)
            player = 1 - player
            depth += 1

        game_over = state.has_connection()
        result = {0: 0, 1: 0}
        if game_over == GameOverState.WHITE_WON:
            result[0] = 1
        elif game_over == GameOverState.BLACK_WON:
            result[1] = 1
        return result

    def backpropagate(self, node, result):
        """Backpropagate the result up the tree"""
        while node is not None:
            node.visits += 1
            node.wins[0] += result[0]  # Update wins for player 0 (white)
            node.wins[1] += result[1]  # Update wins for player 1 (black)
            node = node.parent

    def search(self):
        """Perform the MCTS search and return the best move."""
        start_time = time.time()
        num_iterations = 0

        while (time.time() - start_time < self.time_limit and
               num_iterations < self.max_iterations):
            leaf = self.select()
            game_over = leaf.state.has_connection()

            if game_over.value == 0:  # Game is not over
                if leaf.untried_moves:
                    leaf = self.expand(leaf)
                result = self.simulate(leaf)
                self.backpropagate(leaf, result)

            num_iterations += 1

        if not self.root.children:
            return random.choice(
                self.root.untried_moves) if self.root.untried_moves else None

        # Use visits as a tie-breaker for equal win rates
        best_child = max(self.root.children, key=lambda child: (
            child.wins[self.root.player] / child.visits, child.visits))
        return best_child.move

    def get_stats(self):
        """Get statistics about the search"""
        if not self.root or not self.root.children:
            return "No statistics available"

        stats = []
        total_visits = sum(child.visits for child in self.root.children)

        for child in sorted(
                self.root.children,
                key=lambda c: c.visits,
                reverse=True):
            win_rate = child.wins[self.root.player] \
                / child.visits if child.visits > 0 else 0
            stats.append({
                'move': child.move,
                'visits': child.visits,
                'win_rate': win_rate,
                'probability': child.visits / total_visits if total_visits > 0 else 0
            })

        return stats

    def __str__(self):
        return "Monte Carlo Tree Search"
