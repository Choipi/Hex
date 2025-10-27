from argparse import ArgumentParser, Namespace
from .logger import LogLevel, setup_logging_level, log
from .config import Config


def parse_args(args: list[str], config: Config) -> Namespace:
    """
    Collect the arguments of the program and verify their format.

    Parameters
    ----------
    args: list[str]
        args to check
    config: Config
        configuration of the game to be filled

    Returns
    -------
    ArgumentParser
        value of the option
    """
    parser = ArgumentParser(prog='hex', usage='%(prog)s [options]')

    # Display
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='show additional information')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='show debug messages')
    parser.add_argument('-V', '--version', action='store_true',
                        help='show package version and exit')
    parser.add_argument('-g', '--gui', action='store_true',
                        help='enable graphical user interface')
    parser.add_argument('-L', '--language', type=str, choices=['fr', 'en'],
                        help='display language of the interface')

    # Game
    parser.add_argument('-z', '--size', type=int, choices=range(1, 21),
                        help='choose the size of the board')
    parser.add_argument('-l', '--load', type=str, metavar='FILENAME',
                        help='load a game from a file')
    parser.add_argument('-s', '--swap', action='store_true',
                        help='enable swap action')
    parser.add_argument('-b', '--blitz', action='store_true',
                        help='enable blitz mode')
    parser.add_argument('-t', '--time', type=int, metavar='MINUTES',
                        help='choose a time limit in minutes for blitz mode')
    parser.add_argument('-c', '--contest', type=str, metavar='FILENAME',
                        help='show the next best move for the game stored '
                        'in FILENAME')

    # AI
    parser.add_argument('-a', '--ai', type=str, choices=['X', 'O', 'A'],
                        help='enable AI for player X, o or both')
    parser.add_argument('--ai-time', type=int,
                        help='choose a time limit in seconds for the ai search'
                        ' algorithm')
    parser.add_argument('--heuristic', type=str,
                        choices=['bfs',
                                 'random',
                                 'potential_threats',
                                 'path_oriented',
                                 'dijkstra'
                                 ],
                        help='choose heuristic to evaluate ai board for both'
                        ' sides')
    parser.add_argument('--heuristic-player-o', type=str,
                        choices=['bfs',
                                 'random',
                                 'potential_threats',
                                 'path_oriented',
                                 'dijkstra'
                                 ],
                        help='choose heuristic to evaluate ai board for'
                        ' player o')
    parser.add_argument('--heuristic-player-x', type=str,
                        choices=['bfs',
                                 'random',
                                 'potential_threats',
                                 'path_oriented',
                                 'dijkstra'
                                 ],
                        help='choose heuristic to evaluate ai board for'
                        ' player X')
    parser.add_argument('--ai-mode', type=str,
                        choices=['minimax',
                                 'mcts',
                                 'alpha_beta',
                                 'random_exploration'
                                 ],
                        help='choose ai algorithm to choose best move to play'
                        ' for both sides')
    parser.add_argument('--ai-mode-player-o', type=str,
                        choices=['minimax',
                                 'mcts',
                                 'alpha_beta',
                                 'random_exploration'
                                 ],
                        help='choose ai algorithm to choose best move to play'
                        ' for player o')
    parser.add_argument('--ai-mode-player-x', type=str,
                        choices=['minimax',
                                 'mcts',
                                 'alpha_beta',
                                 'random_exploration'
                                 ],
                        help='choose ai algorithm to choose best move to play'
                        ' for player X')
    parser.add_argument(
        '--ai-depth',
        type=int,
        metavar='DEPTH',
        help='choose a maximum depth for the search tree of the'
        ' ai')

    parsed_namespace = parser.parse_args(args)

    if config is None:
        return parsed_namespace

    return fill_config(config, parsed_namespace)


def fill_config(config: Config, parsed_namespace: Namespace) -> Namespace:
    """
    Check which options have been given by the user and, if an option
    is present, set this option in the configuration of the game with
    config.set.
    """
    if parsed_namespace.verbose:
        config.set("verbose", "true")
        setup_logging_level("-v")

    if parsed_namespace.debug:
        config.set("debug", "true")
        setup_logging_level("-d")

    if parsed_namespace.contest is not None:
        config.set("contest", parsed_namespace.contest)

    if parsed_namespace.version:
        config.set("version", "true")

    if parsed_namespace.gui:
        config.set("gui", "true")

    if parsed_namespace.language is not None:
        config.set("language", parsed_namespace.language)

    if parsed_namespace.blitz:
        config.set("blitz", "true")

    if parsed_namespace.time is not None:
        if not config.get("blitz"):
            log(LogLevel.WARNING, "Time limit for blitz mode's timer is given"
                " but blitz mode is off.")
        config.set("time", str(parsed_namespace.time))

    if parsed_namespace.ai is not None:
        config.set("ai", parsed_namespace.ai)

    if parsed_namespace.ai_time is not None:
        config.set("ai-time", str(parsed_namespace.ai_time))

    if parsed_namespace.heuristic is not None:
        config.set("ai-heuristic-player-o", parsed_namespace.heuristic)
        config.set("ai-heuristic-player-x", parsed_namespace.heuristic)

    if parsed_namespace.heuristic_player_o is not None:
        print(parsed_namespace.heuristic_player_o)
        config.set("ai-heuristic-player-o",
                   parsed_namespace.heuristic_player_o)
        print(config.get("ai-heuristic-player-o"))

    if parsed_namespace.heuristic_player_x is not None:
        config.set("ai-heuristic-player-x",
                   parsed_namespace.heuristic_player_x)

    if parsed_namespace.ai_mode is not None:
        config.set("ai-mode-player-o", parsed_namespace.ai_mode)
        config.set("ai-mode-player-x", parsed_namespace.ai_mode)

    if parsed_namespace.ai_mode_player_o is not None:
        config.set("ai-mode-player-o",
                   parsed_namespace.ai_mode_player_o)

    if parsed_namespace.ai_mode_player_x is not None:
        config.set("ai-mode-player-x",
                   parsed_namespace.ai_mode_player_x)

    if parsed_namespace.ai_depth is not None:
        config.set("ai-depth", str(parsed_namespace.ai_depth))

    if parsed_namespace.size is not None:
        config.set("board-size", str(parsed_namespace.size))

    if parsed_namespace.load is not None:
        config.set("load", parsed_namespace.load)

    if parsed_namespace.swap:
        config.set("swap", "true")

    return parsed_namespace
