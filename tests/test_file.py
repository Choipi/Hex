import pytest
from hex.tools import file
from hex.tools import config
from hex.tools.game_state import GameState
import tempfile
import os
import sys


@pytest.fixture
def basic_file_module():

    conf = config.Config()
    gs = GameState(conf)
    file_m = file.FileModule(gs)
    return file_m


@pytest.mark.parametrize("good_paths", ["tests/test_good_boards/good_1.hexgame"])
def test_check_load_good_paths(basic_file_module, good_paths):
    basic_file_module.load_hexgame(good_paths)


@pytest.mark.parametrize("bad_paths", ["tests/test_bad_boards/wrong_extension/1.hexgamee", "tests/test_bad_boards/wrong_extension/2.hxgame", "tests/test_bad_boards/wrong_extension/3.hex"])
def test_check_extension_bad_paths(basic_file_module, bad_paths):
    with pytest.raises(ValueError):
        basic_file_module.load_hexgame(bad_paths)


@pytest.mark.parametrize("bad_paths", ["tests/test_bad_boards/history_matching/Bad_added_history1.hexgame", "tests/test_bad_boards/history_matching/Bad_added_history2.hexgame", "tests/test_bad_boards/history_matching/Bad_added_piece1.hexgame", "tests/test_bad_boards/history_matching/Bad_added_piece2.hexgame", "tests/test_bad_boards/history_matching/Bad_remove_a_move_from_history1.hexgame", "tests/test_bad_boards/history_matching/bad_remove_a_piece1.hexgame", "tests/test_bad_boards/history_matching/bad_remove_a_piece1.hexgame"])
def test_load_history_not_matching_board(basic_file_module, bad_paths):
    with pytest.raises(ValueError):
        basic_file_module.load_hexgame(bad_paths)


@pytest.mark.parametrize("bad_files", ["tests/test_bad_boards/added_incorect_char/Bad_char1.hexgame", "tests/test_bad_boards/added_incorect_char/Bad_char2.hexgame", "tests/test_bad_boards/added_incorect_char/bad_delete_history_char2.hexgame", "tests/test_bad_boards/added_incorect_char/illegal_values.hexgame", "tests/test_bad_boards/added_incorect_char/illegal_values.hexgame"])
def test_added_incorect_values(basic_file_module, bad_files):
    with pytest.raises(ValueError):
        basic_file_module.load_hexgame(bad_files)


@pytest.mark.parametrize("bad_files", ["tests/test_bad_boards/bad_size/Bad_size.hexgame", "tests/test_bad_boards/bad_size/Bad_size2.hexgame", "tests/test_bad_boards/bad_size/removed_line.hexgame", "tests/test_bad_boards/bad_size/removed_piece.hexgame"])
def test_board_size_incorect(basic_file_module, bad_files):
    with pytest.raises(ValueError):
        basic_file_module.load_hexgame(bad_files)


@pytest.mark.parametrize("good_paths", ["tests/test_good_boards/good_1.hexgame", "tests/test_good_boards/good_2.hexgame"])
def test_save_load_exact_same_board(basic_file_module, good_paths):
    conf = config.Config()
    gs = GameState(conf)
    gs2 = GameState(conf)

    file_m = file.FileModule(gs)
    file_m2 = file.FileModule(gs2)

    file_m.load_hexgame(good_paths)
    file_m.save_as_hexgame("tests/temp_testing_files/tmp")
    file_m2.load_hexgame("tests/temp_testing_files/tmp.hexgame")

    assert gs.are_board_equals(gs2.get_board()) == True


@pytest.mark.parametrize("good_paths", ["tests/test_good_boards/good_1.hexgame"])
def test_save_load_not_same_board(good_paths):
    conf = config.Config()
    gs = GameState(conf)
    gs2 = GameState(conf)

    file_m = file.FileModule(gs)
    file_m2 = file.FileModule(gs2)

    file_m.load_hexgame(good_paths)
    file_m2.load_hexgame("tests/test_good_boards/good_2.hexgame")

    assert gs.are_board_equals(gs2.get_board()) == False


def test_save_load():
    conf = config.Config()
    gs = GameState(conf)
    file_m = file.FileModule(gs)

    file_m.save_as_hexgame("tests/temp_testing_files/empty_board")
    file_m.load_hexgame("tests/temp_testing_files/empty_board.hexgame")
