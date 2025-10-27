from time import sleep
import pytest, gi
from pytest_mock import *
from hex.userinterfaces.gui.main_menu_gui import MainMenuWindow
from hex.userinterfaces.gui.game_gui import GameWindow
from hex.tools.game_state import GameState
from hex.tools.config import Config
from hex.tools.file import FileModule
from hex.userinterfaces.gui.pause_menu_gui import PauseMenuWindow

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

class TestGameWindow:
    @pytest.fixture
    def window(self):
        """
        Returns an instance of the GameWindow class with default config (ai-time = 1 for Hint test).
        """
        config = Config()
        config.set("ai-time", "1")
        game_state = GameState(config)
        app = Gtk.Application()
        menu_window = MainMenuWindow(game_state, FileModule(game_state), application = app)
        game_window = GameWindow(game_state, menu_window, application = app)
        game_window.present()
        yield game_window

    @pytest.fixture
    def window_timer(self):
        """
        Returns an instance of the GameWindow class with blitz enabled.
        """
        config = Config()
        config.set("blitz", "true")
        game_state = GameState(config)
        app = Gtk.Application()
        menu_window = MainMenuWindow(game_state, FileModule(game_state), application = app)
        game_window = GameWindow(game_state, menu_window, application = app)
        game_window.present()
        yield game_window

    @pytest.fixture
    def window_ai(self):
        """
        Returns an instance of the GameWindow class with O player AI enabled.
        """
        config = Config()
        config.set("ai-time", "1")
        config.set("ai", "O")
        game_state = GameState(config)
        app = Gtk.Application()
        menu_window = MainMenuWindow(game_state, FileModule(game_state), application = app)
        game_window = GameWindow(game_state, menu_window, application = app)
        game_window.present()
        yield game_window
    
    @pytest.fixture
    def window_swap(self):
        """
        Returns an instance of the GameWindow class with swap enabled.
        """
        config = Config()
        config.set("swap", "true")
        game_state = GameState(config)
        app = Gtk.Application()
        menu_window = MainMenuWindow(game_state, FileModule(game_state), application = app)
        game_window = GameWindow(game_state, menu_window, application = app)
        game_window.present()
        yield game_window

    def test_main_display(self, window):
        """
        Tests that the main window is created
        """
        assert window.get_title() == "Hex Game"
        assert window.get_visible()
        window.destroy()
        assert not window.get_visible()
        for window in Gtk.Window.get_toplevels():
            if window.get_title() == "Hex Game":
                assert window.get_visible()
    
    def test_update_time_display(self, window, window_timer):
        """
        Tests that the timers display is correctly updated after some moves/undo/redo are made.
        """
        assert window._GameWindow__O_time_label.get_text() == "O's left time : ∞"
        assert window._GameWindow__X_time_label.get_text() == "X's left time : ∞"
        O_time_label = window_timer._GameWindow__O_time_label.get_text()
        X_time_label = window_timer._GameWindow__X_time_label.get_text()
        sleep(1)
        window_timer._GameWindow__update_time_display()
        assert window_timer._GameWindow__O_time_label.get_text() != O_time_label
        assert window_timer._GameWindow__X_time_label.get_text() == X_time_label
        window_timer._GameWindow__game_state.play_move(("a", 1))
        O_time_label = window_timer._GameWindow__O_time_label.get_text()
        X_time_label = window_timer._GameWindow__X_time_label.get_text()
        sleep(1)
        assert window_timer._GameWindow__O_time_label.get_text() == O_time_label
        assert window_timer._GameWindow__X_time_label.get_text() != X_time_label
    
    def test_update_history_display(self, window):
        """
        Tests that the done/undone moves histories display is correctly updated after some moves/undo/redo are made.
        """
        assert window._GameWindow__done_moves_label.get_text() == "Done moves\n- - - - - - - - - - -\nNone"
        assert window._GameWindow__undone_moves_label.get_text() == "Undone moves\n- - - - - - - - - - - - -\nNone"
        window._GameWindow__game_state.play_move(("a", 1))
        window._GameWindow__update_history_display()
        assert window._GameWindow__done_moves_label.get_text() == "Done moves\n- - - - - - - - - - -\n1. 0 a1"
        assert window._GameWindow__undone_moves_label.get_text() == "Undone moves\n- - - - - - - - - - - - -\nNone"
        window._GameWindow__game_state.undo()
        window._GameWindow__update_history_display()
        assert window._GameWindow__done_moves_label.get_text() == "Done moves\n- - - - - - - - - - -\nNone"
        assert window._GameWindow__undone_moves_label.get_text() == "Undone moves\n- - - - - - - - - - - - -\n1. 0 a1"

    def test_update_player_display(self, window):
        """
        Tests that the current player display is correctly updated after some moves/undo/redo are made.
        """
        window._GameWindow__update_player_display()
        assert window._GameWindow__player_label.get_text() == "Round n°1, current player : O"
        window._GameWindow__game_state.play_move(("a", 1))
        window._GameWindow__update_player_display()
        assert window._GameWindow__player_label.get_text() == "Round n°1, current player : X"
        window._GameWindow__game_state.play_move(("a", 2))
        window._GameWindow__update_player_display()
        assert window._GameWindow__player_label.get_text() == "Round n°2, current player : O"

    def test_update_all_displays(self, mocker, window, window_timer):
        """
        Tests that the "update_all_displays" method correctly updates player, timers, and histories displays.
        """
        window_update_time_display_spy = mocker.spy(window, "_GameWindow__update_time_display")
        window_update_history_display_spy = mocker.spy(window, "_GameWindow__update_history_display")
        window_update_player_display_spy = mocker.spy(window, "_GameWindow__update_player_display")
        window_timer_update_time_display_spy = mocker.spy(window_timer, "_GameWindow__update_time_display")
        window_timer_update_history_display_spy = mocker.spy(window_timer, "_GameWindow__update_history_display")
        window_timer_update_player_display_spy = mocker.spy(window_timer, "_GameWindow__update_player_display")
        window._GameWindow__update_all_displays()
        window_timer._GameWindow__update_all_displays()
        assert window_update_player_display_spy.call_count == window_timer_update_player_display_spy.call_count == 1
        assert window_update_history_display_spy.call_count == window_timer_update_history_display_spy.call_count == 1
        assert window_update_time_display_spy.call_count == 0
        assert window_timer_update_time_display_spy.call_count == 1

    def test_undo_button_clicked(self, mocker, window):
        """
        Tests that the undo button works by calling the game_state undo method.
        """
        undo_spy = mocker.spy(GameState, "undo")
        update_displays_spy = mocker.spy(window, "_GameWindow__update_all_displays")
        assert undo_spy.call_count == 0
        assert update_displays_spy.call_count == 0
        window._GameWindow__undo_button_clicked(window._GameWindow__undo_button)
        assert undo_spy.call_count == 1
        assert update_displays_spy.call_count == 0
        window._GameWindow__game_state.play_move(("a", 1))
        window._GameWindow__undo_button_clicked(window._GameWindow__undo_button)
        assert undo_spy.call_count == 2
        assert update_displays_spy.call_count == 1
    
    def test_redo_button_clicked(self, mocker, window):
        """
        Tests that the redo button works by calling the game_state redo method.
        """
        redo_spy = mocker.spy(GameState, "redo")
        update_displays_spy = mocker.spy(window, "_GameWindow__update_all_displays")
        assert redo_spy.call_count == 0
        assert update_displays_spy.call_count == 0
        window._GameWindow__redo_button_clicked(window._GameWindow__redo_button)
        assert redo_spy.call_count == 1
        assert update_displays_spy.call_count == 0
        window._GameWindow__game_state.play_move(("a", 1))
        window._GameWindow__game_state.undo()
        window._GameWindow__redo_button_clicked(window._GameWindow__redo_button)
        assert redo_spy.call_count == 2
        assert update_displays_spy.call_count == 1

    def test_hint_button_clicked(self, mocker, window):
        hint_button_clicked_spy = mocker.spy(window, "_GameWindow__hint_button_clicked")
        assert hint_button_clicked_spy.call_count == 0
        window._GameWindow__hint_button_clicked(window._GameWindow__hint_button)
        assert hint_button_clicked_spy.call_count == 1
    
    def test_pause_button_clicked(self, mocker, window_timer):
        pause_button_clicked_spy = mocker.spy(window_timer, "_GameWindow__pause_button_clicked")
        assert pause_button_clicked_spy.call_count == 0
        window_timer._GameWindow__pause_button_clicked(window_timer._GameWindow__pause_button)
        assert pause_button_clicked_spy.call_count == 1

    def test_on_board_clicked(self, mocker, window):
        """
        Tests that clicking on an empty cell of the board plays a move.
        """
        play_move_spy = mocker.spy(window._GameWindow__game_state, "play_move")
        update_displays_spy = mocker.spy(window, "_GameWindow__update_all_displays")
        assert play_move_spy.call_count == 0
        assert update_displays_spy.call_count == 0
        window._GameWindow__on_board_clicked(None, 1, 0, 0)
        assert play_move_spy.call_count == 0
        assert update_displays_spy.call_count == 0
        window._GameWindow__on_board_clicked(None, 1, 800, 450)
        assert play_move_spy.call_count == 1
        assert update_displays_spy.call_count == 1
    
    def test_on_window_closed(self, window):
        window._GameWindow__on_window_closed(None)

    def test_ai(self, window_ai):
        """
        Tests that O AI player does play the first move.
        """
        assert len(window_ai._GameWindow__game_state.get_last_moves()[0]) == 0
        sleep(2)
        assert len(window_ai._GameWindow__game_state.get_last_moves()[0]) == 1

    def test_swap(self, mocker, window_swap):
        """
        Tests that swap is correctly called with the option enabled.
        """
        swap_spy = mocker.spy(window_swap, "_GameWindow__swap")
        assert swap_spy.call_count == 0
        window_swap._GameWindow__on_board_clicked(None, 1, 800, 450)
        assert swap_spy.call_count == 1
