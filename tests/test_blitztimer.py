from time import sleep
import pytest
from hex.tools.game_over_state import GameOverState
from hex.tools import config
from pytest_mock import *
from hex.tools import game_state


@pytest.fixture
def testing_game(mocker):
    """ 
    The game state used for the tests. Blitz mode is on and the time
    at which the timers will run out is set to 2 seconds.
    """
    c = config.Config()
    c.set("blitz", "true")
    c.set("time", "2")
    game = game_state.GameState(c)

    # Manually putting the time to 2 seconds because the time argument
    # in blitztimer's constructor is multiplied by 60 because it's
    # supposed to be minutes
    game._GameState__blitztimer._BlitzTimer__default_time = 2
    game._GameState__blitztimer._BlitzTimer__w_remaining_time = 2
    game._GameState__blitztimer._BlitzTimer__b_remaining_time = 2
    return game


def test_change_default_time(testing_game):
    """ 
    Test that set_default_time correctly changes the default time,
    and, if the timer resets, correctly changes the remaining
    times.
    """
    timer = testing_game._GameState__blitztimer

    # Check that changing the default time and resetting even if the
    # timer is running correctly changes the default and remaining
    # times
    timer.start()
    sleep(1)
    timer.set_default_time(4)
    timer.reset()
    # 240 seconds = 4 minutes
    assert timer._BlitzTimer__default_time == 240
    assert timer.get_white_remaining_time() == 240
    assert timer.get_black_remaining_time() == 240


def test_white_loses(testing_game):
    """ 
    Test the state of the timer and the game's winner when white's
    timer runs out. 
    """
    timer = testing_game._GameState__blitztimer
    timer.start()
    with pytest.raises(InterruptedError):
        sleep(2.5)
        assert False

    assert testing_game.get_winner() == GameOverState.BLACK_WON  # black wins
    assert timer.get_black_remaining_time() == 2
    assert timer.get_white_remaining_time() <= 0


def test_black_loses(testing_game):
    """ 
    Test the state of the timer and the game's winner when black's
    timer runs out. 
    """
    timer = testing_game._GameState__blitztimer

    # Let white's timer run for around one second
    timer.start()
    sleep(1)

    # Change player and wait until its timer runs out
    timer.next_player()
    with pytest.raises(InterruptedError):
        sleep(2.5)
        assert False

    assert testing_game.get_winner() == GameOverState.WHITE_WON  # white wins
    assert timer.get_white_remaining_time() < 1.5
    assert timer.get_black_remaining_time() <= 0


def test_pause_and_resume(testing_game):
    """ Test that pausing doesn't change the remaining time and that
    resuming resumes subtracting time.
    """
    timer = testing_game._GameState__blitztimer

    # Check that the current time is set to the default time
    first_measure = timer.get_white_remaining_time()
    assert first_measure == 2

    # Start then pause the timer after one second
    timer.start()
    sleep(1)
    timer.pause()

    # Check that one second has been subtracted to the remaining time
    second_measure = timer.get_white_remaining_time()
    assert first_measure > second_measure
    assert second_measure < 1.5

    # Wait one second and check that the remaining time didn't change
    sleep(1)
    third_measure = timer.get_white_remaining_time()
    assert second_measure == third_measure

    # Resume the timer then pause the timer after some time
    timer.resume()
    sleep(0.1)
    timer.pause()

    # Check that some time has been subtracted to the remaining
    # time
    fourth_measure = timer.get_white_remaining_time()
    assert fourth_measure < third_measure


def test_reset(testing_game):
    """
    Test that reset resets the remaining times whether the timer is
    paused or not. If the timer is not paused reset also pauses it.
    """
    timer = testing_game._GameState__blitztimer

    # Start the timer then pause the timer
    # and check that both timers lost around one second
    timer.start()
    sleep(1)
    first_measure = timer.get_white_remaining_time()
    timer.next_player()
    sleep(1)
    timer.pause()
    second_measure = timer.get_black_remaining_time()
    assert first_measure < 1.5
    assert second_measure < 1.5

    # Check that resetting sets both timers to the default time
    timer.reset()
    sleep(1)
    assert timer.get_white_remaining_time() == 2
    assert timer.get_black_remaining_time() == 2

    # Start the timer and check that both timers lost around one
    # second but the timer will not be paused
    timer.start()
    sleep(1.3)
    timer.next_player()
    sleep(1.3)
    third_measure = timer.get_white_remaining_time()
    fourth_measure = timer.get_black_remaining_time()
    assert third_measure < 1.5
    assert fourth_measure < 1.5

    # Check that resetting sets both timers to the default time
    # and pauses the timer
    timer.reset()
    sleep(1)
    assert timer.get_white_remaining_time() == 2
    assert timer.get_black_remaining_time() == 2
