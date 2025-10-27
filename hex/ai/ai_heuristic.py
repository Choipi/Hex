from hex.tools.board import Board
from hex.tools.game_over_state import GameOverState


class Heuristic:

    def evaluate(self, player: int, board: Board) -> int:
        pass

    def _is_game_over(self, board: Board) -> tuple[bool, int]:
        match board.has_connection():
            case GameOverState.BLACK_WON:
                return (True, 1)
            case GameOverState.WHITE_WON:
                return (True, 0)
            case GameOverState.NO_WINNER:
                return (False, 2)
            case _:
                raise ValueError("Unknown Value")
