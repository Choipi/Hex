import pytest
from hex.tools.game_over_state import GameOverState
from hex.tools.game_state import GameState
from hex.tools.config import Config
from hex.tools.history import History


def translate(letter: str, number: str) -> int:
    """Converts a line number and a column letter to a one dimension index.

    Parameters
    ----------
    letter: str
        String reprensenting the column of the desired move.
    number: str
        String reprensenting the line of the desired move.
    """
    return (int(number) - 1) * 2 + ord(letter) - 97


class DummyBoard:
    def __init__(self, dimension):
        self.dimension = dimension
        self.moves = []  # keep track of moves that have been made

    def check_legal_move(self, move):
        if not isinstance(move, int):
            return False
        if move < 0 or move >= self.dimension * self.dimension:
            return False
        if move in self.moves:
            return False
        return True

# --- Pytest Fixtures ---


@pytest.fixture
def game_state(monkeypatch):
    """
    Create a Game_State instance with a 3x3 board,
    and replace its internal board with DummyBoard.
    """
    config = Config()
    __history=History()
    config.set("board-size", '3')
    config.set("blitz", 'true')
    gs = GameState(config)
    return gs


# --- Tests for get_game_size ---
@pytest.mark.parametrize("dimension", [1, 3, 5])
def test_get_game_dim(dimension):
    """
    Test that the game size is correctly reported.
    """
    config = Config()
    config.set("board-size", str(dimension))
    gs = GameState(config)
    assert gs.get_game_dim() == dimension


# --- Test for get_current_player ---
def test_get_current_player(game_state):
    """
    The initial current player should be 0.
    """
    assert game_state.get_current_player() == 0
    
    
# --- Test for set_current_player ---
def test_get_current_player(game_state):
    """
    Changing player to 1.
    """
    game_state.set_current_player(1)
    assert game_state.get_current_player() == 1
    
# --- Test for get_current_game_round ---
def test_get_current_round(game_state):
    """
    The initial current game round should be 1.
    """
    assert game_state.get_current_game_round() == 1
    
    
# --- Test for get_current_game_round ---
def test_set_current_round(game_state):
    """
    Changing round to 5.
    """
    game_state.set_current_game_round(5)
    assert game_state.get_current_game_round() == 5


# --- Test for get_winner ---
def test_get_winner(game_state):
    """
    Setting white won then testing if get_winner actually tell white are the winner
    """
    assert game_state.is_game_over() == False
    game_state.set_game_over(GameOverState.WHITE_WON)
    assert game_state.is_game_over() == True
    assert game_state.get_winner() == GameOverState.WHITE_WON

# --- Test for set_history ---
def test_set_history(game_state):
    """
    Testing for set_history
    """
    hist=History()
    hist.add_move(1, "O", "a", "1")
    
    assert game_state.set_history(hist) == None

# --- Test for reset_game_state ---
def test_reset_game_state(game_state):
    """
    Test that reset_game_state really reset.
    """
    config = Config()
    config.set("board-size", '4')
    gs = GameState(config)
    gs2=GameState(config)
    gs.play_move(('a', 1))
    gs.play_move(('b', 1))
    gs.reset_game_state()
    assert gs.get_current_game_round() == 1
    assert gs.get_current_player() == 0
    assert gs.are_board_equals(gs2.get_board())



# --- Test for are_board_equals ---
def test_are_board_equals(game_state):
    """
    Test that are_board_equals really reset.
    """
    config = Config()
    config.set("board-size", '4')
    gs = GameState(config)
    gs2=GameState(config)
    gs.play_move(('a', 1))
    gs2.play_move(('a', 1))

    assert gs.are_board_equals(gs2.get_board())
    gs.reset_game_state()
    assert not(gs.are_board_equals(gs2.get_board()))

# --- Tests for board_to_string ---
def test_board_to_string(game_state):
    """
    Test that board_to_string toggles between 0 and 1.
    """

    assert game_state.board_to_string() == "  a b c\n   o o o\n1 x . . . x \n 2 x . . . x \n  3 x . . . x \n       o o o "
# --- Tests for get_black_time ---
def test_get_black_time(game_state):
    """
    Test that get_black_time is 30 minutes (1800 seconds).
    """

    assert game_state.get_black_time() == 1800
