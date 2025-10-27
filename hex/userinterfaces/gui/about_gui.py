import gettext
import os
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from hex import __version__
from hex.tools.game_state import GameState
from hex.tools.logger import log, LogLevel


class AboutWindow(Gtk.ApplicationWindow):
    def __init__(self, game: GameState, prev_window: Gtk.ApplicationWindow,
                 **kwargs):
        global lang
        lang = game.get_config().get("language")
        language_translations = gettext.translation(
            "babout",
            localedir=os.path.join(os.path.dirname(__file__), "../locales"),
            languages=[lang],
            fallback=True)
        language_translations.install()

        global _
        _ = language_translations.gettext

        super().__init__(**kwargs, title=_("About"))
        self.set_default_size(200, -1)
        self.set_resizable(False)
        self.connect("close-request", self.__on_window_closed)

        self.__prev_window = prev_window

        # Main box (takes the whole window)
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)
        main_box.set_margin_top(10)
        main_box.set_margin_bottom(20)
        main_box.set_halign(Gtk.Align.CENTER)
        self.set_child(main_box)

        about_label = Gtk.Label()
        about_label.set_markup(
            '<span size="xx-large"><b>' + _("Informations") + '</b></span>')
        about_label.set_halign(Gtk.Align.CENTER)
        about_label.set_justify(Gtk.Justification.CENTER)
        main_box.append(about_label)

        config = [
            "gui",
            "version",
            "verbose",
            "debug"
        ]

        for key in config:
            if key == "version":
                label = Gtk.Label()
                label.set_markup(
                    f"<b>{key.replace('-', ' ').capitalize()}</b> "
                    f": {__version__}")
                main_box.append(label)
                continue

            value = game.get_config().get(key)
            label = Gtk.Label()
            label.set_markup(f"<b>{key.replace('-', ' ').capitalize()}</b> "
                             f": {value}")
            main_box.append(label)

        spacer = Gtk.Box()
        main_box.append(spacer)

        contributors_label = Gtk.Label()
        contributors_label.set_markup(
            '<span size="xx-large"><b>' + _("Contributors") + '</b></span>')
        contributors_label.set_halign(Gtk.Align.CENTER)
        contributors_label.set_justify(Gtk.Justification.CENTER)
        main_box.append(contributors_label)

        authors = [{"name": "KUSTERS Timon",
                    "email": "timon.kusters@etu.u-bordeaux.fr"},
                   {"name": "HERR Mariano",
                    "email": "mariano.herr@etu.u-bordeaux.fr"},
                   {"name": "HUBINCU Morgan",
                    "email": "morgan.hubincu@etu.u-bordeaux.fr"},
                   {"name": "ROCHETEAU Yohann",
                    "email": "yohann.rocheteau@etu.u-bordeaux.fr"},
                   {"name": "GUITARD Paul",
                    "email": "paul.guitard@etu.u-bordeaux.fr"}]

        for item in authors:
            label = Gtk.Label()
            label.set_markup(f"<b>{item['name']}</b>\n"
                             f"{item['email']}")
            label.set_selectable(True)
            label.set_halign(Gtk.Align.CENTER)
            label.set_justify(Gtk.Justification.CENTER)
            main_box.append(label)

        back_button = Gtk.Button(label=_("Back"))
        back_button.connect("clicked", self.__on_back_clicked)
        main_box.append(back_button)

        # Without grab_focus(), the first selectable label is highlighted
        back_button.grab_focus()

    def __on_back_clicked(self, button):
        """
        When the user hits the "Back" button, the window acts like
        if it was closed
        """
        log(LogLevel.DEBUG, "User interaction : Going back to main menu")
        self.close()

    def __on_window_closed(self, window):
        """
        Displays the main menu if the user closes this window
        """
        log(LogLevel.DEBUG, "Closing the about window")
        if self.__prev_window is not None:
            self.__prev_window.present()
        return False
