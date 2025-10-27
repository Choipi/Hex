import pytest
from hex.tools.game_over_state import GameOverState
from hex.tools.game_state import GameState
from hex.tools.config import Config
from hex.tools.file import FileModule
from hex.ai.ai import AIModule
from hex.ai.ai_heuristic import Heuristic
from hex.ai.exploration_algorithm import Exploration_algorithm


@pytest.fixture
def testing_game() -> GameState:
    """Create a game of size 6x6"""
    config = Config()
    config.set('board-size', '6')
    return GameState(config)


def test_ai_init(testing_game):
    """Test all configuration methods."""
    ai = testing_game.get_ai()
    # ai depth
    depth = ai.get_ai_depth()
    assert depth == testing_game.get_config().get("ai-depth")
    # ai players
    ai.set_ai_player("")
    assert ai.get_ai_players() == []
    ai.set_ai_player("None")
    assert ai.get_ai_players() == []
    ai.set_ai_player("X")
    assert ai.get_ai_players() == [1]
    ai.set_ai_player("O")
    assert ai.get_ai_players() == [0]
    ai.set_ai_player("A")
    assert ai.get_ai_players() == [0, 1]
    # ai heuristics
    heuristics = ai.get_all_heuristic_names()
    for heur in heuristics:
        if str(ai.get_a_O()) != "Monte Carlo Tree Search":
            ai.set_heuristic_from_string(heur, 0)
            assert isinstance(ai.get_h_O(), Heuristic)
        if str(ai.get_a_O()) != "Monte Carlo Tree Search":
            ai.set_heuristic_from_string(heur, 1)
            assert isinstance(ai.get_h_X(), Heuristic)

    if str(ai.get_a_O()) != "Monte Carlo Tree Search":
        ai.set_heuristic_from_string("", 0)
        assert str(ai.get_h_O()) == "Random"
    if str(ai.get_a_X()) != "Monte Carlo Tree Search":
        ai.set_heuristic_from_string("", 1)
        assert str(ai.get_h_X()) == "Random"
    # ai mode

    ai.set_exploration_algorithm_from_string("", 0)
    assert str(ai.get_a_O()) == "Random Exploration"
    ai.set_exploration_algorithm_from_string("", 1)
    assert str(ai.get_a_X()) == "Random Exploration"


def test_ai_black_wins(testing_game):
    """Test endgame heuristics for black."""
    file_m = FileModule(testing_game)
    file_m.load_hexgame("tests/test_ai_boards/ai_black_wins.hexgame")
    ai = testing_game.get_ai()
    heuristics = ['bfs', 'potential_threats',
                  'path_oriented', 'dijkstra']
    ai_modes = ['minimax', 'alpha_beta', 'mcts']
    for heur in heuristics:
        if str(ai.get_a_X()) != "Monte Carlo Tree Search":
            ai.set_heuristic_from_string(heur, 1)
        for mode in ai_modes:
            ai.set_exploration_algorithm_from_string(mode, 1)
            print(heur, mode)
            testing_game.ai_play_move(1)
            assert testing_game.get_winner() == GameOverState.BLACK_WON
            testing_game.undo()


def test_ai_white_wins(testing_game):
    """Test endgame heuristics for white."""
    file_m = FileModule(testing_game)
    file_m.load_hexgame("tests/test_ai_boards/ai_white_wins.hexgame")
    ai = testing_game.get_ai()
    ai_modes = ['minimax', 'alpha_beta', 'mcts']
    heuristics = ['bfs', 'potential_threats',
                  'path_oriented', 'dijkstra']
    for heur in heuristics:
        if str(ai.get_a_O()) != "Monte Carlo Tree Search":
            ai.set_heuristic_from_string(heur, 0)
        for mode in ai_modes:
            ai.set_exploration_algorithm_from_string(mode, 0)
            testing_game.ai_play_move(0)
            assert testing_game.get_winner() == GameOverState.WHITE_WON
            testing_game.undo()


def test_all_ai_return_a_move(testing_game):
    """Test that checks that every ai returns a move."""
    ai = testing_game.get_ai()
    ai.set_max_time(5)
    heuristics = ['random', 'bfs', 'potential_threats',
                  'path_oriented', 'dijkstra']
    ai_modes = ['random_exploration', 'minimax', 'alpha_beta']
    for heur in heuristics:
        if str(ai.get_a_O()) != "Monte Carlo Tree Search":
            ai.set_heuristic_from_string(heur, 0)
        for mode in ai_modes:
            ai.set_exploration_algorithm_from_string(mode, 0)
            move = ai.ai_get_move(
                0, testing_game.get_board().duplicate_board())
            assert testing_game.get_board().check_legal_move(move)

    # Monte Carlo Tree Search
    ai.set_heuristic_from_string('', 0)
    ai.set_exploration_algorithm_from_string('mcts', 0)
    move = ai.ai_get_move(
        0, testing_game.get_board().duplicate_board())
    assert testing_game.get_board().check_legal_move(move)
