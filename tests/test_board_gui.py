import pytest
import gi
gi.require_version('Gtk', '4.0')
from random import seed, randint
from pytest_mock import *
from gi.repository import Gtk
from hex.tools.game_over_state import GameOverState
from hex.tools import config
from hex.tools import game_state
from hex.userinterfaces.gui import board_gui


seed(10)
TESTING_DIMS = 20


@pytest.fixture
def testing_widgets() -> list[board_gui.BoardWidget]:
    """
    Create widgets containing game_states with each one representing
    a game with a boards of dim between 9 and 20.
    """
    widgets = []
    for i in range(1, TESTING_DIMS + 1):
        configuration = config.Config()
        configuration.set("board-size", str(i))
        game = game_state.GameState(configuration)
        widget = board_gui.BoardWidget(game, use_cairo=False)
        widgets.append(widget)
    return widgets


def test_init(mocker, testing_widgets):
    """
    Test that the widget correctly loads by verifying which functions
    are called.
    """
    for n in range(0, TESTING_DIMS):
        dim = n+1
        widget = testing_widgets[n]
        assert widget._BoardWidget__game_dim == dim
        for i in range(dim):
            for j in range(dim):
                assert widget._BoardWidget__board_rects[i][j] is not None
        update_dimension_spy = mocker.patch.object(board_gui.BoardWidget,
                                                   "_BoardWidget__update_dimensions",
                                                   new_callable=mocker.PropertyMock)
        draw_board_spy = mocker.patch.object(board_gui.BoardWidget,
                                             "_BoardWidget__draw_board",
                                             new_callable=mocker.PropertyMock)

        def mockreturn(snap):
            return True
        # This function needs a displayed cairo context we can't directly test
        # nor load
        mocker.patch.object(board_gui.BoardWidget, "_BoardWidget__draw_borders_and_text",
                            new_callable=mocker.PropertyMock,
                            return_value=mockreturn)

        snapshot = Gtk.Snapshot.new()
        widget.do_snapshot(snapshot)
        # These two aren't called but should not cause any problem
        widget._BoardWidget__draw_white_borders(snapshot)
        widget._BoardWidget__draw_winning_path(snapshot)

        update_dimension_spy.assert_called_once()
        draw_board_spy.assert_called_once()


def assert_inside_hexagon(widget, rect, x, y, value):
    assert widget._BoardWidget__is_inside_hexagon(rect, x, y) == value


def test_is_inside_hexagon(testing_widgets):
    """
    Test that coordinates are correctly read as inside or outside an
    hexagon.
    """
    epsilon = .01
    for n in range(TESTING_DIMS):
        dim = n + 1
        for i in range(dim):
            for j in range(dim):
                widget = testing_widgets[n]
                rect = widget._BoardWidget__board_rects[i][j]
                rect_dim = widget._BoardWidget__rect_dim
                rect_center = rect.get_center()
                rect_x = rect_center.x
                rect_y = rect_center.y
                r = rect_dim/2
                # Checking the center of the hexagon
                assert_inside_hexagon(widget, rect, rect_x, rect_y, True)

                # Checking corners
                # bottom left corner
                assert_inside_hexagon(
                    widget, rect, rect_x - r, rect_y + r, False)
                # top left corner
                assert_inside_hexagon(
                    widget, rect, rect_x - r, rect_y - r, False)
                # top right corner
                assert_inside_hexagon(
                    widget, rect, rect_x + r, rect_y - r, False)
                # bottom right corner
                assert_inside_hexagon(
                    widget, rect, rect_x + r, rect_y + r, False)

                # We will use -epsilon and +epsilon here because float
                # rounding can lead to undetermined results on the
                # borders of the hexagon

                # Checking sides
                # left side
                assert_inside_hexagon(
                    widget, rect, rect_x - r - epsilon, rect_y, False)
                assert_inside_hexagon(
                    widget, rect, rect_x - r + epsilon, rect_y, True)
                # right side
                assert_inside_hexagon(
                    widget, rect, rect_x + r - epsilon, rect_y, True)
                assert_inside_hexagon(
                    widget, rect, rect_x + r + epsilon, rect_y, False)

                # Checking diagonals
                # top right diag
                assert_inside_hexagon(
                    widget, rect, rect_x + r/2, rect_y + r/2 + r/4 - epsilon,
                    True)
                assert_inside_hexagon(
                    widget, rect, rect_x + r/2, rect_y + r/2 + r/4 + epsilon,
                    False)
                # bottom left diag
                assert_inside_hexagon(
                    widget, rect, rect_x - r/2, rect_y - r/2 - r/4 - epsilon,
                    False)
                assert_inside_hexagon(
                    widget, rect, rect_x - r/2, rect_y - r/2 - r/4 + epsilon,
                    True)

                # Checking vertices
                # bottom right vertex
                assert_inside_hexagon(
                    widget, rect, rect_x + r + epsilon, rect_y + r/2, False)
                assert_inside_hexagon(
                    widget, rect, rect_x + r - epsilon, rect_y + r/2, True)

                # bottom pointy vertex
                assert_inside_hexagon(
                    widget, rect, rect_x, rect_y + r + epsilon, False)
                assert_inside_hexagon(
                    widget, rect, rect_x, rect_y + r - epsilon, True)


