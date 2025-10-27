import os
import threading
import gi
import gettext
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, GLib
from .board_gui import BoardWidget
from hex.userinterfaces.gui.pause_menu_gui import PauseMenuWindow
from hex.tools.game_over_state import GameOverState
from hex.tools.game_state import GameState
from hex.tools.logger import LogLevel, log


class GameWindow(Gtk.ApplicationWindow):
    """
    Class that represents and handles the GUI main game window.

    Attributes
    ----------
    game_state: Game_State
        The game state instance that links the window to the game data.
    main_menu_window: Gtk.ApplicationWindow
        The main menu window instance that links the window to the menu.
    css: Gtk.CssProvider
        Links the window to a css file used for styling.
    """

    def __init__(self, game_state: GameState,
                 main_menu_window: Gtk.ApplicationWindow, **kargs):
        """
        GameWindow's constructor.

        Parameters
        ----------
        game_state: Game_State
            The game state instance that links the window to the game data.
        main_menu_window: Gtk.ApplicationWindow
            The main menu window instance that links the window to the menu.
        """
        log(LogLevel.DEBUG, "GUI: Initialization of game menu started")
        self.__game_state = game_state
        self.__main_menu_window = main_menu_window
        global lang
        lang = self.__game_state.get_config().get("language")
        language_translations = gettext.translation(
            "bgame",
            localedir=os.path.join(os.path.dirname(__file__), "../locales"),
            languages=[lang],
            fallback=True)
        language_translations.install()

        global _
        _ = language_translations.gettext
        super().__init__(**kargs, title=_('Hex Game'))
        self.set_default_size(1600, 900)
        self.set_size_request(-1, -1)
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.connect("close-request", self.__on_window_closed)

        self.__board_widget = BoardWidget(self.__game_state)
        self.__board_click_gesture = Gtk.GestureClick.new()
        self.__board_click_gesture.connect("pressed", self.__on_board_clicked)
        self.__board_widget.add_controller(self.__board_click_gesture)

        self.__player_label = Gtk.Label()
        self.__O_time_label = Gtk.Label()
        self.__X_time_label = Gtk.Label()
        self.__done_moves_label = Gtk.Label()
        self.__undone_moves_label = Gtk.Label()
        self.__done_moves_label.set_yalign(0)
        self.__undone_moves_label.set_yalign(0)
        self.__top_margin_label = Gtk.Label()
        self.__botom_margin_label = Gtk.Label()
        self.__left_margin_label = Gtk.Label()
        self.__right_margin_label = Gtk.Label()

        self.__undo_button = Gtk.Button(label=_("Undo"))
        self.__redo_button = Gtk.Button(label=_("Redo"))
        self.__hint_button = Gtk.Button(label=_("Hint"))
        self.__pause_button = Gtk.Button(label=_("Pause..."))
        self.__undo_button.set_cursor_from_name("pointer")
        self.__redo_button.set_cursor_from_name("pointer")
        self.__hint_button.set_cursor_from_name("pointer")
        self.__pause_button.set_cursor_from_name("pointer")
        self.__undo_button.connect("clicked", self.__undo_button_clicked)
        self.__redo_button.connect("clicked", self.__redo_button_clicked)
        self.__hint_button.connect("clicked", self.__hint_button_clicked)
        self.__pause_button.connect("clicked", self.__pause_button_clicked)

        self.__css = Gtk.CssProvider()
        self.__css.load_from_file(Gio.file_new_for_path(
            "hex/userinterfaces/gui/resources/game_gui_style.css"))
        self.get_style_context().add_provider(
            self.__css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.__done_moves_label.get_style_context().add_provider(
            self.__css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.__undone_moves_label.get_style_context().add_provider(
            self.__css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.__O_time_label.get_style_context().add_provider(
            self.__css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.__X_time_label.get_style_context().add_provider(
            self.__css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.__player_label.get_style_context().add_provider(
            self.__css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.__undo_button.get_style_context().add_provider(
            self.__css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.__redo_button.get_style_context().add_provider(
            self.__css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.__hint_button.get_style_context().add_provider(
            self.__css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.__pause_button.get_style_context().add_provider(
            self.__css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.__grid = Gtk.Grid()
        self.__grid.set_column_homogeneous(True)
        self.__grid.set_row_homogeneous(True)

        self.__grid.attach(self.__top_margin_label, 0, 0, 24, 1)
        self.__grid.attach(self.__botom_margin_label, 0, 23, 24, 1)
        self.__grid.attach(self.__left_margin_label, 0, 1, 1, 22)
        self.__grid.attach(self.__right_margin_label, 23, 1, 1, 22)

        self.__grid.attach(self.__O_time_label, 1, 1, 6, 2)
        self.__grid.attach(self.__player_label, 8, 1, 6, 2)
        self.__grid.attach(self.__X_time_label, 16, 1, 6, 2)

        self.__grid.attach(self.__done_moves_label, 1, 5, 2, 14)
        self.__grid.attach(self.__board_widget, 3, 2, 18, 18)
        self.__grid.attach(self.__undone_moves_label, 21, 5, 2, 14)

        self.__grid.attach(self.__undo_button, 1, 21, 4, 2)
        self.__grid.attach(self.__redo_button, 7, 21, 4, 2)
        self.__grid.attach(self.__hint_button, 13, 21, 4, 2)
        self.__grid.attach(self.__pause_button, 19, 21, 4, 2)

        self.__update_player_display()
        self.__update_time_display()
        self.__update_history_display()

        self.__is_blitz = game_state.get_config().get("blitz")
        if self.__is_blitz:
            game_state.timer_set_gui_refresh_methods(
                [self.__update_time_display, self.__update_all_displays])
            game_state.start_timer()

        log(LogLevel.DEBUG,
            "GUI: Initialization of game menu completed")
        self.set_child(self.__grid)

        if self.__game_state.get_current_player() in self.__game_state.get_current_ai_players(
        ) and not self.__game_state.is_game_over():
            threading.Thread(target=self.__let_AI_play, daemon=True).start()

    def __update_time_display(self):
        """
        Updates the display of both players timers on the window.
        """
        if self.__game_state.get_config().get("blitz"):
            O_time = self.__game_state.get_white_time()
            X_time = self.__game_state.get_black_time()
            self.__O_time_label.set_markup(
                _("O's left time : ") +
                f"{int(O_time//60):02d}m{int(O_time%60):02d}s")
            self.__X_time_label.set_markup(
                _("X's left time : ") +
                f"{int(X_time//60):02d}m{int(X_time%60):02d}s")
        else:
            self.__O_time_label.set_markup(_("O's left time : ∞"))
            self.__X_time_label.set_markup(_("X's left time : ∞"))

    def __update_history_display(self):
        """
        Updates the display of both done and undone moves histories on the window.
        """
        done_moves, undone_moves = self.__game_state.get_last_moves()
        done_moves_markup = _("Done moves\n- - - - - - - - - - -")
        undone_moves_markup = _("Undone moves\n- - - - - - - - - - - - -")
        if len(done_moves) == 0:
            done_moves_markup += _("\nNone")
        else:
            for i in range(len(done_moves)):
                done_moves_markup += f"\n{done_moves[i]['round']}. {'0' if done_moves[i]['player'] == 0 else 'X'} {done_moves[i]['letter']}{done_moves[i]['number']}"
        if len(undone_moves) == 0:
            undone_moves_markup += _("\nNone")
        else:
            for i in range(len(undone_moves)):
                undone_moves_markup += f"\n{undone_moves[i]['round']}. {'0' if undone_moves[i]['player'] == 0 else 'X'} {undone_moves[i]['letter']}{undone_moves[i]['number']}"
        self.__done_moves_label.set_markup(done_moves_markup)
        self.__undone_moves_label.set_markup(undone_moves_markup)

    def __update_all_displays(self):
        """
        Updates the display of the whole window.
        """
        self.__update_history_display()
        self.__update_player_display()
        self.__board_widget.queue_draw()
        if self.__game_state.get_config().get("blitz"):
            self.__update_time_display()

    def __undo_button_clicked(self, button):
        """
        Handles the clicking of the undo button.

        Parameters
        ----------
        button:
            The button being clicked.
        """
        ret = self.__game_state.undo()
        if ret == 0:
            self.__update_all_displays()
            if self.__game_state.get_current_player() in self.__game_state.get_current_ai_players(
            ) and not self.__game_state.is_game_over():
                threading.Thread(
                    target=self.__let_AI_play,
                    daemon=True).start()
        elif ret == 1:
            popup = Gtk.Dialog(
                title=_("Undo not possible : the done moves list is currently empty."),
                transient_for=self,
                destroy_with_parent=True,
                use_header_bar=True,
                modal=True,
                height_request=0)
            popup.show()

    def __redo_button_clicked(self, button):
        """
        Handles the clicking of the redo button.

        Parameters
        ----------
        button:
            The button being clicked.
        """
        ret = self.__game_state.redo()
        if ret == 0:
            self.__update_all_displays()
            if self.__game_state.get_config().get("swap") and len(
                    self.__game_state.get_done_moves()) == 1:
                self.__swap()
            if self.__game_state.get_current_player() in self.__game_state.get_current_ai_players(
            ) and not self.__game_state.is_game_over():
                threading.Thread(
                    target=self.__let_AI_play,
                    daemon=True).start()
        elif ret == 1:
            popup = Gtk.Dialog(
                title=_("Redo not possible: the undone moves list is currently empty."),
                transient_for=self,
                destroy_with_parent=True,
                use_header_bar=True,
                modal=True,
                height_request=0)
            popup.show()

    def __hint_button_clicked(self, button):
        """
        Handles the clicking of the hint button.

        Parameters
        ----------
        button:
            The button being clicked.
        """
        if self.__game_state.is_game_over():
            msg = _("Game is over !")
        else:
            move = self.__game_state.get_ai().ai_get_move(
                self.__game_state.get_current_player(), self.__game_state.get_board())
            msg = _(
                "The best AI thinks that the current player should play the move '")
            msg += str(move[0]).upper() + str(move[1]) + "'"
        popup = Gtk.Dialog(
            title=msg,
            transient_for=self,
            destroy_with_parent=True,
            use_header_bar=True,
            modal=True,
            height_request=0)
        popup.show()

    def __pause_button_clicked(self, button):
        """
        Handles the clicking of the pause button.

        Parameters
        ----------
        button:
            The button being clicked.
        """
        if self.__is_blitz:
            self.__update_time_display()
        pause_menu = PauseMenuWindow(self.__game_state,
                                     main_menu_window=self.__main_menu_window,
                                     application=self.get_application(),
                                     transient_for=self,
                                     destroy_with_parent=True,
                                     use_header_bar=True,
                                     modal=True)

        def on_pause_menu_destroyed(pausemenu: PauseMenuWindow):
            self.__update_all_displays()
        pause_menu.connect("unmap", on_pause_menu_destroyed)
        pause_menu.present()

    def __update_player_display(self):
        """
        Updates the display of the current player playing.
        """
        if (self.__game_state.is_game_over()):
            self.__player_label.set_markup(
                _("Game over ! Winner : ") +
                f"{'O' if self.__game_state.get_winner() == GameOverState.WHITE_WON else 'X'}")
        else:
            markup = _("Round n°") \
                + f"{self.__game_state.get_current_game_round()}, " \
                + _("current player : ") \
                + f"{'O' if self.__game_state.get_current_player() == 0 else 'X'}"
            if self.__game_state.get_current_player(
            ) in self.__game_state.get_current_ai_players():
                markup += _("\n--- AI IS CURRENTLY PLAYING ---")
            self.__player_label.set_markup(markup)

    def __let_AI_play(self):
        """
        Lets the AI play and disables any window interaction as long as the AI is playing.
        Made to be called as a daemon.
        """
        self.set_can_target(False)
        self.__game_state.ai_play_move(self.__game_state.get_current_player())
        GLib.idle_add(self.__update_all_displays)
        if self.__game_state.get_current_player() in self.__game_state.get_current_ai_players(
        ) and not self.__game_state.is_game_over():
            threading.Thread(target=self.__let_AI_play, daemon=True).start()
        else:
            self.set_can_target(True)
            if self.__game_state.get_config().get("swap") and len(
                    self.__game_state.get_done_moves()) == 1:
                GLib.idle_add(self.__swap)

    def __on_board_clicked(self, gesture, n_press, real_x, real_y):
        """
        Handles the clicking on the board widget.

        Parameters
        ----------
        gesture:
            The Gtk gesture being recognized.
        n_press:
            The number of simultaneous clicks.
        real_x:
            The xcoordinates of the click.
        real_y:
            The xcoordinates of the click.
        """
        if self.__board_widget.on_clicked(gesture, n_press, real_x, real_y):
            self.__update_all_displays()
            if self.__game_state.get_current_player() in self.__game_state.get_current_ai_players(
            ) and not self.__game_state.is_game_over():
                threading.Thread(
                    target=self.__let_AI_play,
                    daemon=True).start()
            elif self.__game_state.get_config().get("swap") and len(self.__game_state.get_done_moves()) == 1:
                self.__swap()

    def __swap(self):
        """
        Handles swapping.
        Made to be called when swap should occur.
        """
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text=_("Swap option is enabled and is now available so that X player can play over O player's move."),
        )
        dialog.props.secondary_text = _("Would you like to swap ?")

        def dialog_callback(dialog, response):
            if response == Gtk.ResponseType.YES:
                self.__game_state.swap()
                self.__update_all_displays()
                if self.__game_state.get_current_player() in self.__game_state.get_current_ai_players(
                ) and not self.__game_state.is_game_over():
                    threading.Thread(
                        target=self.__let_AI_play,
                        daemon=True).start()
            dialog.destroy()
        dialog.connect("response", dialog_callback)
        dialog.present()

    def __on_window_closed(self, window):
        """
        Handles the closing of the window.
        Made to be called when the window should be closed.

        Parameters
        ----------
        window:
            The window being closed.
        """
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text=_("Do you really want to close the game ?"),
        )
        dialog.props.secondary_text = _("Any unsaved progress will be lost.")

        def dialog_callback(dialog, response):
            dialog.destroy()
            if response == Gtk.ResponseType.YES:
                for window in self.get_application().get_windows():
                    window.destroy()
                self.close()
        dialog.connect("response", dialog_callback)
        dialog.present()
        # Returns True because only the dialog_callback should close this
        # window (return False would close this window instantly)
        return True
