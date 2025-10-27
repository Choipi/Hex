import gettext
import os
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from hex.tools.game_state import GameState
from hex.tools.logger import log, LogLevel
from hex.userinterfaces.gui.game_gui import GameWindow


class NewGameMenuWindow(Gtk.ApplicationWindow):
    def __init__(self, game: GameState, prev_window: Gtk.ApplicationWindow,
                 **kwargs):
        global lang
        lang = game.get_config().get("language")
        language_translations = gettext.translation(
            "bnew",
            localedir=os.path.join(os.path.dirname(__file__), "../locales"),
            languages=[lang],
            fallback=True)
        language_translations.install()

        global _
        _ = language_translations.gettext

        super().__init__(**kwargs, title=_("New Game"))
        self.set_default_size(150, 550)
        self.set_size_request(150, 550)
        self.set_resizable(False)
        self.connect("close-request", self.__on_window_closed)

        self.__game = game
        self.__prev_window = prev_window

        self.__ai_difficulties = {
            "Easy": {"ai-mode": "mcts",
                     "ai-depth": 3,
                     "ai-heuristic": "dijkstra",
                     "ai-time": 15},
            "Hard": {"ai-mode": "alpha_beta",
                     "ai-depth": 3,
                     "ai-heuristic": "dijkstra",
                     "ai-time": 60},
        }

        # Main box (takes the whole window)
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)
        main_box.set_margin_top(10)
        main_box.set_halign(Gtk.Align.CENTER)
        self.set_child(main_box)

        new_game_label = Gtk.Label()
        new_game_label.set_markup(
            '<span size="xx-large"><b>' + _("New Game") + '</b></span>')
        main_box.append(new_game_label)

        general_label = Gtk.Label()
        general_label.set_markup(
            '<span size="large"><b>' + _("General Settings") + '</b></span>')
        main_box.append(general_label)

        # Size section
        size = game.get_config().get("board-size")
        size_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        main_box.append(size_box)

        size_label = Gtk.Label(label=_("Board size"))
        size_box.append(size_label)

        spacer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        spacer.set_hexpand(True)
        size_box.append(spacer)

        size_adjustment = Gtk.Adjustment(value=size, lower=1, upper=20,
                                         step_increment=1, page_increment=1)
        self.__size_entry = Gtk.SpinButton(adjustment=size_adjustment)
        self.__size_entry.connect("value-changed",
                                  self.__on_size_entry_changed)
        size_box.append(self.__size_entry)

        # Blitz section
        blitz = game.get_config().get("blitz")
        blitz_time = game.get_config().get("time")

        blitz_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        main_box.append(blitz_box)

        self.__blitz_checkbutton = Gtk.CheckButton(label=_("Blitz"))
        self.__blitz_checkbutton.set_active(blitz)
        self.__blitz_checkbutton.connect("toggled", self.__on_blitz_toggled)
        blitz_box.append(self.__blitz_checkbutton)

        spacer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        spacer.set_hexpand(True)
        blitz_box.append(spacer)

        blitz_time_label = Gtk.Label(label=_("Time (min)"))
        blitz_box.append(blitz_time_label)
        blitz_adjustment = Gtk.Adjustment(value=blitz_time, lower=1, upper=180,
                                          step_increment=1, page_increment=10)
        self.__blitz_time_entry = Gtk.SpinButton(adjustment=blitz_adjustment)
        self.__blitz_time_entry.connect("value-changed",
                                        self.__on_blitz_entry_changed)
        blitz_box.append(self.__blitz_time_entry)

        self.__blitz_time_entry.set_sensitive(blitz)

        # Swap section
        swap = game.get_config().get("swap")

        self.__swap_checkbutton = Gtk.CheckButton(label=_("Swap"))
        self.__swap_checkbutton.set_active(swap)
        self.__swap_checkbutton.connect("toggled", self.__on_swap_toggled)

        main_box.append(self.__swap_checkbutton)

        # AI Section
        general_label = Gtk.Label()
        general_label.set_markup(
            '<span size="large"><b>' + _("AI Settings") + '</b></span>')
        main_box.append(general_label)

        ai_player = game.get_config().get("ai")

        ai_notebook = Gtk.Notebook()
        ai_notebook.set_vexpand(True)
        main_box.append(ai_notebook)

        # AI - Simple Setup
        ai_simple_container_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                                          spacing=15)
        ai_simple_container_box.set_margin_start(50)
        ai_simple_container_box.set_margin_end(50)
        ai_simple_container_box.set_margin_top(20)
        ai_simple_container_box.set_margin_bottom(20)
        ai_notebook.append_page(ai_simple_container_box,
                                tab_label=Gtk.Label(label=_("Simple")))

        self.__ai_simple_none_text = _("Player vs Player : no AI is involved.\
\n\nIf you wish to play against an AI, select another option from the dropdown\
 above, or adjust the settings in the Advanced tab.")

        self.__ai_simple_hard_text = _("This mode is designed for advanced \
players.\n\nThe AI will have more time to analyze the game in-depth, using \
sophisticated algorithms.")

        self.__ai_simple_easy_text = _("This mode is designed for beginners.\n\
\nThe AI will make simple moves, it won't analyze the game deeply.")

        self.__ai_simple_custom_text = _("Custom settings.\n\nManually adjust\
 the AI settings as needed, in the Advanced tab.")

        self.__ai_simple_label = Gtk.Label(
            label=(self.__ai_simple_none_text
                   if ai_player == "None" else self.__ai_simple_custom_text))
        self.__ai_simple_label.set_wrap(True)

        self.__ai_difficulty_items = Gtk.StringList()
        self.__ai_difficulty_map = {
            "None": _("None"),
            "Easy": _("Easy"),
            "Hard": _("Hard"),
            "Custom": _("Custom")
        }
        for ai_difficulty_item in self.__ai_difficulty_map.values():
            self.__ai_difficulty_items.append(ai_difficulty_item)

        self.__ai_difficulty_dropdown = Gtk.DropDown(
            model=self.__ai_difficulty_items)
        self.__ai_difficulty_dropdown.connect("notify::selected",
                                              self.__on_difficulty_changed)

        if ai_player == "None":
            self.__ai_difficulty_dropdown.set_selected(0)
        else:
            self.__ai_difficulty_items.append(_("Custom"))
            self.__ai_difficulty_dropdown.set_selected(3)

        ai_simple_container_box.append(self.__ai_difficulty_dropdown)
        ai_simple_container_box.append(self.__ai_simple_label)

        # AI - Advanced Setup
        ai_advanced_container_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10)
        ai_advanced_container_box.set_margin_start(10)
        ai_advanced_container_box.set_margin_end(10)
        ai_advanced_container_box.set_margin_top(10)
        ai_advanced_container_box.set_margin_bottom(10)

        ai_notebook.append_page(ai_advanced_container_box,
                                tab_label=Gtk.Label(label=_("Advanced")))

        # AI Players
        ai_player_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                                spacing=5)
        ai_advanced_container_box.append(ai_player_box)

        ai_player_label = Gtk.Label(label=_("AI Player : "))

        self.__ai_none_checkbutton = Gtk.CheckButton(label=_("None"))
        self.__ai_x_checkbutton = Gtk.CheckButton(
            label="X",
            group=self.__ai_none_checkbutton)
        self.__ai_o_checkbutton = Gtk.CheckButton(
            label="O",
            group=self.__ai_none_checkbutton)
        self.__ai_a_checkbutton = Gtk.CheckButton(
            label="A",
            group=self.__ai_none_checkbutton)
        self.__ai_buttons = {
            "None": self.__ai_none_checkbutton,
            "X": self.__ai_x_checkbutton,
            "O": self.__ai_o_checkbutton,
            "A": self.__ai_a_checkbutton
        }

        if ai_player in self.__ai_buttons:
            self.__ai_buttons[ai_player].set_active(True)

        # AI - Setup initial value for Radio buttons
        for button in [self.__ai_none_checkbutton,
                       self.__ai_x_checkbutton,
                       self.__ai_o_checkbutton,
                       self.__ai_a_checkbutton]:
            button.connect("toggled", self.__on_ai_radio_toggled)

        ai_player_help = Gtk.Image.new_from_icon_name("dialog-question")
        ai_player_help.set_tooltip_text(
            _("Select which player the AI will control\n")
            + _("- None: No AI assistance\n")
            + _("- X: AI controls player X\n")
            + _("- O: AI controls player O\n")
            + _("- A: AI controls all players"))

        ai_player_box.append(ai_player_label)
        ai_player_box.append(ai_player_help)
        ai_player_box.append(self.__ai_none_checkbutton)
        ai_player_box.append(self.__ai_x_checkbutton)
        ai_player_box.append(self.__ai_o_checkbutton)
        ai_player_box.append(self.__ai_a_checkbutton)

        # AI Mode
        ai_mode_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                              spacing=5)
        ai_advanced_container_box.append(ai_mode_box)

        # Map a user-friendly value to its internal value
        self.__ai_modes = {
            _("Minimax"): "minimax",
            _("αβ-pruning"): "alpha_beta",
            _("Random exploration"): "random_exploration",
            _("Monte Carlo Tree Search"): "mcts"
        }
        ai_mode_items = Gtk.StringList()
        for ai_mode_item in self.__ai_modes.keys():
            ai_mode_items.append(ai_mode_item)

        # AI Mode - player X
        ai_mode_player_X = game.get_config().get("ai-mode-player-x")
        ai_mode_player_X_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                                       spacing=5)
        ai_mode_box.append(ai_mode_player_X_box)

        ai_mode_player_X_label = Gtk.Label(label=_("AI Mode (player X)"))
        ai_mode_player_X_box.append(ai_mode_player_X_label)

        spacer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        spacer.set_hexpand(True)
        ai_mode_player_X_box.append(spacer)

        self.__ai_mode_player_X_dropdown = Gtk.DropDown(model=ai_mode_items)

        for index, value in enumerate(self.__ai_modes.values()):
            if value == ai_mode_player_X:
                self.__ai_mode_player_X_dropdown.set_selected(index)
                break

        ai_mode_player_X_box.append(self.__ai_mode_player_X_dropdown)

        self.__ai_mode_player_X_dropdown.set_sensitive(
            ai_player.upper() == "X" or ai_player.upper() == "A")

        # AI Mode - player O
        ai_mode_player_O = game.get_config().get("ai-mode-player-o")
        ai_mode_player_O_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                                       spacing=5)
        ai_mode_box.append(ai_mode_player_O_box)

        ai_mode_player_O_label = Gtk.Label(label=_("AI Mode (player O)"))
        ai_mode_player_O_box.append(ai_mode_player_O_label)

        spacer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        spacer.set_hexpand(True)
        ai_mode_player_O_box.append(spacer)

        self.__ai_mode_player_O_dropdown = Gtk.DropDown(model=ai_mode_items)

        for index, value in enumerate(self.__ai_modes.values()):
            if value == ai_mode_player_O:
                self.__ai_mode_player_O_dropdown.set_selected(index)
                break

        ai_mode_player_O_box.append(self.__ai_mode_player_O_dropdown)

        self.__ai_mode_player_O_dropdown.set_sensitive(
            ai_player.upper() == "O" or ai_player.upper() == "A")

        # AI Depth
        ai_depth = game.get_config().get("ai-depth")
        ai_depth_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                               spacing=0)
        ai_advanced_container_box.append(ai_depth_box)

        ai_depth_label = Gtk.Label(label=_("AI Depth"))
        ai_depth_box.append(ai_depth_label)

        spacer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        spacer.set_hexpand(True)
        ai_depth_box.append(spacer)

        ai_depth_adjustment = Gtk.Adjustment(value=ai_depth, lower=1, upper=4,
                                             step_increment=1,
                                             page_increment=1)
        self.__ai_depth_entry = Gtk.SpinButton(adjustment=ai_depth_adjustment)
        self.__ai_depth_entry.connect("value-changed",
                                      self.__on_ai_depth_entry_changed)
        ai_depth_box.append(self.__ai_depth_entry)

        self.__ai_depth_entry.set_sensitive(ai_player.upper() != "NONE")

        # AI Heuristic
        ai_heuristic_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                                   spacing=5)
        ai_advanced_container_box.append(ai_heuristic_box)

        # Map a user-friendly value to its internal value
        self.__ai_heuristics = {
            _("Path oriented"): "path_oriented",
            _("Potential threats"): "potential_threats",
            _("Random"): "random",
            _("BFS"): "bfs",
            _("Dijkstra"): "dijkstra"}

        ai_heuristic_items = Gtk.StringList()
        for ai_heuristic_item in self.__ai_heuristics.keys():
            ai_heuristic_items.append(ai_heuristic_item)

        # AI Heuristic - Player X
        ai_heuristic_player_X = game.get_config().get("ai-heuristic-player-x")
        ai_heuristic_player_X_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        ai_heuristic_box.append(ai_heuristic_player_X_box)

        ai_heuristic_player_X_label = Gtk.Label(
            label=_("AI Heuristic (player X)"))
        ai_heuristic_player_X_box.append(ai_heuristic_player_X_label)

        spacer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        spacer.set_hexpand(True)
        ai_heuristic_player_X_box.append(spacer)

        self.__ai_heuristic_player_X_dropdown = Gtk.DropDown(
            model=ai_heuristic_items)
        for index, value in enumerate(self.__ai_heuristics.values()):
            if value == ai_heuristic_player_X:
                self.__ai_heuristic_player_X_dropdown.set_selected(index)
                break

        ai_heuristic_player_X_box.append(self.__ai_heuristic_player_X_dropdown)

        self.__ai_heuristic_player_X_dropdown.set_sensitive(
            ai_player.upper() == "X" or ai_player.upper() == "A")

        # AI Heuristic - Player O
        ai_heuristic_player_O = game.get_config().get("ai-heuristic-player-o")
        ai_heuristic_player_O_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        ai_heuristic_box.append(ai_heuristic_player_O_box)

        ai_heuristic_player_O_label = Gtk.Label(
            label=_("AI Heuristic (player O)"))
        ai_heuristic_player_O_box.append(ai_heuristic_player_O_label)

        spacer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        spacer.set_hexpand(True)
        ai_heuristic_player_O_box.append(spacer)

        self.__ai_heuristic_player_O_dropdown = Gtk.DropDown(
            model=ai_heuristic_items)
        for index, value in enumerate(self.__ai_heuristics.values()):
            if value == ai_heuristic_player_O:
                self.__ai_heuristic_player_O_dropdown.set_selected(index)
                break

        ai_heuristic_player_O_box.append(self.__ai_heuristic_player_O_dropdown)

        self.__ai_heuristic_player_O_dropdown.set_sensitive(
            ai_player.upper() == "O" or ai_player.upper() == "A")

        # AI Time
        ai_time = game.get_config().get("ai-time")
        ai_time_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                              spacing=5)
        ai_advanced_container_box.append(ai_time_box)

        ai_time_label = Gtk.Label(label=_("AI time (s)"))
        ai_time_box.append(ai_time_label)

        spacer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        spacer.set_hexpand(True)
        ai_time_box.append(spacer)

        ai_time_adjustment = Gtk.Adjustment(value=ai_time, lower=1, upper=60,
                                            step_increment=1,
                                            page_increment=1)
        self.__ai_time_entry = Gtk.SpinButton(adjustment=ai_time_adjustment)
        self.__ai_time_entry.connect("value-changed",
                                     self.__on_ai_time_entry_changed)
        ai_time_box.append(self.__ai_time_entry)

        self.__ai_time_entry.set_sensitive(ai_player.upper() != "NONE")

        # Lower buttons
        self.__error_label = Gtk.Label()
        self.__error_label.set_visible(False)
        self.__error_label.set_wrap(True)
        main_box.append(self.__error_label)

        lower_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        lower_box.set_margin_bottom(10)

        main_box.append(lower_box)

        back_button = Gtk.Button(label=_("Back"))
        back_button.connect("clicked", self.__on_back_clicked)
        if prev_window is None:
            back_button.set_sensitive(False)
            back_button.set_tooltip_text(_("Back button unavailable"))

        start_button = Gtk.Button(label=_("Start"))
        start_button.connect("clicked", self.__on_start_clicked)

        spacer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        spacer.set_hexpand(True)

        lower_box.append(back_button)
        lower_box.append(spacer)
        lower_box.append(start_button)

    """
    METHODS
    """

    def __on_size_entry_changed(self, spin_button):
        """Used for debug purposes only"""
        current_value = spin_button.get_value()
        log(LogLevel.DEBUG, f"current size value: {current_value}")

    def __on_blitz_entry_changed(self, spin_button):
        """Used for debug purposes only"""
        current_value = spin_button.get_value()
        log(LogLevel.DEBUG, f"current blitz time value: {current_value}")

    def __on_difficulty_changed(self, dropdown, param):
        """
        When the user changes the AI level from the "simple" tab, we
        update the helper text and update every values in the
        "advanced tab"

        - Retrieves the choosen AI difficulty
        - Retrieves the actual level linked to the translation
        - Updates the helper text under the dropdown
        - Updates the settings in advanced tab

        If no AI player is selected and the difficulty is not "None",
        it switches to player "X"
        If the difficulty changes back to "None", it switches back to
        player "None"
        """
        selected_index = dropdown.get_selected()
        selected_value = dropdown.get_model().get_string(selected_index)

        # We need to find the original value (not translated) to map
        # self.ai_difficulties
        original_value = selected_value
        for key, val in self.__ai_difficulty_map.items():
            if val == selected_value:
                original_value = key

        log(LogLevel.DEBUG, f"current difficulty: {original_value}")

        if original_value == "None":
            self.__ai_simple_label.set_label(self.__ai_simple_none_text)
        elif original_value == "Easy":
            self.__ai_simple_label.set_label(self.__ai_simple_easy_text)
        elif original_value == "Hard":
            self.__ai_simple_label.set_label(self.__ai_simple_hard_text)
        else:
            self.__ai_simple_label.set_label(self.__ai_simple_custom_text)

        if original_value == "None":
            self.__ai_none_checkbutton.props.active = True
            return

        # If the user changes the AI level, he wants to play against
        # an AI so this makes sure that an AI player is selected
        if self.__ai_none_checkbutton.props.active:
            self.__ai_x_checkbutton.props.active = True

        # We don't want to change anything in the Advanced tab if the user
        # manually changes the AI player from None
        if original_value == "Custom":
            return

        ai_mode_value = self.__ai_difficulties[original_value]["ai-mode"]
        for index, value in enumerate(self.__ai_modes.values()):
            if value == ai_mode_value:
                self.__ai_mode_player_X_dropdown.set_selected(index)
                break

        self.__ai_depth_entry.set_value(
            self.__ai_difficulties[original_value]["ai-depth"])

        ai_heuristic_value = (
            self.__ai_difficulties[original_value]["ai-heuristic"])

        for index, value in enumerate(self.__ai_heuristics.values()):
            if value == ai_heuristic_value:
                self.__ai_heuristic_player_X_dropdown.set_selected(index)
                break

        self.__ai_time_entry.set_value(
            self.__ai_difficulties[original_value]["ai-time"])

    def __on_ai_depth_entry_changed(self, spin_button):
        """Used for debug purposes only"""
        current_value = spin_button.get_value()
        log(LogLevel.DEBUG, f"current ai-depth value: {current_value}")

    def __on_ai_time_entry_changed(self, spin_button):
        """Used for debug purposes only"""
        current_value = spin_button.get_value()
        log(LogLevel.DEBUG, f"current ai-time value: {current_value}")

    def __on_blitz_toggled(self, button):
        """
        This function disables the blitz time entry if blitz mode is unchecked
        """
        is_active = button.props.active
        log(LogLevel.DEBUG, "Blitz mode " + ("enabled" if is_active else
                                             "disabled"))
        # Toggles the blitz time entry depending on the blitz checkbox
        self.__blitz_time_entry.set_sensitive(is_active)

    def __on_swap_toggled(self, button):
        """Used for debug purposes only"""
        is_active = button.props.active
        log(LogLevel.DEBUG, "Swap mode " + ("enabled" if is_active else
                                            "disabled"))

    def __on_ai_radio_toggled(self, button):
        """
        Disables the AI settings if the AI player is None
        """
        if button.get_active():
            label = button.get_label()
            log(LogLevel.DEBUG,
                f"AI selection changed to {label}")

            # Updates the selected value in the "simple" tab
            if label == _("None"):
                self.__ai_difficulty_dropdown.set_selected(0)

            # switches to "Custom" if dropdown is set to "None" but player
            # is not "None"
            if label != _("None")\
               and self.__ai_difficulty_dropdown.get_selected() == 0:
                self.__ai_difficulty_dropdown.set_selected(3)

        selected_player = button.get_label()
        enable_ai = selected_player != self.__ai_none_checkbutton.get_label()
        self.__ai_depth_entry.set_sensitive(enable_ai)
        self.__ai_time_entry.set_sensitive(enable_ai)

        # Enables / Disables the correct dropdowns based on the selected player
        dropdowns = {
            'A': [
                self.__ai_mode_player_X_dropdown,
                self.__ai_heuristic_player_X_dropdown,
                self.__ai_mode_player_O_dropdown,
                self.__ai_heuristic_player_O_dropdown,
            ],
            'X': [
                self.__ai_mode_player_X_dropdown,
                self.__ai_heuristic_player_X_dropdown
            ],
            'O': [
                self.__ai_mode_player_O_dropdown,
                self.__ai_heuristic_player_O_dropdown
            ],
        }

        if selected_player != 'A':
            for dropdown in dropdowns['A']:
                dropdown.set_sensitive(False)

        if selected_player in dropdowns:
            for dropdown in dropdowns[selected_player]:
                dropdown.set_sensitive(True)

    def __on_back_clicked(self, button):
        """
        When the user hits the "Back" button, the window acts like
        if it was closed
        """
        log(LogLevel.DEBUG, "User interaction : Going back to main menu")
        self.close()

    def __on_start_clicked(self, button):
        """
        Handles the start of a new game :
        - Validates user input, displays an error message if any field
        is invalid
        - Retrieves every value to update the configuration
        - Destroys this windows and start the game
        """
        board_size = self.__size_entry.get_text()
        blitz_time = self.__blitz_time_entry.get_text()

        if not board_size.isdigit() or not blitz_time.isdigit():
            error_message = "Size and/or Blitz time is not a positive number."
            log(LogLevel.ERROR, error_message)
            self.__error_label.set_text(error_message)
            return

        if int(board_size) < 1 or int(board_size) > 20:
            error_message = _("The board size must be a number between 1 and \
20.")
            log(LogLevel.ERROR, error_message)
            self.__error_label.set_text(error_message)
            self.__error_label.set_visible(True)
            return

        ai_label_to_id = {
            _("None"): "None",
            "X": "X",
            "O": "O",
            "A": "A"
        }
        active_ai = "None"
        for button in [self.__ai_none_checkbutton,
                       self.__ai_x_checkbutton,
                       self.__ai_o_checkbutton,
                       self.__ai_a_checkbutton]:
            if button.props.active:
                active_ai = ai_label_to_id.get(button.get_label(), "None")
                break

        new_config = {
            "board-size": board_size,
            "blitz": str(self.__blitz_checkbutton.get_active()),
            "time": blitz_time,
            "swap": str(self.__swap_checkbutton.get_active()),
            "ai": active_ai,
            "ai-mode-player-X": self.__ai_modes.get(
                self.__ai_mode_player_X_dropdown
                .get_selected_item().get_string(), "minimax"
            ),
            "ai-mode-player-O": self.__ai_modes.get(
                self.__ai_mode_player_O_dropdown
                .get_selected_item().get_string(), "minimax"
            ),
            "ai-depth": self.__ai_depth_entry.get_text(),
            "ai-heuristic-player-X": self.__ai_heuristics.get(
                self.__ai_heuristic_player_X_dropdown
                .get_selected_item().get_string(), "bfs"
            ),
            "ai-heuristic-player-O": self.__ai_heuristics.get(
                self.__ai_heuristic_player_O_dropdown
                .get_selected_item().get_string(), "bfs"
            ),
            "ai-time": self.__ai_time_entry.get_text()
        }
        log(LogLevel.DEBUG, "Modified config from GUI : " + str(new_config))

        for (key, value) in new_config.items():
            self.__game.get_config().set(key, value)

        log(LogLevel.INFO, "Configuration ready, starting the game…")

        # Creating a new Game_State to create a new board with the new config
        new_game_state = GameState(self.__game.get_config())
        # prev_window must be a MainMenuWindow
        self.__prev_window.update_game_state(new_game_state)

        game_window = GameWindow(new_game_state,
                                 self.__prev_window,
                                 application=self.get_application())
        game_window.present()
        self.destroy()

    def __on_window_closed(self, window):
        """
        Displays the main menu if the user closes this window
        """
        log(LogLevel.DEBUG, "Closing the new game menu window")
        if self.__prev_window is not None:
            self.__prev_window.present()
        return False
