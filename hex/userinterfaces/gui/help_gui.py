import gettext
import os
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from hex.tools.game_state import GameState
from hex.tools.logger import log, LogLevel


class HelpWindow(Gtk.ApplicationWindow):
    def __init__(self, game: GameState, prev_window: Gtk.ApplicationWindow,
                 **kwargs):
        global lang
        lang = game.get_config().get("language")
        language_translations = gettext.translation(
            "bhelp",
            localedir=os.path.join(os.path.dirname(__file__), "../locales"),
            languages=[lang],
            fallback=True)
        language_translations.install()

        global _
        _ = language_translations.gettext

        super().__init__(**kwargs, title=_("Help"))
        self.set_default_size(400, -1)
        self.set_resizable(False)
        self.connect("close-request", self.__on_window_closed)

        self.__game = game
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
            '<span size="xx-large"><b>' +
            _("Game Configuration") +
            '</b></span>')
        about_label.set_halign(Gtk.Align.CENTER)
        about_label.set_justify(Gtk.Justification.CENTER)
        main_box.append(about_label)

        config = [
            "board-size",
            "swap",
            "blitz",
            "time",
            "language",
            "ai",
            "ai-mode",
            "ai-depth",
            "ai-heuristic",
            "ai-time"
        ]

        config_grid = Gtk.Grid()
        config_grid.set_column_spacing(20)
        config_grid.set_row_spacing(5)
        config_grid.set_halign(Gtk.Align.CENTER)
        main_box.append(config_grid)

        i = 0
        for key in config:
            value = game.get_config().get(key)

            label_key = Gtk.Label()
            label_key.set_markup(
                f"<b>{key.replace('-', ' ').capitalize()}</b> :")
            label_key.set_halign(Gtk.Align.START)

            label_value = Gtk.Label(label=str(value))
            label_value.set_halign(Gtk.Align.START)

            config_grid.attach(label_key, (i % 2) * 2, i // 2, 1, 1)
            config_grid.attach(label_value, (i % 2) * 2 + 1, i // 2, 1, 1)
            i += 1

        rules_label = Gtk.Label()
        rules_label.set_markup(
            '<span size="xx-large"><b>' + _("Game Rules") + '</b></span>')
        rules_label.set_justify(Gtk.Justification.LEFT)
        main_box.append(rules_label)

        help_text = (
            _('<b>Your goal :</b>\n')
            + _('Connect your two opposite sides with an unbroken chain before\
 your opponent.\n\n')
            + _('<b>Gameplay :</b>\n')
            + _('- Two players: <b>Black</b> (left to right) and <b>White</b>\
 (top to bottom).\n')
            + _('- Players take turns placing a piece on an empty hexagon.\n')
            + _('- Once placed, pieces cannot be moved or removed.\n')
            + _('- The four corners belong to both adjacent sides.\n\n')
            + _('<b>Winning Condition :</b>\n')
            + _('The first player to create a continuous path between their\
 two sides wins.\n')
            + _('A draw is <b>impossible</b>.\n\n')
            + _('<b>Swap Rule (Optional) :</b>\n')
            + _('The second player can swap colors after the first move to\
 balance the game.\n\n')
            + _('<b>Basic Strategy :</b>\n')
            + _('- <b>Build, don’t just block</b> : focus on your path while\
 disrupting your opponent.\n')
            + _('- <b>Bridge formations</b> : Use bridges to make connections\
 between your pieces and block your opponent simultaneously.\n')
            + _('- <b>Hex connections</b> : each tile has <b>6 neighbors</b>,\
 offering multiple paths.\n')
            + _('- <b>Take your time</b> : If you can easily counter your own\
 move, find a stronger one.\n')
            + _('- <b>Never give up</b> : Don\'t lose hope until the game is\
 truly over, focus on securing winnable areas.')
        )

        help_label = Gtk.Label()
        help_label.set_markup(help_text)
        help_label.set_justify(Gtk.Justification.LEFT)
        help_label.set_wrap(True)
        main_box.append(help_label)

        back_button = Gtk.Button(label=_("Back"))
        back_button.connect("clicked", self.__on_back_clicked)
        main_box.append(back_button)

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
        log(LogLevel.DEBUG, "Closing the new game menu window")
        if self.__prev_window is not None:
            self.__prev_window.present()
        return False
