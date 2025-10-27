import pytest
import gi
import gettext
from hex.userinterfaces.gui.main_menu_gui import MainMenuWindow
from hex.userinterfaces.gui.new_game_menu_gui import NewGameMenuWindow
from hex.userinterfaces.gui.pause_menu_gui import PauseMenuWindow
from hex.userinterfaces.gui.about_gui import AboutWindow
from hex.userinterfaces.gui.help_gui import HelpWindow
from hex.tools.game_state import GameState
from hex.tools.config import Config
from hex.tools.file import FileModule

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk


class DummyPrevWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, title="Dummy Window")


class TestMainMenu:
    @pytest.fixture
    def window(self):
        config = Config()
        game_state = GameState(config)
        file_m = FileModule(game_state)

        app = Gtk.Application()
        window = MainMenuWindow(game_state, file_m, application=app)
        window.present()
        yield window

    def test_main_menu_title(self, window):
        assert window.get_title() == "Main Menu"

    def test_new_game_menu(self, window):
        assert window.get_visible()
        window._MainMenuWindow__on_new_game_clicked(None)
        assert not window.get_visible()

        for window in Gtk.Window.get_toplevels():
            if window.get_title() == "New Game":
                assert window.get_visible()

    def test_change_language(self, window):
        """
        By default, the program starts with language[0] selected
        so it is safe to test with index 1
        """
        global current_lang
        current_lang = window._MainMenuWindow__game.get_config().get("language")
        language_translations = gettext.translation("bmain",
                                                    localedir="hex/\
userinterfaces/locales",
                                                    languages=[current_lang],
                                                    fallback=True)
        language_translations.install()

        global _
        _ = language_translations.gettext

        current_title = window.get_title()
        window._MainMenuWindow__language_dropdown.set_selected(1)
        assert current_title != window.get_title()

        new_lang = window._MainMenuWindow__game.get_config().get("language")
        assert current_lang != new_lang

        assert window._MainMenuWindow__main_menu_label.get_label() != _("Main Menu")
        for label, fun in window._MainMenuWindow__main_buttons_label_func:
            assert window._MainMenuWindow__main_buttons[label].get_label() != label
        assert window._MainMenuWindow__about_button.get_label() != _("About")
        assert window._MainMenuWindow__help_button.get_label() != _("Help")

    def test_on_about_clicked(self, window):
        assert window.is_visible()
        window._MainMenuWindow__about_button.emit("clicked")
        assert not window.is_visible()

        for window in Gtk.Window.get_toplevels():
            if window.get_title() == "About":
                assert window.get_visible()

    def test_on_help_clicked(self, window):
        assert window.is_visible()
        window._MainMenuWindow__help_button.emit("clicked")
        assert not window.is_visible()

        for window in Gtk.Window.get_toplevels():
            if window.get_title() == "Help":
                assert window.get_visible()

    def test_on_load_game_clicked(self, window, mocker):
        window._MainMenuWindow__main_buttons["Load Game..."].emit("clicked")

        # mock_function = mocker.Mock(side_effect=window.file_dialog_callback)

        # ? How to test FileChooserDialog ?
        # mock_function(None, None, None)


