from hex.ai.ai import AIModule
from .board import Board
from .history import History
from .config import Config
from .blitztimer import BlitzTimer
from .game_over_state import GameOverState


PLAYER_O = 0
PLAYER_X = 1


class GameState:
    """A class that handle all the operation related to the game structures

    Attributes
    ----------

    configuration: Config
        the game's configuration

    board: Board
        the game's board

    current_player: int
        a value keeping track of the current player:
        white is 0; black is 1

    game_round: int
        a value keeping track of the game round

    blitztimer: Blitztimer | None
        the game's blitztimer if in blitz mode

    history: History
        the game's history of moves

    ai_module: AI_Module
        structure containing all the ai data and methods

    game_comment: str
        a comment applied to the game that will in the save file if
        the game is ever saved

    game_over_state: GameOverState
        state that represents if the game is won and by who

    winning_path: list[tuple[str, int]]
        contains the winning connecting path. Always empty until a
        game ends with a move
    """

    def __init__(self, config: Config):
        """
        Parameters
        ----------
        config: Config
            the game's configuration read from the default config file
            or parsed from the user's args
        """
        # Configuration
        self.__configuration = config

        # Data of the game at the beginning
        self.__board = Board(self.__configuration.get("board-size"))
        self.__current_player = 0
        self.__game_round = 1
        self.__game_over_state = GameOverState.NO_WINNER
        self.__winning_path: list[tuple[str, int]] = []

        # Blitz and History
        if config.get("blitz"):
            self.__blitztimer = BlitzTimer(self, config.get("time"))
            self.__history = History(self.__blitztimer.get_default_time())
        else:
            self.__blitztimer = None
            self.__history = History()

        # AI
        self.__ai_module = AIModule(config.get(
            "ai-depth"), config.get("ai-depth"), config.get("ai-time"))
        self.__configure_ai_module()

        # Miscellaneous
        self.__game_comment = "§"

    def __configure_ai_module(self):
        config = self.__configuration

        self.__ai_module.set_exploration_algorithm_from_string(
            config.get("ai-mode-player-o"), PLAYER_O)

        self.__ai_module.set_exploration_algorithm_from_string(
            config.get("ai-mode-player-x"), PLAYER_X)

        if str(self.__ai_module.get_a_O()) != "Monte Carlo Tree Search":
            self.__ai_module.set_heuristic_from_string(
                config.get("ai-heuristic-player-o"), PLAYER_O)

        if str(self.__ai_module.get_a_X()) != "Monte Carlo Tree Search":
            self.__ai_module.set_heuristic_from_string(
                config.get("ai-heuristic-player-x"), PLAYER_X)

        self.__ai_module.set_ai_player(config.get("ai"))

    def get_game_dim(self) -> int:
        """
        Return the dimension of the current board.
        """
        return self.__board.get_dim()

    def get_current_game_round(self) -> int:
        """
        Return the current game round.
        """
        return self.__game_round

    def get_current_player(self) -> int:
        """
        Return the current player.
        """
        return self.__current_player

    def set_next_player(self) -> None:
        """
        Set the current player to the next player.
        """
        tmp_new_current_player_value = (self.__current_player + 1) % 2
        if tmp_new_current_player_value not in {PLAYER_O, PLAYER_X}:
            raise ValueError("invalid current_player value")
        if self.__configuration.get("blitz"):
            self.__blitztimer.next_player()
        self.__current_player = tmp_new_current_player_value

    def play_move(self, position: tuple[str, int]) -> int:
        """
        Update the board with the given move if the move is legal,
        returns True if the board is updated, returns False if nothing
        happened because of an illegal move.

        Parameters
        ----------
        letter: str
            The letter representing the column of the move.
        number: int
            The number representing the line of the move.

        Returns
        -------
        int
            - 0: valid move, tile updated
            - 1: invalid move, played on an already occupied tile,
                nothing happens
            - 2: invalid move, tile out of bounds
        """
        try:
            if self.__board.check_legal_move(position):
                self.__board.add_move(position, self.__current_player)
                self.__history.add_move(self.__game_round,
                                        self.__current_player,
                                        position[0], position[1],
                                        self.get_white_time(),
                                        self.get_black_time())
                self.__game_over_state = self.__board.has_connection()
                self.set_winning_path()
                self.set_next_player()
                if self.__current_player == PLAYER_O:
                    self.__game_round += 1
                return 0
            return 1
        except IndexError:
            return 2

    def board_to_string(self) -> str:
        """
        Returns
        -------
        String
            corresponding to the current board, to display
        """
        return str(self.__board)

    def is_game_over(self) -> bool:
        """
        Check if the game is over.

        Returns
        -------
        bool
            - True: game is over
            - False: game is not over
        """
        return self.__game_over_state.value > 0

    def get_winner(self) -> GameOverState:
        """
        Return the current winner.

        Returns
        -------
        GameOverState
            State representing the winner
            - GameOverState.NO_WINNER if nobody there's no winner
            - GameOverState.WHITE_WON if white is the game's winner
            - GameOverState.BLACK_WON if black is the game's winner
        """
        return self.__game_over_state

    def get_value_of_space(self, position: int | tuple[str, int]) -> int:
        """
        Return the value of the space at "position".

        Returns
        -------
        int
            0 if empty;
            1 if white;
            2 if black
        """
        return self.__board.get_space_value(position)

    def set_board(self, board: Board) -> None:
        """
        Set the board to the given board.

        Parameters
        ----------
        board: Board
            new board object
        """
        self.__board = board

    def set_history(self, history: History) -> None:
        """
        Set the history to the given history.

        Parameters
        ----------
        history: History
            new history object
        """
        self.__history = history

    def set_current_player(self, player: int) -> None:
        """
        Set the current player to 1 or 0 else raise an error.

        Parameters
        ----------
        player: int
            player id, 0 for white, 1 for black.

        Raises
        ------
        ValueError
            if an invalid player id is given
        """
        if player not in {PLAYER_O, PLAYER_X}:
            raise ValueError("invalid player id given: ", player)
        self.__current_player = player

    def set_current_game_round(self, game_round: int) -> None:
        """
        Set the current game round to the given round.

        Parameters
        ----------
        game_round: int

        Raises
        ------
        ValueError
            if an invalid round value is given
        """
        if game_round < 0:
            raise ValueError("invalid round value given: ", game_round)
        self.__game_round = game_round

    def reset_game_state(self) -> None:
        """
        Reset the game's state.
        """
        self.__current_player = PLAYER_O
        self.__game_round = 1
        self.__board.reset()
        self.__history.reset()
        if self.__blitztimer is not None:
            self.__blitztimer.reset()
        self.__game_comment = "§"
        self.set_game_over(GameOverState.NO_WINNER)

    def undo(self) -> int:
        """
        Revert a played move. If undo is possible, it
        will remove the move from the board and change the current
        player and the round accordingly.

        Returns
        -------
        int
            - 0 if the move has succesfully been reverted
            - 1 if the history is empty
            - 2 if an unexpected error occured
        """
        undone_move, swap_undone = self.__history.undo()
        if not undone_move:
            return 1
        try:
            self.__board.remove_move(
                (undone_move["letter"], undone_move["number"]),
                undone_move["player"]
            )
        except (TypeError, ValueError, IndexError):
            return 2
        # in case the game was in its finished state we reset the
        # game_over_state
        self.__game_over_state = GameOverState.NO_WINNER
        if self.__configuration.get("blitz"):
            self.__blitztimer.set_white_remaining_time(
                undone_move["white_time"])
            self.__blitztimer.set_black_remaining_time(
                undone_move["black_time"])
        if swap_undone:
            self.__game_round = 1
            self.__current_player = PLAYER_O
        else:
            self.set_next_player()
            if self.get_current_player() == PLAYER_X:
                self.__game_round -= 1
        if self.get_current_player() in self.get_current_ai_players() and len(
                self.__history.get_done_moves()) != 0:
            return self.undo()
        return 0

    def redo(self) -> int:
        """
        Replay a move previously undone. If redo is possible it will
        add the move to the board, then change the current player and
        finally change the round accordingly.

        Returns
        -------
        int
            - 0 if the move has succesfully been replayed
            - 1 if the history is empty
            - 2 if an unexpected error occured
        """
        redone_move = self.__history.redo()
        if not redone_move:
            return 1
        try:
            self.__board.add_move(
                (redone_move["letter"], redone_move["number"]),
                redone_move["player"]
            )
        except (TypeError, ValueError, IndexError):
            return 2
        self.__game_over_state = self.__board.has_connection()
        if self.__configuration.get("blitz"):
            self.__blitztimer.set_white_remaining_time(
                redone_move["white_time"])
            self.__blitztimer.set_black_remaining_time(
                redone_move["black_time"])
        self.set_next_player()
        if self.get_current_player() == PLAYER_O:
            self.__game_round += 1
        if self.get_current_player() in self.get_current_ai_players() and len(
                self.__history.get_undone_moves()) != 0:
            return self.redo()
        return 0

    def are_board_equals(self, board: Board) -> bool:
        """
        Check if the board are equals.

        Parameters
        ----------
        board: Board
            board that will be compared to this game's board

        Returns
        -------
            bool
                -True: board are equals
                -False: board are not equals
        """
        return self.__board == board

    def get_last_moves(self) -> tuple[list, list]:
        """
        Return the <#game's dimension> last played moves.
        """
        return self.__history.get_last_moves(self.__board.get_dim())

    def add_game_comment(self, comment: str) -> None:
        """
        Set the game comment.

        Parameters
        ----------
        comment: str
            comment that will be added to the save file
        """
        self.__game_comment = comment

    def get_game_comment(self) -> str:
        """
        Return the game comment.
        """
        return self.__game_comment

    def get_done_moves(self) -> list:
        """
        Return the list of every played move.
        """
        return self.__history.get_done_moves()

    def get_undone_moves(self) -> list:
        """
        Return the list of every undone move.
        """
        return self.__history.get_undone_moves()

    def set_game_over(self, state: GameOverState) -> None:
        """
        Set the current game over state to the given state.

        Parameters
        ----------
        state: GameOverState
            game's winner
        """
        self.__game_over_state = state

    def start_timer(self) -> None:
        """
        Start the timer if blitz mode is activated.
        """
        if self.__configuration.get("blitz"):
            self.__blitztimer.start()

    def resume_timer(self) -> None:
        """
        Resume the blitz timer after the it has been paused if blitz
        mode is activated.
        """
        if self.__configuration.get("blitz"):
            self.__blitztimer.resume()

    def pause_timer(self) -> None:
        """
        Pause the blitz timer if blitz mode is activated.
        """
        if self.__configuration.get("blitz"):
            self.__blitztimer.pause()

    def get_white_time(self) -> float | None:
        """
        Return the remaining time of white if blitz mode is activated.
        """
        if self.__configuration.get("blitz"):
            return self.__blitztimer.get_white_remaining_time()
        return None

    def get_black_time(self) -> float | None:
        """
        Return the remaining time of white if blitz mode is activated.
        """
        if self.__configuration.get("blitz"):
            return self.__blitztimer.get_black_remaining_time()
        return None

    def get_config(self) -> Config:
        """
        Get the configuration of the game.
        """
        return self.__configuration

    def get_board(self) -> Board:
        """
        Get the board of the current game.
        """
        return self.__board

    def give_up(self) -> None:
        """
        Give up action.
        If the current player is white, black will win and
        vice versa.
        """
        if self.get_current_player() == PLAYER_O:
            self.set_game_over(GameOverState.BLACK_WON)
        else:
            self.set_game_over(GameOverState.WHITE_WON)

    def swap(self) -> None:
        """
        Swap action. Remove the first move of the first player
        and play the same move but with the second player.
        """
        last_done_move = self.__history.get_done_moves()[0]
        self.__board.remove_move(
            (last_done_move["letter"], last_done_move["number"]),
            last_done_move["player"]
        )
        self.play_move((last_done_move["letter"], last_done_move["number"]))

    def set_winning_path(self) -> None:
        """
        Set the winning path to the connecting path only if there is a
        winner.
        """
        match self.__game_over_state:
            case GameOverState.NO_WINNER:
                self.__winning_path = []
            case GameOverState.WHITE_WON:
                self.__winning_path = self.__board.winning_path(PLAYER_O)
            case GameOverState.BLACK_WON:
                self.__winning_path = self.__board.winning_path(PLAYER_X)

    def get_winning_path(self) -> list[tuple[str, int]]:
        """
        Get the winning connecting path.

        Returns
        -------
        list[tuple[str, int]]
            the winning connecting path
        """
        return self.__winning_path

    def get_current_ai_players(self) -> list[int]:
        """
        Get the list of ai players.

        Returns
        -------
        list[int]
            list of all ai players
        """
        if self.__ai_module is not None:
            return self.__ai_module.get_ai_players()
        return []

    def ai_play_move(self, player: int) -> None:
        """
        Play a move computed by the ai player.

        Parameters
        ----------
        player: int
            id of the player. 0 for white and 1 for black.
        """
        if self.__ai_module is not None:
            ai_board = self.__board.duplicate_board()
            self.play_move(self.__ai_module.ai_get_move(player, ai_board))

    def get_ai(self) -> AIModule:
        """
        Return the ai mode structure.
        """
        return self.__ai_module

    def timer_set_gui_refresh_methods(self, methods) -> None:
        """
        Set the methods used by the timer to refresh the display.

        Parameters
        ----------
        methods:
            - methods[0] is supposed to be the timer display refresh
            method
            - methods[1] is supposed to be all displays' refresh
            methods
        """
        self.__blitztimer.set_gui_refresh_methods(methods)

    def contest(self) -> str:
        """
        Plays the best move for the current player according
        to the selected AI.

        Returns
        -------
        str
            message indicating which move has been found and played
        """
        player = self.get_current_player()
        move = self.get_ai().ai_get_move(player, self.get_board())
        player_str = 'O' if player == 0 else 'X'
        move_str = str(move[0]) + str(move[1])
        msg = "The best move for player " + player_str
        self.play_move(move)
        return msg + " is '" + move_str + "'."
