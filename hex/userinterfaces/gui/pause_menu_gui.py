import gettext
import os
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
from hex.tools.game_state import GameState
from hex.tools.logger import log, LogLevel
from hex.tools.file import FileModule


class PauseMenuWindow(Gtk.Dialog):
    def __init__(self, game: GameState,
                 main_menu_window: Gtk.ApplicationWindow, **kwargs):
        # Language
        global lang
        lang = game.get_config().get("language")
        language_translations = \
            gettext.translation(
                "bpause",
                localedir=os.path.join(os.path.dirname(__file__),
                                       "../locales"),
                languages=[lang],
                fallback=True)
        language_translations.install()

        global _
        _ = language_translations.gettext

        super().__init__(**kwargs, title=_("Pause"))
        self.set_default_size(200, -1)
        self.set_resizable(False)

        # Blitz mode logic
        if game.get_config().get("blitz"):
            game.pause_timer()
        self.connect('close-request', self.__on_resume_clicked)

        self.__game = game
        self.__main_menu_window = main_menu_window

        # Main box (takes the whole window)
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)
        main_box.set_margin_top(10)
        main_box.set_margin_bottom(20)
        main_box.set_halign(Gtk.Align.CENTER)
        self.set_child(main_box)

        # Top section
        top_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        main_box.append(top_box)

        pause_label = Gtk.Label()
        pause_label.set_markup('<span size="xx-large"><b>'
                               + _("Pause")
                               + '</b></span>')
        top_box.append(pause_label)

        self.__resume_button = Gtk.Button(label=_("Resume"))
        self.__resume_button.connect("clicked", self.__on_resume_clicked)
        top_box.append(self.__resume_button)

        self.__save_game_button = Gtk.Button(label=_("Save..."))
        self.__save_game_button.connect("clicked", self.__on_save_game_clicked)
        top_box.append(self.__save_game_button)

        self.__restart_game_button = Gtk.Button(label=_("Restart..."))
        self.__restart_game_button.connect("clicked",
                                           self.__on_restart_clicked)
        top_box.append(self.__restart_game_button)

        spacer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        spacer.set_hexpand(True)
        main_box.append(spacer)

        # Lower section
        lower_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        main_box.append(lower_box)

        self.__main_menu_button = Gtk.Button(label=_("Main Menu..."))
        self.__main_menu_button.connect("clicked", self.__on_main_menu_clicked)
        lower_box.append(self.__main_menu_button)

        self.__give_up_button = Gtk.Button(label=_("Give up..."))
        self.__give_up_button.connect("clicked", self.__on_give_up_clicked)
        lower_box.append(self.__give_up_button)

    def __on_resume_clicked(self, button):
        """
        Unpause the game timer if blitz mode is activated and hides this window
        to resume the game
        """
        self.close()
        if self.__game.get_config().get("blitz"):
            self.__game.resume_timer()
        log(LogLevel.DEBUG, "User interaction : Resuming game")

    def __on_save_game_clicked(self, button):
        """
        Displays a FileChooserDialog to allow the player to save the current
        game.
        """
        log(LogLevel.DEBUG, "User interaction : Saving game")

        f = Gtk.FileFilter()
        f.set_name(_("Hex Game file"))
        f.add_suffix("hexgame")

        dialog = Gtk.FileChooserDialog(
            title=_("Save the current game"),
            action=Gtk.FileChooserAction.SAVE,
            transient_for=self,
        )
        dialog.set_filter(f)
        dialog.add_button(_("Cancel"), Gtk.ResponseType.CANCEL)
        dialog.add_button(_("Save"), Gtk.ResponseType.ACCEPT)

        dialog.connect("response", self.__save_game_dialog_callback)
        dialog.present()

    def __save_game_dialog_callback(self, dialog, response):
        """
        Handles the response from the FileChooserDialog when the user save the
        current game.

        - Displays a MessageDialog if the save is successful
        - Logs an error if it failed or the user canceled the Dialog
        """
        try:
            if response == Gtk.ResponseType.ACCEPT:
                file_path = dialog.get_file().get_path()

                file_module = FileModule(self.__game)
                file_module.save_as_hexgame(file_path)

                success_dialog = Gtk.MessageDialog(
                    transient_for=self,
                    modal=True,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.CLOSE,
                    text=_("Game successfully saved !"),
                )
                success_dialog.props.secondary_text = _(
                    ("Game saved at : {}.hexgame").format(file_path)
                )

                def success_callback(dialog, response):
                    dialog.destroy()

                success_dialog.connect("response", success_callback)
                success_dialog.present()

                log(LogLevel.INFO,
                    f"Game successfully saved at: {file_path}.hexgame")
            elif response == Gtk.ResponseType.CANCEL:
                log(LogLevel.DEBUG, "User cancelled the save dialog")
        except GLib.Error as error:
            log(LogLevel.ERROR, f"Error saving file: {error.message}")
        finally:
            dialog.destroy()

    def __on_restart_clicked(self, button):
        """
        Asks for confirmation before restarting the game as any unsaved
        progress will be lost.
        """
        log(LogLevel.DEBUG, "User interaction : Restarting the game")

        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text=_("Do you really want to go restart the game ?"),
        )

        dialog.props.secondary_text = _("Any unsaved progress will be lost.")

        def dialog_callback(dialog, response):
            dialog.destroy()

            if response == Gtk.ResponseType.YES:
                self.__game.reset_game_state()
                self.close()

        dialog.connect("response", dialog_callback)
        dialog.present()

    def __on_main_menu_clicked(self, button):
        """
        Asks for confirmation before going back to the main menu as any unsaved
        progress will be lost.
        """
        log(LogLevel.DEBUG, "User interaction : Going to main menu")

        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text=_("Do you really want to go back to the main menu ?"),
        )

        dialog.props.secondary_text = _("Any unsaved progress will be lost.")

        def dialog_callback(dialog, response):
            dialog.destroy()

            if response == Gtk.ResponseType.YES:
                for window in self.get_application().get_windows():
                    if window != self.__main_menu_window:
                        window.destroy()

                self.__main_menu_window.present()
                self.close()

        dialog.connect("response", dialog_callback)
        dialog.present()

    def __give_up_dialog_callback(self, dialog, response):
        """
        Displays a MessageDialog announcing which player gave up. The user has
        two options :
        - save the game to analyze it later
        - go back to the main menu.
        """
        SAVE_RESPONSE = 1
        MAIN_MENU_RESPONSE = 2
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            self.__game.give_up()
            give_up_dialog = Gtk.MessageDialog(
                transient_for=self,
                modal=True,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.NONE,
                text=_("Player {} gave up!").format(
                    self.__game.get_current_player()
                ),
            )
            give_up_dialog.add_button(_("Save"), SAVE_RESPONSE)
            give_up_dialog.add_button(_("Main Menu"), MAIN_MENU_RESPONSE)

            def dialog_callback(dialog, response):
                dialog.destroy()
                if response == SAVE_RESPONSE:
                    self.__on_save_game_clicked(None)
                elif response == MAIN_MENU_RESPONSE:
                    self.__on_main_menu_clicked(None)

            give_up_dialog.connect("response", dialog_callback)
            give_up_dialog.present()

    def __on_give_up_clicked(self, button):
        """
        Asks for confirmation before giving up as any unsaved progress will
        be lost.
        """
        log(LogLevel.DEBUG, "User interaction : user gave up")

        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=_("Do you really want to give up ?"),
        )

        dialog.props.secondary_text = _("Any unsaved progress will be lost.")

        dialog.connect("response", self.__give_up_dialog_callback)
        dialog.present()