class TestNewGameMenu:
    @pytest.fixture
    def window(self):
        config = Config()
        game_state = GameState(config)

        dummy_window = DummyPrevWindow()
        window = NewGameMenuWindow(game_state, dummy_window)
        yield window
        window.destroy()

    def test_main_menu_title(self, window):
        assert window.get_title() == "New Game"

    def test_start_clicked(self, window, caplog):
        start_button = None

        # The start button is located inside a Box, not directly
        # in the window
        for child in window.get_child().observe_children():
            if isinstance(child, Gtk.Box):
                for child2 in child.observe_children():
                    if isinstance(child2, Gtk.Button) \
                       and "Start" in child2.get_label():
                        start_button = child2

        assert start_button is not None

        start_button.emit("clicked")
        assert not window.is_visible()

        window._NewGameMenuWindow__blitz_time_entry.props.text = "-5"
        start_button.emit("clicked")
        assert "Size and/or Blitz time is not a positive number.\
" in caplog.text

        window._NewGameMenuWindow__blitz_time_entry.props.text = "10"
        window._NewGameMenuWindow__size_entry.props.text = "35"
        caplog.clear()
        start_button.emit("clicked")
        assert "The board size must be a number between 1 and \
20." in caplog.text

    def test_blitz(self, window):
        assert not window._NewGameMenuWindow__blitz_checkbutton.get_active()
        assert not window._NewGameMenuWindow__blitz_time_entry.get_sensitive()

        window._NewGameMenuWindow__blitz_checkbutton.emit("activate")
        assert window._NewGameMenuWindow__blitz_time_entry.get_sensitive()

    def test_radio_buttons(self, window):
        # AI player None is selected by default so difficulty dropdown should
        # be on None also
        assert window._NewGameMenuWindow__ai_none_checkbutton.get_active()
        assert not window._NewGameMenuWindow__ai_x_checkbutton.get_active()
        assert not window._NewGameMenuWindow__ai_o_checkbutton.get_active()
        assert not window._NewGameMenuWindow__ai_a_checkbutton.get_active()
        assert (window._NewGameMenuWindow__ai_difficulty_dropdown.get_selected_item().get_string()
                == "None")

        # when player X is selected, dropdown selection should be Custom
        # (index = 3)
        window._NewGameMenuWindow__ai_x_checkbutton.set_active(True)
        assert not window._NewGameMenuWindow__ai_none_checkbutton.get_active()
        assert window._NewGameMenuWindow__ai_x_checkbutton.get_active()
        assert (window._NewGameMenuWindow__ai_difficulty_dropdown.get_selected_item().get_string()
                == "Custom")

        # when AI player goes back to None, the difficulty dropdown should
        # be on None also
        window._NewGameMenuWindow__ai_none_checkbutton.set_active(True)
        assert window._NewGameMenuWindow__ai_none_checkbutton.get_active()
        assert not window._NewGameMenuWindow__ai_x_checkbutton.get_active()
        assert (window._NewGameMenuWindow__ai_difficulty_dropdown.get_selected_item().get_string()
                == "None")

        # when player O is selected, dropdown selection should be Custom
        window._NewGameMenuWindow__ai_o_checkbutton.set_active(True)
        assert not window._NewGameMenuWindow__ai_none_checkbutton.get_active()
        assert window._NewGameMenuWindow__ai_o_checkbutton.get_active()
        assert (window._NewGameMenuWindow__ai_difficulty_dropdown.get_selected_item().get_string()
                == "Custom")

        # when player A is selected, dropdown selection should be Custom
        window._NewGameMenuWindow__ai_a_checkbutton.set_active(True)
        assert not window._NewGameMenuWindow__ai_none_checkbutton.get_active()
        assert window._NewGameMenuWindow__ai_a_checkbutton.get_active()
        assert (window._NewGameMenuWindow__ai_difficulty_dropdown.get_selected_item().get_string()
                == "Custom")

    def test_ai_difficulty(self, window):
        assert window._NewGameMenuWindow__ai_none_checkbutton.get_active()
        assert not window._NewGameMenuWindow__ai_x_checkbutton.get_active()
        assert (window._NewGameMenuWindow__ai_difficulty_dropdown.get_selected_item().get_string()
                == "None")

        window._NewGameMenuWindow__ai_difficulty_dropdown.set_selected(1)
        assert not window._NewGameMenuWindow__ai_none_checkbutton.get_active()
        assert window._NewGameMenuWindow__ai_x_checkbutton.get_active()

        window._NewGameMenuWindow__ai_difficulty_dropdown.set_selected(0)
        assert window._NewGameMenuWindow__ai_none_checkbutton.get_active()
        assert not window._NewGameMenuWindow__ai_x_checkbutton.get_active()

    def test_on_window_closed(self, window):
        window.set_visible(True)
        assert not window._NewGameMenuWindow__prev_window.is_visible()
        assert window.is_visible()
        assert not window._NewGameMenuWindow__on_window_closed(None)
        assert window._NewGameMenuWindow__prev_window.is_visible()


class TestPauseMenu:
    @pytest.fixture
    def window(self):
        config = Config()
        config.set("blitz", "true")
        game_state = GameState(config)

        dummy_window = DummyPrevWindow()

        window = PauseMenuWindow(game_state, dummy_window)
        yield window
        window.destroy()

    def test_main_menu_title(self, window):
        assert window.get_title() == "Pause"

    def test_on_resume_clicked(self, window, mocker):
        # blitz mode is activated
        assert window._PauseMenuWindow__game.get_white_time() is not None

        mock_resume = mocker.patch.object(window._PauseMenuWindow__game, "resume_timer")

        window._PauseMenuWindow__resume_button.emit("clicked")
        mock_resume.assert_called_once()

        assert not window.is_visible()


class TestAboutMenu:
    @pytest.fixture
    def window(self):
        config = Config()
        game_state = GameState(config)

        dummy_window = DummyPrevWindow()

        window = AboutWindow(game_state, dummy_window)
        yield window
        window.destroy()

    def test_components_presence(self, window):
        back_button = None
        for child in window.get_child().observe_children():
            if isinstance(child, Gtk.Button) and "Back" in child.get_label():
                back_button = child

        assert back_button is not None

        # simulate a user interacting with the back button
        window.set_visible(True)
        assert not window._AboutWindow__prev_window.is_visible()
        back_button.emit("clicked")
        assert not window.is_visible()
        assert window._AboutWindow__prev_window.is_visible()

    def test_main_menu_title(self, window):
        assert window.get_title() == "About"


class TestHelpMenu:
    @pytest.fixture
    def window(self):
        config = Config()
        game_state = GameState(config)

        dummy_window = DummyPrevWindow()

        window = HelpWindow(game_state, dummy_window)
        yield window
        window.destroy()

    def test_components_presence(self, window):
        back_button = None
        for child in window.get_child().observe_children():
            if isinstance(child, Gtk.Button) and "Back" in child.get_label():
                back_button = child

        assert back_button is not None

        # simulate a user interacting with the back button
        window.set_visible(True)
        assert not window._HelpWindow__prev_window.is_visible()
        back_button.emit("clicked")
        assert not window.is_visible()
        assert window._HelpWindow__prev_window.is_visible()

    def test_main_menu_title(self, window):
        assert window.get_title() == "Help"
