import configparser
import sys
from signal import SIG_BLOCK, SIGUSR1, pthread_sigmask
from hex import __version__
from hex.userinterfaces.cli import Cli
from hex.userinterfaces.gui.gui import GUI
from hex.tools.game_state import GameState
from hex.tools.config import Config
from hex.tools.file import FileModule
from hex.tools.parser import parse_args

def load_game(file_m: FileModule, filename: str) -> None:
    try:
        file_m.load_hexgame(filename)
    except ValueError as err:
        print("Provided file is incorrect: " + str(err), file=sys.stderr)
        sys.exit(1)

def main():
    """
    Starting point of the program. Loads the configuration, a game
    file if specified, and starts the user interface.
    """
    # Mask signal SIGUSR1 used by blitz mode's timer
    pthread_sigmask(SIG_BLOCK, [SIGUSR1])

    # Load configuration from config.checkersrc
    try:
        config = Config()
    except (ValueError, FileNotFoundError,
            configparser.ParsingError) as error:
        print("Configuration issue: " + str(error), file=sys.stderr)
        sys.exit(1)
    # Parse user provided arguments
    parse_args(sys.argv[1:], config)

    if config.get("version"):
        print(__version__)
        sys.exit(0)
    # Initialize game structures
    game_state = GameState(config)
    file_m = FileModule(game_state)

    if (filename := config.get("load")) != "":
        load_game(file_m, filename)

    if (filename := config.get("contest")) != "":
        load_game(file_m, filename)
        print(game_state.contest())
        file, _ = filename.split('.')
        file_m.save_as_hexgame(file)
        print("Move saved in file: " + filename)
        sys.exit(0)
    # Start the selected user interfaces
    if config.get("gui"):
        GUI(game_state, file_m)
    else:
        display = Cli(game_state, file_m)
        display.start_game()

if __name__ == "__main__":
    main()
