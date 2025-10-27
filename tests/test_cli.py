import pytest
import os
from pytest_mock import *
from hex.userinterfaces import cli
from hex.tools import game_state
from hex.tools import config
from hex.tools.file import FileModule


@pytest.fixture
def testing_interface():
    """
    Returns an instance of the Cli class for testing.
    """
    game = game_state.GameState(config.Config())
    file_m = FileModule(game)
    interface = cli.Cli(game, file_m)
    return interface


def test_invalid(mocker, testing_interface):
    """
    Tests that an invalid input is correctly recognized and notified in the output.
    """
    mocked_input = mocker.patch("builtins.input")
    mocked_input.side_effect = ["x", KeyboardInterrupt]
    mocked_print = mocker.patch('builtins.print')
    with pytest.raises(SystemExit):
        testing_interface.start_game()
    mocked_print.assert_any_call("Invalid input (input 'h' for help).")


def test_quit_confirm(mocker, testing_interface):
    """
    Tests that the "quit" command is correctly recognized and handled.
    """
    mocked_input = mocker.patch("builtins.input")
    mocked_input.side_effect = ["q", "a", "n", "quit", "y"]
    quit_input_spy = mocker.spy(cli.Cli, "_Cli__check_user_input_quit")
    confirm_spy = mocker.spy(cli.Cli, "_Cli__confirm")
    with pytest.raises(SystemExit):
        testing_interface.start_game()
    assert quit_input_spy.call_count == 2
    assert quit_input_spy.spy_return_list == [True, True]
    assert confirm_spy.call_count == 3
    assert confirm_spy.spy_return_list == [False, False, True]
    confirm_spy.assert_called_with(testing_interface, "quit")

def test_help(mocker, testing_interface):
    """
    Tests that the "help" command is correctly recognized and handled.
    """
    mocked_input = mocker.patch("builtins.input")
    mocked_input.side_effect = ["h", KeyboardInterrupt]
    mocked_print = mocker.patch('builtins.print')
    help_input_spy = mocker.spy(cli.Cli, "_Cli__check_user_input_help")
    help_display_spy = mocker.spy(cli.Cli, "_Cli__display_help")
    with pytest.raises(SystemExit):
        testing_interface.start_game()
    assert help_input_spy.call_count == help_display_spy.call_count == 1
    assert help_input_spy.spy_return == True
    mocked_print.assert_any_call("""Hex game input syntax help:
    [letter][number]: Input next move to play (example: 'a5').
    'u/undo':         Undo the last move.
    'r/redo':         Redo the last undone move.
    'h/help':         Display program help.
    'd/display':      Display current game board.
    'restart':        Restart current game (with the same configuration).
    'l/load' [FILE]:  Load game from specified file.
    's/save' [FILE]:  Save current game in specified file.
    'g/give up'       Give up current game (current player loses).
    'q/quit':         Exit program.""")


def test_undo_redo(mocker, testing_interface):
    """
    Tests that the "undo" and "redo" commands are correctly recognized and handled.
    """
    mocked_input = mocker.patch("builtins.input")
    mocked_input.side_effect = ["u", "r", "a1",
                                "undo", "redo", KeyboardInterrupt]
    mocked_print = mocker.patch('builtins.print')
    undo_input_spy = mocker.spy(cli.Cli, "_Cli__check_user_input_undo")
    redo_input_spy = mocker.spy(cli.Cli, "_Cli__check_user_input_redo")
    undo_spy = mocker.spy(cli.Cli, "_Cli__undo")
    redo_spy = mocker.spy(cli.Cli, "_Cli__redo")
    with pytest.raises(SystemExit):
        testing_interface.start_game()
    assert undo_input_spy.call_count == 5
    assert undo_input_spy.spy_return_list == [True, False, False, True, False]
    assert redo_input_spy.call_count == 3
    assert redo_input_spy.spy_return_list == [True, False, True]
    assert undo_spy.call_count == redo_spy.call_count == 2
    mocked_print.assert_any_call(
        "Undo not possible; done moves history is currently empty.")
    mocked_print.assert_any_call(
        "Redo not possible; undone moves history is currently empty.")