def test_click(testing_widgets):
    """
    Test that verifies that click events are correctly handled inside
    and outside the board.
    """
    for n in range(TESTING_DIMS):
        dim = n + 1
        widget = testing_widgets[n]
        game = widget._BoardWidget__game
        rect_dim = widget._BoardWidget__rect_dim

        # Testing clicks inside an hexagon
        for i in range(dim):
            for j in range(dim):
                rect = widget._BoardWidget__board_rects[i][j]
                rect_center = rect.get_center()
                rect_x = rect_center.x
                rect_y = rect_center.y
                widget.on_clicked(None, 0, rect_x, rect_y)
                assert widget._BoardWidget__is_inside_hexagon(rect, rect_x, rect_y) == True
                position = i*dim + j
                assert game.get_value_of_space(position) == 1
                game.undo()

        random_border_coord = randint(0, dim-1)
        # inside a rectangle but not inside any other rectangle
        # and not inside the board
        rect = widget._BoardWidget__board_rects[0][random_border_coord]
        # inside the top left void of the rectangle
        rect_x = rect.get_x() + 1
        rect_y = rect.get_y() + 1
        widget.on_clicked(None, 0, rect_x, rect_y)
        assert widget._BoardWidget__is_inside_hexagon(rect, rect_x, rect_y) == False
        assert game.get_current_player() == 0
        # above the board
        rect = widget._BoardWidget__board_rects[0][random_border_coord]
        rect_center = rect.get_center()
        rect_x = rect_center.x
        rect_y = rect.get_y() - 1
        widget.on_clicked(None, 0, rect_x, rect_y)
        assert widget._BoardWidget__is_inside_hexagon(rect, rect_x, rect_y) == False
        assert game.get_current_player() == 0
        # left of the board
        rect = widget._BoardWidget__board_rects[random_border_coord][0]
        rect_center = rect.get_center()
        rect_x = rect.get_x() - 1
        rect_y = rect_center.y
        widget.on_clicked(None, 0, rect_x, rect_y)
        assert widget._BoardWidget__is_inside_hexagon(rect, rect_x, rect_y) == False
        assert game.get_current_player() == 0
        # right of the board
        rect = widget._BoardWidget__board_rects[random_border_coord][dim-1]
        rect_center = rect.get_center()
        rect_x = rect.get_x() + rect_dim + 1
        rect_y = rect_center.y
        widget.on_clicked(None, 0, rect_x, rect_y)
        assert widget._BoardWidget__is_inside_hexagon(rect, rect_x, rect_y) == False
        assert game.get_current_player() == 0
        # below the board
        rect = widget._BoardWidget__board_rects[dim-1][random_border_coord]
        rect_center = rect.get_center()
        rect_x = rect_center.x
        rect_y = rect.get_y() + rect_dim + 1
        widget.on_clicked(None, 0, rect_x, rect_y)
        assert widget._BoardWidget__is_inside_hexagon(rect, rect_x, rect_y) == False
        assert game.get_current_player() == 0


def test_draw_winning_path(mocker, testing_widgets):
    """
    Test that if the game is finished then the draw function should
    call the draw_winning_path method even if there is no winning
    path.
    """
    def mockreturn(snap):
        return True
    # This function needs a displayed cairo context we can't directly
    # test nor load
    mocker.patch.object(board_gui.BoardWidget, "_BoardWidget__draw_borders_and_text",
                        new_callable=mocker.PropertyMock,
                        return_value=mockreturn)
    for n in range(TESTING_DIMS):
        dim = n + 1
        widget = testing_widgets[n]
        game = widget._BoardWidget__game
        # Create a spy for each widget
        draw_winning_path_spy = mocker.patch.object(board_gui.BoardWidget,
                                                    "_BoardWidget__draw_winning_path",
                                                    new_callable=mocker.PropertyMock)
        snapshot = Gtk.Snapshot.new()
        # No winning path
        game.set_game_over(GameOverState.BLACK_WON)
        widget.do_snapshot(snapshot)
        draw_winning_path_spy.assert_called_once()
        # With a winning path
        for i in range(dim):
            game._GameState__board.add_move(i, 1)
        widget.do_snapshot(snapshot)
        assert draw_winning_path_spy.call_count == 2
