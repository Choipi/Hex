import gettext
import os
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
from hex.tools.game_state import GameState
from hex.tools.file import FileModule
from hex.tools.logger import log, LogLevel
from hex.userinterfaces.gui.game_gui import GameWindow
from hex.userinterfaces.gui.new_game_menu_gui import NewGameMenuWindow
from hex.userinterfaces.gui.about_gui import AboutWindow
from hex.userinterfaces.gui.help_gui import HelpWindow


class MainMenuWindow(Gtk.ApplicationWindow):
    def __init__(self, game: GameState, file_module: FileModule, **kwargs):
        global lang
        lang = game.get_config().get("language")
        language_translations = gettext.translation(
            "bmain",
            localedir=os.path.join(os.path.dirname(__file__), "../locales"),
            languages=[lang],
            fallback=True)
        language_translations.install()

        global _
        _ = language_translations.gettext

        super().__init__(**kwargs, title=_("Main Menu"))
        self.set_resizable(False)
        self.connect("close-request", self.__on_window_closed)
        self.connect("show", self.__on_window_shown)

        self.__game = game
        self.__file_module = file_module

        # Main box (takes the whole window)
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)
        main_box.set_margin_top(10)
        main_box.set_margin_bottom(20)
        self.set_child(main_box)

        # Upper box (containing main buttons)
        top_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        top_box.set_margin_start(50)
        top_box.set_margin_end(50)
        main_box.append(top_box)

        self.__main_menu_label = Gtk.Label()
        self.__main_menu_label.set_markup('<span size="xx-large"><b>'
                                          + _("Main Menu") + '</b></span>')
        top_box.append(self.__main_menu_label)

        self.__main_buttons = {}

        self.__main_buttons_label_func = [
            ("New Game...", self.__on_new_game_clicked),
            ("Load Game...", self.__on_load_game_clicked),
            ("Contest", self.__on_contest_clicked),
            ("Exit", self.__on_exit_clicked)
        ]

        for label, fun in self.__main_buttons_label_func:
            button = Gtk.Button(label=label)
            button.set_size_request(200, -1)
            button.connect("clicked", fun)
            top_box.append(button)
            # We use the button's label as the key to easily change
            # its label when the user changes the language
            self.__main_buttons[label] = button

        # Spacer to push boxes top and bottom boxes to the borders
        spacer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        spacer.set_vexpand(True)
        main_box.append(spacer)

        # Lower box (about, help, language…)
        bottom_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        main_box.append(bottom_box)

        # Lower buttons - Left
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.__about_button = Gtk.Button(label=_("About..."))
        self.__about_button.connect("clicked", self.__on_about_clicked)
        self.__help_button = Gtk.Button(label=_("Help..."))
        self.__help_button.connect("clicked", self.__on_help_clicked)
        left_box.append(self.__about_button)
        left_box.append(self.__help_button)

        # Spacer to push bottom boxes to the borders
        spacer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        spacer.set_hexpand(True)

        # Lower buttons - Right
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        # Using a box just for the label to center its content
        # vertically
        language_label_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        language_label_box.set_vexpand(True)
        right_box.append(language_label_box)

        lang = self.__game.get_config().get("language")

        self.__language_label = Gtk.Label(label=_("Language : ")
                                          + lang.upper())
        self.__language_label.set_halign(Gtk.Align.CENTER)
        self.__language_label.set_valign(Gtk.Align.CENTER)
        self.__language_label.set_vexpand(True)
        language_label_box.append(self.__language_label)

        language_items = Gtk.StringList()
        for language_item in ["English", "Français"]:
            language_items.append(language_item)

        self.__language_dropdown = Gtk.DropDown(model=language_items)
        self.__language_dropdown.connect('notify::selected-item',
                                         self.__on_language_selected)

        # Sets the default value for the language dropdown component
        for index, language in enumerate(language_items):
            language_code = language.props.string[:2].lower()
            if language_code == lang.lower():
                self.__language_dropdown.set_selected(index)
                break

        right_box.append(self.__language_dropdown)

        bottom_box.append(left_box)
        bottom_box.append(spacer)
        bottom_box.append(right_box)

    """
    METHODS
    """

    def update_game_state(self, new_game_state: GameState):
        self.__game = new_game_state

    def __on_new_game_clicked(self, button):
        """
        Hides this window and displays the "New Game" window when the
        user clicks on the "New Game" button
        """
        log(LogLevel.DEBUG, "User interaction : New game")
        self.set_visible(False)
        new_game = NewGameMenuWindow(self.__game, self,
                                     application=self.get_application())
        new_game.present()

    def __file_chooser(self, callback):
        f = Gtk.FileFilter()
        f.set_name(_("Hex Game file"))
        f.add_suffix("hexgame")

        dialog = Gtk.FileChooserDialog(
            title=_("Choose a game file"),
            action=Gtk.FileChooserAction.OPEN,
            transient_for=self,
        )
        dialog.set_filter(f)
        dialog.add_button(_("Cancel"), Gtk.ResponseType.CANCEL)
        dialog.add_button(_("Open"), Gtk.ResponseType.ACCEPT)

        dialog.connect("response", callback)
        dialog.present()

    def __on_load_game_clicked(self, button):
        """
        Opens a file dialog when the user wants to load a game
        from a file by clicking on the "Load Game" button
        """
        log(LogLevel.DEBUG, "User interaction : Load game")
        self.__file_chooser(self.__game_file_dialog_callback)

    def __game_file_dialog_callback(self, dialog, response):
        """
        Callback function called when the user leaves the FileDialog
        after choosing a game file or closing the FileDialog.
        """
        if response == Gtk.ResponseType.ACCEPT:
            # The user chose a file
            file = dialog.get_file()
            try:
                log(LogLevel.DEBUG, f"Game file path is {file.get_path()}")
                self.__file_module.load_hexgame(path=file.get_path())
                self.set_visible(False)
                game_window = GameWindow(self.__game, self,
                                         application=self.get_application())
                game_window.present()
            except ValueError as error:
                log(LogLevel.ERROR, f"Error opening file: {error}")
            except GLib.Error as error:
                log(LogLevel.ERROR, f"Error opening file: {error.message}")
        # If a user canceled, nothing happens
        elif response == Gtk.ResponseType.CANCEL:
            log(LogLevel.DEBUG, "User cancelled the file dialog")
        # Destroy the dialog box after using it
        dialog.destroy()

    def __on_contest_clicked(self, button):
        """
        Opens a file dialog when the user wants to load a game
        from a file by clicking on the "Contest" button
        """
        log(LogLevel.DEBUG, "User interaction : Contest mode")
        self.__file_chooser(self.__contest_file_dialog_callback)

    def __contest_file_dialog_callback(self, dialog, response):
        """
        Callback function called when the user leaves the FileDialog
        after choosing a game file or closing the FileDialog.
        For the contest button.
        """
        if response == Gtk.ResponseType.ACCEPT:
            # The user chose a file
            file = dialog.get_file()
            try:
                log(LogLevel.DEBUG, f"Game file path is {file.get_path()}")
                self.__file_module.load_hexgame(path=file.get_path())
                if self.__game.is_game_over():
                    msg = _("Game is already over !")
                else:
                    msg = self.__game.contest()
                    filename, extension = file.get_path().split('.')
                    self.__file_module.save_as_hexgame(filename)
                    msg += " Move saved in file: " + file.get_path()
                popup = Gtk.Dialog(title=msg,
                                   transient_for=self,
                                   destroy_with_parent=True,
                                   use_header_bar=True,
                                   modal=True,
                                   height_request=0)
                popup.show()
            except ValueError as error:
                log(LogLevel.ERROR, f"Error opening file: {error}")
            except GLib.Error as error:
                log(LogLevel.ERROR, f"Error opening file: {error.message}")
        # If a user canceled, nothing happens
        elif response == Gtk.ResponseType.CANCEL:
            log(LogLevel.DEBUG, "User cancelled the file dialog")
        # Destroy the dialog box after using it
        dialog.destroy()

    def __on_exit_clicked(self, button):
        log(LogLevel.DEBUG, "User interaction : Exit program")
        self.close()

    def __on_about_clicked(self, button):
        """
        Hides this window and displays the "About" window when the user
        clicks on the "About" button
        """
        log(LogLevel.DEBUG, "User interaction : About program")
        self.set_visible(False)
        about_window = AboutWindow(self.__game, self,
                                   application=self.get_application())
        about_window.present()

    def __on_help_clicked(self, button):
        """
        Hides this window and displays the "Help" window when the user
        clicks on the "Help" button
        """
        log(LogLevel.DEBUG, "User interaction : Game help")
        self.set_visible(False)
        help_window = HelpWindow(self.__game, self,
                                 application=self.get_application())
        help_window.present()

    def __on_language_selected(self, dropdown, _pspec):
        """
        Updates the language stored in the configuration and call the
        function to refresh every labels when the user interacts with
        the language dropdown.
        """
        selected = dropdown.props.selected_item

        if selected is not None:
            language = selected.props.string
            self.__game.get_config().set("language",
                                         language[:2].upper())
            log(LogLevel.INFO, "User interaction : Language changed to "
                + language)
            self.update_language_text()

    def update_language_text(self):
        """
        Refreshes every label according to the language stored in the
        configuration.
        """
        global lang
        lang = self.__game.get_config().get("language").lower()
        language_translations = gettext.translation(
            "bmain",
            localedir=os.path.join(os.path.dirname(__file__), "../locales"),
            languages=[lang],
            fallback=True)
        language_translations.install()
        global _
        _ = language_translations.gettext

        self.set_title(_("Main Menu"))
        self.__main_menu_label.set_markup('<span size="xx-large"><b>'
                                          + _("Main Menu") + '</b></span>')

        for label, fun in self.__main_buttons_label_func:
            self.__main_buttons[label].set_label(_(label))

        self.__about_button.set_label(_("About..."))
        self.__help_button.set_label(_("Help..."))

        self.__language_label.set_label(_("Language : ") + lang.upper())

    def __on_window_closed(self, window):
        """
        When this window is closed, we make sure that every window
        is destroyed before exiting the program.
        """
        log(LogLevel.DEBUG, "Closing the main menu window")
        for w in Gtk.Window.list_toplevels():
            if not w.get_visible():
                w.destroy()
        return False

    def __on_window_shown(self, window):
        """
        If the user plays a game until it's over and tries to use contest
        mode, it will return "game over".
        This method is used to reset the game state so contest mode
        does not consider the game over because of the previous game.
        """
        self.__game.reset_game_state()
