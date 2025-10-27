import os
from signal import SIG_BLOCK, SIG_UNBLOCK, SIGUSR1, pthread_sigmask
from hex.tools.game_over_state import GameOverState
from hex.tools.game_state import GameState
from hex.tools.file import FileModule
import gettext
import time

DELAY_AFTER_AI_PLAYS = 0


class Cli():
    """
    Class that represents and handles the display of the game in command line mode.

    Attributes
    ----------
    game_state: Game_State
        The Game_State instace used to tie the display to the board.
    file_module: File_module
        The File_module instace used to tie the display to the files handling.

    Methods
    -------
    start_game(self) -> None:
        Starts the game associated to the game_state attribute.
        Made to be called by the main program after the Cli instance was created.
    """

    def __init__(
            self,
            game_state: GameState,
            file_module: FileModule) -> None:
        """
        Cli's constructor.

        Parameters
        ----------
        game_state: Game_State
            The Game_State instace used to tie the display to the board.
        file_module: File_module
            The File_module instace used to tie the display to the files handling.
        """
        self.__game_state = game_state
        self.__file_module = file_module
        """
        The part below is used for the translation of the game using gettext.
        The variable lang will get the current language then it will give it to gettext.
        The it will search the dir where the translation is to use it with "_".
        Everytime there is a "_" before a string, it will be translated.
        """
        global lang
        lang = game_state.get_config().get("language")
        language_translations = gettext.translation(
            "base", localedir=os.path.dirname(__file__) + "/locales",
            languages=[lang])
        language_translations.install()

        global _
        _ = language_translations.gettext

    def __confirm(self, action: str) -> bool:
        """
        Asks the user for a specific action's confirmation.
        Made to be used for 'critical' actions.

        Parameters
        ----------
        action: str
            The action to ask confirmation for.

        Returns
        -------
        boolean
            Wether the user has confirmed the action or not (canceled).
        """
        try:
            ipt = input(_("confirm action ") + action +
                        _(", yes or no ? ('y/n'):\n"))
        except (EOFError, KeyboardInterrupt) as e:
            if self.__game_state.get_config().get("blitz"):
                self.__game_state.pause_timer()
            print()
            exit(0)
        if ipt == "y":
            return True
        elif ipt == "n":
            return False
        else:
            print(_("" "Invalid input") +
                  f' "{ipt}" ' + _("; respond by typing 'y' or 'n'."))
            return self.__confirm(action)

    def __display_help(self) -> None:
        """
        Function that simply displays the list of input commands available.
        """
        print(_("""Hex game input syntax help:
    [letter][number]: Input next move to play (example: 'a5').
    'u/undo':         Undo the last move.
    'r/redo':         Redo the last undone move.
    'h/help':         Display program help.
    'd/display':      Display current game board.
    'restart':        Restart current game (with the same configuration).
    'l/load' [FILE]:  Load game from specified file.
    's/save' [FILE]:  Save current game in specified file.
    'g/give up'       Give up current game (current player loses).
    'q/quit':         Exit program."""))

    def start_game(self) -> None:
        """
        Starts the game associated to the game_state attribute.
        Made to be called by the main program after the Cli instance was created.
        """
        print(_("------ HEX GAME ------"))
        self.__game_state.start_timer()
        return self.__game_loop()

    def __restart_game(self) -> None:
        """
        Restarts the current game after resetting the game's data.
        """
        self.__game_state.reset_game_state()
        return self.start_game()

    def __display_ai_info(self) -> None:
        """
        Displays the values of the current AIs evaluations (heuristic for each turn etc.).
        """
        if self.__game_state.get_current_game_round() == 1 \
                and self.__game_state.get_current_player() == 0:
            heur_o = self.__game_state.get_ai().get_h_O()
            heur_x = self.__game_state.get_ai().get_h_X()
            algo_o = self.__game_state.get_ai().get_a_O()
            algo_x = self.__game_state.get_ai().get_a_X()
            match self.__game_state.get_config().get("ai"):
                case "O":
                    print(_("Player O heuristic = ") + str(heur_o)
                          + ", algo = " + str(algo_o))
                case "X":
                    print(_("Player X heuristic = ") + str(heur_x)
                          + ", algo = " + str(algo_x))
                case "A":
                    print(_("Player O heuristic = ") + str(heur_o)
                          + ", algo = " + str(algo_o))
                    print(_("Player X heuristic = ") + str(heur_x)
                          + ", algo = " + str(algo_x))
            print(
                "Maximum depth is ",
                self.__game_state.get_ai().get_ai_depth())

    def __game_loop(self) -> None:
        """
        Serves as the main game loop.
        Tests if the game is over, displays the current board state
        and asks for the user input.
        """
        self.__display_game()
        if self.__game_state.get_config().get("ai") != "None":
            self.__display_ai_info()
        if self.__game_state.get_current_player() in self.__game_state.get_current_ai_players(
        ) and not self.__game_state.is_game_over():
            self.__game_state.ai_play_move(
                self.__game_state.get_current_player())
            time.sleep(DELAY_AFTER_AI_PLAYS)
            self.__game_loop()
        return self.__handle_user_input()

    def __display_game(self) -> None:
        """
        Main display for the Cli.
        Displays the current board's state, the done/undone moves history and remaining times for each player.
        """
        last_done_moves, last_undone_moves = self.__game_state.get_last_moves()
        str_split = self.__game_state.board_to_string().split("\n")

        str_done = _("Last done moves:")
        str_undone = _("Last undone moves:")
        str_O_time = _("O remaining time:")
        str_X_time = _("X remaining time:")

        str_split[0] += f"{' ' * (self.__game_state.get_game_dim() + 4)}{str_done}     {str_undone}     {str_O_time}     {str_X_time}"
        str_split[1] += f"{' ' * (self.__game_state.get_game_dim() + 3)}{'-' * len(str_done)}     {'-' * len(str_undone)}     {'-' * len(str_O_time)}     {'-' * len(str_X_time)}"
        for i in range(self.__game_state.get_game_dim()):
            str_split[2 + i] += " " * \
                (self.__game_state.get_game_dim() - 1 - i)
            if len(last_done_moves) > i:
                str_split[2 +
                          i] += f"| {last_done_moves[i]['round']}. {'0' if last_done_moves[i]['player'] == 0 else 'X'} {last_done_moves[i]['letter']}{last_done_moves[i]['number']} |{' ' * (len(str_done) - 6)}"
            else:
                str_split[2 + i] += " " * (len(str_done) + 5)
            if len(last_undone_moves) > i:
                str_split[2 +
                          i] += f"| {last_undone_moves[i]['round']}. {'0' if last_undone_moves[i]['player'] == 0 else 'X'} {last_undone_moves[i]['letter']}{last_undone_moves[i]['number']} |{' ' * (len(str_undone) - 6)}"
            else:
                str_split[2 + i] += " " * (len(str_undone) + 5)
        O_time = self.__game_state.get_white_time()
        X_time = self.__game_state.get_black_time()
        str_split[2] += (f"{int(O_time//60):02d}:{int(O_time%60):02d}" if O_time is not None else "∞    ") + \
            " " * len(str_O_time) + \
            (f"{int(X_time//60):02d}:{int(X_time%60):02d}" if X_time is not None else "∞")
        print("\n".join(str_split))

    def __load_game(self, path: str) -> None:
        """
        Used to load a current game from a specified filename.

        Parameters
        ----------
        path: str
            String reprensenting the name of the file from which to
            load the game from.
        """
        try:
            self.__file_module.load_hexgame(path=path)
            return self.start_game()
        except ValueError:
            print(_("File does not correspond to the hexgame format."))
            return self.__handle_user_input()

    def __save_game(self, path: str) -> None:
        """
        Used to save the current game state in a specified filename.

        Parameters
        ----------
        path: str
            String reprensenting the name of the file in which to save
            the current game state into.
        """
        print(path)
        self.__file_module.save_as_hexgame(path=path)
        print(_("File saved at [") + path + ".hexgame].")

    def __handle_move(self, move: tuple[str, int]) -> None:
        """
        Tries to play a given move if possible.
        Shows if the action has succeeded or not.

        Parameters
        ----------
        move: tuple[str, int]
            The letter representing the column of the move and
            the number representing the line of the move.
        """
        move_player = self.__game_state.get_current_player()
        letter, number = move
        play_move_return = self.__game_state.play_move(move)
        if play_move_return == 0:
            if move_player == 0:
                print(
                    _("Player O played move (") +
                    letter +
                    "," +
                    str(number) +
                    ").")
            else:
                print(
                    _("Player X played move (") +
                    letter +
                    "," +
                    str(number) +
                    ").")
            return self.__game_loop()
        elif play_move_return == 1:
            print(_("Space (") + letter + ", "
                  + str(number) + _(") is already occupied."))
        else:
            print(_("Move (") + letter + ", "
                  + str(number) + _(") is out of bounds."))
        return self.__handle_user_input()

    def __undo(self) -> None:
        """
        Tries to undo the last done move if possible.
        Shows if the action has not succeeded.
        """
        code = self.__game_state.undo()
        if code == 0:
            return self.__game_loop()
        elif code == 1:
            print(_("Undo not possible; done moves history is currently empty."))
        else:
            print(
                _("Undo not possible; an unexpected error occured (code") + code + ").")

    def __redo(self) -> None:
        """
        Tries to redo the last undone move if possible.
        Shows if the action has not succeeded.
        """
        code = self.__game_state.redo()
        if code == 0:
            return self.__game_loop()
        elif code == 1:
            print(_("Redo not possible; undone moves history is currently empty."))
        else:
            print(
                _("Redo not possible; an unexpected error occured (code ") + code + ").")

    def __check_user_input_undo(self, user_input: str) -> bool:
        """
        Given an input, checks if it corresponds to the "undo" command.
        Returns True or False depending on this.

        Parameters
        ----------
        user_input: str
            The user input given to this method.

        Returns
        -------
        boolean
            Wether the user input corresponds to the command being checked or not.
        """
        return user_input.lower() == "u" or user_input.lower() == "undo"

    def __check_user_input_redo(self, user_input: str) -> bool:
        """
        Given an input, checks if it corresponds to the "redo" command.
        Returns True or False depending on this.

        Parameters
        ----------
        user_input: str
            The user input given to this method.

        Returns
        -------
        boolean
            Wether the user input corresponds to the command being checked or not.
        """
        return user_input.lower() == "r" or user_input.lower() == "redo"

    def __check_user_input_help(self, user_input: str) -> bool:
        """
        Given an input, checks if it corresponds to the "help" command.
        Returns True or False depending on this.

        Parameters
        ----------
        user_input: str
            The user input given to this method.

        Returns
        -------
        boolean
            Wether the user input corresponds to the command being checked or not.
        """
        return user_input.lower() == "h" or user_input.lower() == "help"

    def __check_user_input_display(self, user_input: str) -> bool:
        """
        Given an input, checks if it corresponds to the "display" command.
        Returns True or False depending on this.

        Parameters
        ----------
        user_input: str
            The user input given to this method.

        Returns
        -------
        boolean
            Wether the user input corresponds to the command being checked or not.
        """
        return user_input.lower() == "d" or user_input.lower() == "display"

    def __check_user_input_restart(self, user_input: str) -> bool:
        """
        Given an input, checks if it corresponds to the "restart" command.
        Returns True or False depending on this.

        Parameters
        ----------
        user_input: str
            The user input given to this method.

        Returns
        -------
        boolean
            Wether the user input corresponds to the command being checked or not.
        """
        return user_input.lower() == "restart"

    def __check_user_input_quit(self, user_input: str) -> bool:
        """
        Given an input, checks if it corresponds to the "quit" command.
        Returns True or False depending on this.

        Parameters
        ----------
        user_input: str
            The user input given to this method.

        Returns
        -------
        boolean
            Wether the user input corresponds to the command being checked or not.
        """
        return user_input.lower() == "q" or user_input.lower() == "quit"

    def __check_user_input_give_up(self, user_input: str) -> bool:
        """
        Given an input, checks if it corresponds to the "give up" command.
        Returns True or False depending on this.

        Parameters
        ----------
        user_input: str
            The user input given to this method.

        Returns
        -------
        boolean
            Wether the user input corresponds to the command being checked or not.
        """
        return user_input.lower() == "g" or user_input.lower() == "give up"

    def __check_user_input_save(self, user_input: str) -> str:
        """
        Given an input, checks if it corresponds to a save command.
        Returns the save path.

        Parameters
        ----------
        user_input: str
            The user input given to this method.

        Returns
        -------
        str
            Return the save path if the command is valid, otherwise "" as an invalid value.
        """
        if len(user_input.split(" ")) == 2:
            ipt_split = user_input.split(" ")
            if ipt_split[0].lower() == "s" or ipt_split[0].lower() == "save":
                return ipt_split[1]
        return ""

    def __check_user_input_load(self, user_input: str) -> str:
        """
        Given an input, checks if it corresponds to a load command.
        Returns the load path.

        Parameters
        ----------
        user_input: str
            The user input given to this method.

        Returns
        -------
        str
            Return the load path if the command is valid, otherwise "" as an invalid value.
        """
        if len(user_input.split(" ")) == 2:
            ipt_split = user_input.split(" ")
            if ipt_split[0].lower() == "l" or ipt_split[0].lower() == "load":
                return ipt_split[1]
        return ""

    def __check_user_input_move(self, user_input: str) -> tuple[str, int]:
        """
        Given an input, checks if it corresponds to a move to play.
        Returns the move (letter, number) values.

        Parameters
        ----------
        user_input: str
            The user input given to this method.

        Returns
        -------
        tuple[str, int]
            Return the move (letter, number) if the command is valid, otherwise ("", -1) as an invalid value.
        """
        letter, number = None, None
        if len(user_input.split(" ")) == 2:
            ipt_split = user_input.split(" ")
            if ipt_split[0].lower() >= "a" and ipt_split[0].lower() \
                    <= "z" and ipt_split[1].isdigit():
                letter, number = ipt_split[0], ipt_split[1]
            elif ipt_split[1].lower() >= "a" and ipt_split[1].lower() \
                    <= "z" and ipt_split[0].isdigit():
                letter, number = ipt_split[1], ipt_split[0]
        elif len(user_input) >= 2:
            if user_input[0].lower() >= "a" and user_input[0].lower() \
                    <= "z" and user_input[1:].isdigit():
                letter, number = user_input[0].lower(), user_input[1:]
            elif user_input[-1].lower() >= "a" and user_input[-1].lower() \
                    <= "z" and user_input[:-1].isdigit():
                letter, number = user_input[-1].lower(), user_input[:-1]
        if letter is not None and number is not None:
            return (letter, int(number))
        else:
            return ("", -1)

    def __parse_user_input(self, user_input: str) -> None:
        """
        Method that uses other auxiliary methods to parse the user input.
        Calls the adequate method depending the recognized valid/invalid command.

        Parameters
        ----------
        user_input: str
            The user input given to this method.
        """
        if self.__check_user_input_undo(
                user_input) and not self.__game_state.is_game_over():
            self.__undo()
        elif self.__check_user_input_redo(user_input) and not self.__game_state.is_game_over():
            self.__redo()
        elif self.__check_user_input_help(user_input):
            self.__display_help()
        elif self.__check_user_input_display(user_input) and not self.__game_state.is_game_over():
            self.__display_game()
        elif self.__check_user_input_restart(user_input):
            if self.__confirm("restart"):
                return self.__restart_game()
        elif self.__check_user_input_quit(user_input):
            if self.__confirm("quit"):
                exit(0)
        elif self.__check_user_input_give_up(user_input) and not self.__game_state.is_game_over():
            if self.__confirm("give up"):
                self.__game_state.give_up()
                return self.__handle_user_input()
        elif (ret := self.__check_user_input_save(user_input)) != "":
            self.__save_game(ret)
        elif (ret := self.__check_user_input_load(user_input)) != "":
            return self.__load_game(ret)
        elif (retpos := self.__check_user_input_move(user_input)) != ("", -1) and not self.__game_state.is_game_over():
            return self.__handle_move(retpos)
        else:
            print(_("Invalid input (input 'h' for help)."))
        return self.__handle_user_input()

    def __handle_user_input(self) -> None:
        """
        Method that asks and waits for the user input before calling another to parse it.
        Terminates the program in case of a EOFError/KeyboardInterrupt.
        """
        try:
            if self.__game_state.is_game_over():
                if self.__game_state.get_winner() == GameOverState.WHITE_WON:
                    print(_("Game over ! Winner : O"))
                else:
                    print(_("Game over ! Winner : X"))
                winning_path = self.__game_state.get_winning_path()
                if winning_path != []:
                    print(_("Winning path: "))
                    print([move[0] + str(move[1]) for move in winning_path])
                user_input = input(
                    _("Input next action (actions available from game over: load/save/restart/quit) ('h' for help):\n"))
            else:
                if self.__game_state.get_current_player() == 0:
                    print(_("Round ") +
                          str(self.__game_state.get_current_game_round()) +
                          _(", current player : O."))
                else:
                    print(_("Round ") +
                          str(self.__game_state.get_current_game_round()) +
                          _(", current player : X."))
                pthread_sigmask(SIG_UNBLOCK, [SIGUSR1])
                if self.__game_state.get_config().get("swap") and len(
                        self.__game_state.get_done_moves()) == 1:
                    print(
                        _("Swap option is enabled. Player X can play over player O's move."))
                    if self.__confirm("swap"):
                        self.__game_state.swap()
                        return self.__game_loop()
                # input needs to be interrupted by SIGUSR1 if a timer runs out
                user_input = input(_("Input next action ('h' for help):\n"))
                pthread_sigmask(SIG_BLOCK, [SIGUSR1])
        except (EOFError, KeyboardInterrupt) as e:
            if self.__game_state.get_config().get("blitz"):
                self.__game_state.pause_timer()
            print()
            exit(0)
        except InterruptedError:
            pthread_sigmask(SIG_BLOCK, [SIGUSR1])
            if self.__game_state.get_winner() == GameOverState.WHITE_WON:
                print(_("Player X's time ran out !"))
            else:
                print(_("Player O's time ran out !"))
            return self.__handle_user_input()
        return self.__parse_user_input(user_input)
