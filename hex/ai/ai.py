from .heuristics.path_oriented import HexBoardHeuristic
from .exploration_algorithms.minimax import Minimax
from .heuristics.random_heuristic import Random_Heuristic
from .heuristics.potential_threats import PotentialThreatsHeuristic
from .heuristics.bfs import BfsHeuristic
from .exploration_algorithms.random_exploration import Random_exploration
from .exploration_algorithms.mcts import MonteCarloTreeSearch
from .exploration_algorithms.alpha_beta import Alpha_Beta_pruning
from .heuristics.dijkstra import DijkstraHex
from .ai_heuristic import Heuristic
from .exploration_algorithm import Exploration_algorithm
from hex.tools.board import Board
from hex.tools.logger import log, LogLevel
from os import listdir
from os.path import isfile, join

HEURISTICS_PATH = "hex/ai/heuristics"
EXPLORATION_ALGORITHM_PATH = "hex/ai/heuristics"


class AIModule:

    def __init__(self, depth_O: int, depth_X: int, max_reflexion_time=5.0):
        if depth_O < 1:
            depth_O = 1
        if depth_X < 1:
            depth_X = 1
        if depth_O < 1 or depth_X < 1:
            log(LogLevel.WARNING, "AI depth can't be under 1. Depth set to 1.")
        self.__depth_O = depth_O
        self.__depth_X = depth_X
        self.__max_time = max_reflexion_time

        self.__heuristic_player_X: Heuristic = Random_Heuristic()
        self.__exploration_algorithm_player_X: Exploration_algorithm = Alpha_Beta_pruning(
            self.__heuristic_player_X, self.__depth_X, self.__max_time)
        self.__heuristic_player_O: Heuristic = Random_Heuristic()
        self.__exploration_algorithm_player_O: Exploration_algorithm = Alpha_Beta_pruning(
            self.__heuristic_player_O, self.__depth_O, self.__max_time)

        self.__current_ai_players: list[int] = []

    def set_ai_player(self, player: str):
        match player:
            case "X":
                self.__current_ai_players = [1]
            case "O":
                self.__current_ai_players = [0]
            case "A":
                self.__current_ai_players = [0, 1]
            case "None":
                self.__current_ai_players = []
            case _:
                self.__current_ai_players = []
                log(LogLevel.WARNING, "Cannot associate \"" + player +
                    "\" with a player, so no player will be set as"
                    " artificial player this game")

    def get_ai_players(self) -> list[int]:
        return self.__current_ai_players

    def get_all_heuristic_names(self):
        return [f.split('.py')[0] for f in listdir(
            HEURISTICS_PATH) if isfile(join(HEURISTICS_PATH, f))]

    def get_all_exploration_algorithms_names(self):
        return [f.split('.py')[0] for f in listdir(
            EXPLORATION_ALGORITHM_PATH) if isfile(join(HEURISTICS_PATH, f))]

    def set_heuristic_from_string(self, heuristic: str, player: int):
        match heuristic:
            case "random":
                match player:
                    case 0:
                        self.__heuristic_player_O = Random_Heuristic()
                        self.__exploration_algorithm_player_O.set_heuristic(
                            self.__heuristic_player_O)
                    case 1:
                        self.__heuristic_player_X = Random_Heuristic()
                        self.__exploration_algorithm_player_X.set_heuristic(
                            self.__heuristic_player_X)

            case "bfs":
                match player:
                    case 0:
                        self.__heuristic_player_O = BfsHeuristic()
                        self.__exploration_algorithm_player_O.set_heuristic(
                            self.__heuristic_player_O)
                    case 1:
                        self.__heuristic_player_X = BfsHeuristic()
                        self.__exploration_algorithm_player_X.set_heuristic(
                            self.__heuristic_player_X)

            case "potential_threats":
                match player:
                    case 0:
                        self.__heuristic_player_O = PotentialThreatsHeuristic()
                        self.__exploration_algorithm_player_O.set_heuristic(
                            self.__heuristic_player_O)
                    case 1:
                        self.__heuristic_player_X = PotentialThreatsHeuristic()
                        self.__exploration_algorithm_player_X.set_heuristic(
                            self.__heuristic_player_X)

            case "path_oriented":
                match player:
                    case 0:
                        self.__heuristic_player_O = HexBoardHeuristic()
                        self.__exploration_algorithm_player_O.set_heuristic(
                            self.__heuristic_player_O)
                    case 1:
                        self.__heuristic_player_X = HexBoardHeuristic()
                        self.__exploration_algorithm_player_X.set_heuristic(
                            self.__heuristic_player_X)

            case "dijkstra":
                match player:
                    case 0:
                        self.__heuristic_player_O = DijkstraHex()
                        self.__exploration_algorithm_player_O.set_heuristic(
                            self.__heuristic_player_O)
                    case 1:
                        self.__heuristic_player_X = DijkstraHex()
                        self.__exploration_algorithm_player_X.set_heuristic(
                            self.__heuristic_player_X)

            case _:
                match player:
                    case 0:
                        self.__heuristic_player_O = Random_Heuristic()
                        self.__exploration_algorithm_player_O.set_heuristic(
                            self.__heuristic_player_O)
                    case 1:
                        self.__heuristic_player_X = Random_Heuristic()
                        self.__exploration_algorithm_player_X.set_heuristic(
                            self.__heuristic_player_X)
                log(LogLevel.WARNING,
                    "Due to an unknown given heuristic name, random evaluation"
                    " will be set for player " + str(player))

    def set_exploration_algorithm_from_string(self, exploration_algorithm: str,
                                              player: int):
        match exploration_algorithm:
            case "minimax":
                match player:
                    case 0:
                        self.__exploration_algorithm_player_O = Minimax(
                            self.__heuristic_player_O, self.__depth_O,
                            self.__max_time)
                    case 1:
                        self.__exploration_algorithm_player_X = Minimax(
                            self.__heuristic_player_X, self.__depth_X,
                            self.__max_time)

            case "random_exploration":
                match player:
                    case 0:
                        self.__exploration_algorithm_player_O = Random_exploration(
                            self.__heuristic_player_O, self.__depth_O,
                            self.__max_time)
                    case 1:
                        self.__exploration_algorithm_player_X = Random_exploration(
                            self.__heuristic_player_X, self.__depth_X,
                            self.__max_time)
            case "mcts":
                match player:
                    case 0:
                        self.__exploration_algorithm_player_O = MonteCarloTreeSearch(
                            time_limit=self.__max_time)
                    case 1:
                        self.__exploration_algorithm_player_X = MonteCarloTreeSearch(
                            time_limit=self.__max_time)

            case "alpha_beta":
                match player:
                    case 0:
                        self.__exploration_algorithm_player_O = Alpha_Beta_pruning(
                            self.__heuristic_player_O, self.__depth_O, self.__max_time)
                    case 1:
                        self.__exploration_algorithm_player_X = Alpha_Beta_pruning(
                            self.__heuristic_player_X, self.__depth_X, self.__max_time)

            case _:
                match player:
                    case 0:
                        self.__exploration_algorithm_player_O = Random_exploration(
                            self.__heuristic_player_O, self.__depth_O, self.__max_time)
                    case 1:
                        self.__exploration_algorithm_player_X = Random_exploration(
                            self.__heuristic_player_X, self.__depth_X, self.__max_time)
                log(LogLevel.WARNING,
                    "Due to an unknown given exploration algorithm name,"
                    " random exploration  will be set for player "
                    + str(player))

    def ai_get_move(self, player: int, board: Board) -> tuple[str, int]:
        match player:
            case 0:
                return self.__exploration_algorithm_player_O.get_move(
                    player, board)
            case 1:
                return self.__exploration_algorithm_player_X.get_move(
                    player, board)
            case _:
                raise ValueError("Unknown player value")

    def get_h_O(self):
        return self.__heuristic_player_O

    def get_h_X(self):
        return self.__heuristic_player_X

    def get_a_O(self):
        return self.__exploration_algorithm_player_O

    def get_a_X(self):
        return self.__exploration_algorithm_player_X

    def get_ai_depth(self):
        return self.__depth_O

    def set_max_time(self, max_time: float):
        self.__max_time = max_time