def test_display(mocker, testing_interface):
    """
    Tests that the board, history and timers are correctly being displayed.
    """
    mocked_input = mocker.patch("builtins.input")
    mocked_input.side_effect = ["d", "display", "a1", KeyboardInterrupt]
    mocked_print = mocker.patch('builtins.print')
    display_input_spy = mocker.spy(cli.Cli, "_Cli__check_user_input_display")
    game_display_spy = mocker.spy(cli.Cli, "_Cli__display_game")
    with pytest.raises(SystemExit):
        testing_interface.start_game()
    assert display_input_spy.call_count == 3
    assert display_input_spy.spy_return_list == [True, True, False]
    assert game_display_spy.call_count == 4
    mocked_print.assert_any_call("""  a b c d e f g h i j k               Last done moves:     Last undone moves:     O remaining time:     X remaining time:
   o o o o o o o o o o o              ----------------     ------------------     -----------------     -----------------
1 x . . . . . . . . . . . x                                                       ∞                     ∞
 2 x . . . . . . . . . . . x                                                      
  3 x . . . . . . . . . . . x                                                     
   4 x . . . . . . . . . . . x                                                    
    5 x . . . . . . . . . . . x                                                   
     6 x . . . . . . . . . . . x                                                  
      7 x . . . . . . . . . . . x                                                 
       8 x . . . . . . . . . . . x                                                
        9 x . . . . . . . . . . . x                                               
        10 x . . . . . . . . . . . x                                              
         11 x . . . . . . . . . . . x                                             
               o o o o o o o o o o o """)
    mocked_print.assert_any_call("""  a b c d e f g h i j k               Last done moves:     Last undone moves:     O remaining time:     X remaining time:
   o o o o o o o o o o o              ----------------     ------------------     -----------------     -----------------
1 x O . . . . . . . . . . x           | 1. 0 a1 |                                 ∞                     ∞
 2 x . . . . . . . . . . . x                                                      
  3 x . . . . . . . . . . . x                                                     
   4 x . . . . . . . . . . . x                                                    
    5 x . . . . . . . . . . . x                                                   
     6 x . . . . . . . . . . . x                                                  
      7 x . . . . . . . . . . . x                                                 
       8 x . . . . . . . . . . . x                                                
        9 x . . . . . . . . . . . x                                               
        10 x . . . . . . . . . . . x                                              
         11 x . . . . . . . . . . . x                                             
               o o o o o o o o o o o """)


def test_start_restart(mocker, testing_interface):
    """
    Tests that the "restart" command is correctly recognized and handled.
    """
    mocked_input = mocker.patch("builtins.input")
    mocked_input.side_effect = ["restart", "y", KeyboardInterrupt]
    game_start_spy = mocker.spy(cli.Cli, "start_game")
    restart_input_spy = mocker.spy(cli.Cli, "_Cli__check_user_input_restart")
    game_restart_spy = mocker.spy(cli.Cli, "_Cli__restart_game")
    with pytest.raises(SystemExit):
        testing_interface.start_game()
    assert game_start_spy.call_count == 2
    assert restart_input_spy.call_count == game_restart_spy.call_count == 1
    assert restart_input_spy.spy_return == True


def test_give_up(mocker, testing_interface):
    """
    Tests that the "give up" command is correctly recognized and handled.
    """
    mocked_input = mocker.patch("builtins.input")
    mocked_input.side_effect = ["g", "n", "give up", "y", KeyboardInterrupt]
    give_up_input_spy = mocker.spy(cli.Cli, "_Cli__check_user_input_give_up")
    with pytest.raises(SystemExit):
        testing_interface.start_game()
    assert give_up_input_spy.call_count == 2
    assert give_up_input_spy.spy_return_list == [True, True]


def test_move(mocker, testing_interface):
    """
    Tests that a move being input is correctly recognized and handled.
    """
    mocked_input = mocker.patch("builtins.input")
    mocked_input.side_effect = ["a1", "a1", "a99",
                                "1b", "c 1", "1 d", KeyboardInterrupt]
    mocked_print = mocker.patch('builtins.print')
    move_input_spy = mocker.spy(cli.Cli, "_Cli__check_user_input_move")
    move_handling_spy = mocker.spy(cli.Cli, "_Cli__handle_move")
    with pytest.raises(SystemExit):
        testing_interface.start_game()
    assert move_input_spy.call_count == 6
    assert len(move_input_spy.spy_return_list) == 6 and all(
        e != False for e in move_input_spy.spy_return_list)
    assert move_handling_spy.call_count == 6
    move_handling_spy.assert_called_with(testing_interface, ("d", 1))
    mocked_print.assert_any_call("Space (a, 1) is already occupied.")
    mocked_print.assert_any_call("Move (a, 99) is out of bounds.")


def test_save_load(mocker, testing_interface):
    """
    Tests that the "save" and "load" commands are correctly recognized and handled.
    """
    mocked_input = mocker.patch("builtins.input")
    mocked_input.side_effect = ["save test_save_load",
                                "load test_save_load.hexgame", KeyboardInterrupt]
    load_input_spy = mocker.spy(cli.Cli, "_Cli__check_user_input_load")
    game_load_spy = mocker.spy(cli.Cli, "_Cli__load_game")
    save_input_spy = mocker.spy(cli.Cli, "_Cli__check_user_input_save")
    game_save_spy = mocker.spy(cli.Cli, "_Cli__save_game")
    with pytest.raises(SystemExit):
        testing_interface.start_game()
    load_input_spy.assert_called_once()
    assert save_input_spy.call_count == 2
    game_save_spy.assert_called_once_with(testing_interface, "test_save_load")
    game_load_spy.assert_called_once_with(
        testing_interface, "test_save_load.hexgame")
    if os.path.exists("test_save_load.hexgame"):
        os.remove("test_save_load.hexgame")
