import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from hex.tools.game_state import GameState
from hex.tools.file import FileModule
from hex.userinterfaces.gui.main_menu_gui import MainMenuWindow

class GUI:
    def __init__(self, game: GameState, file_module: FileModule, **kargs):
        self.__game = game
        self.__file_module = file_module
        app = Gtk.Application(application_id='pdp.hex.python')
        app.connect('activate', self.on_activate)
        try:
            app.run(None)
        except KeyboardInterrupt:
            print()
            exit(0)

    def on_activate(self, app):
        win = MainMenuWindow(self.__game, self.__file_module, application=app)
        win.present()