# --- Tests for get_white_time ---
def test_get_white_time(game_state):
    """
    Test that get_white_time is 30 minutes (1800 seconds).
    """
    game_state.start_timer()
    game_state.pause_timer()
    assert game_state.get_white_time() == 1800

# --- Tests for set_next_player ---
def test_set_next_player(game_state):
    """
    Test that set_next_player toggles between 0 and 1.
    """
    # Initially current player is 0.
    game_state.set_next_player()
    assert game_state.get_current_player() == 1
    game_state.set_next_player()
    assert game_state.get_current_player() == 0


# --- Tests for play_move ---
def test_play_move_legal():
    """
    When a legal move is played:
      - The move is added to the board.
      - The current player is toggled.
      - If the move was played by player 1, game round should be increased.
    """
    config = Config()
    config.set("board-size", '4')
    gs = GameState(config)
    # Current player is 0 initially.
    result = gs.play_move(('a', 2))
    assert result is 0
    # Current player should have toggled to 1.
    assert gs.get_current_player() == 1
    # Since the move was by player 0, game round should not have increased.
    assert gs.get_current_game_round() == 1
    
# --- Test for is_game_over ---
def test_is_game_over(game_state):
    """
    The current game should not be over.
    """
    assert game_state.is_game_over() == False
# --- Test for set_game_over ---
def test_set_game_over(game_state):
    """
    The current game should not be over then over.
    """
    assert game_state.is_game_over() == False
    game_state.set_game_over(GameOverState.WHITE_WON)
    assert game_state.is_game_over() == True
    
# --- Test for give_up ---
def test_give_up(game_state):
    """
    giving up on white turn so the game should end with a black victory
    """
    game_state.give_up()
    assert game_state.is_game_over() == True
    assert game_state.get_winner() == GameOverState.BLACK_WON
    
# --- Test for undo ---
def test_undo(game_state):
    """
    Playing a move then undo check with a board doing the same whitout the undo
    """
    config = Config()
    config.set("board-size", '4')
    gs = GameState(config)
    gs2=GameState(config)
    gs.play_move(('a', 1))
    gs2.play_move(('a', 1))

    assert gs.are_board_equals(gs2.get_board()) 
    gs.undo()
    assert not(gs.are_board_equals(gs2.get_board())) 
    

# --- Test for redo ---
def test_redo(game_state):
    """
    Playing a move then undo/redo check with a board doing the same whitout the undo/redo
    """
    config = Config()
    config.set("board-size", '4')
    gs = GameState(config)
    gs2 = GameState(config)
    gs.play_move(('a', 1))
    gs2.play_move(('a', 1))

    assert gs.are_board_equals(gs2.get_board()) 
    gs.undo()
    gs.redo()
    assert gs.are_board_equals(gs2.get_board()) 
    
    
@pytest.mark.parametrize("illegal_move", [translate('z', 1), translate('a', 125), translate('z', 13)])
def test_play_move_illegal(game_state, illegal_move):
    """
    Playing an illegal move should return False,
    and the board and current player should remain unchanged.
    """
    original_player = game_state.get_current_player()

    result = game_state.play_move(illegal_move)
    assert result is 2

    # The current player must remain the same.
    assert game_state.get_current_player() == original_player


def test_play_move_game_round_increase():
    """
    Test that when a move is played by player 1, the game round is increased.
    This is simulated by first playing a move with player 0 (so that the current player toggles to 1),
    then playing a move with player 1.
    """
    config = Config()
    config.set("board-size", '4')
    gs = GameState(config)

    # First move by player 0.
    result1 = gs.play_move(('a', 1))
    assert result1 is 0
    # Now, current player is 1 and game round remains 0.
    assert gs.get_current_player() == 1
    assert gs.get_current_game_round() == 1

    # Second move by player 1.
    result2 = gs.play_move(('b', 1))
    assert result2 is 0
    # Current player toggles back to 0
    assert gs.get_current_player() == 0
    assert gs.get_current_game_round() == 2



def test_get_value_of_space():
    """
    Test that get_value_of_space return the good value.
    """
    config = Config()
    config.set("board-size", '4')
    gs = GameState(config)

    # First move by player 0.
    result1 = gs.play_move(('a', 1))
    assert result1 is 0
    assert gs.get_value_of_space(('a', 1)) is 1