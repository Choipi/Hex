from .game_state import GameState
from .board import Board
from .history import History

PLAYER_X_VALUE = 1
PLAYER_O_VALUE = 0

FILE_FORMAT_SECTION_SEPARATOR = "\n#\n"
FILE_FORMAT_NUMBER_OF_SECTION = 6

FILE_FORMAT_ONE_VALUE_SEPARATOR = ": "
FILE_FORMAT_COMMENT_SECTION_INDEX = 0
FILE_FORMAT_BOARD_SECTION_INDEX = 1
FILE_FORMAT_CURRENT_PLAYER_SECTION_INDEX = 2
FILE_FORMAT_CURRENT_GAME_ROUND_SECTION_INDEX = 3
FILE_FORMAT_HISTORY_SECTION_INDEX = 4
FILE_FORMAT_BOARD_DIM_SECTION_INDEX = 5

CHECK_FORMAT_CHECKED_VALUE = 3
CHECK_FORMAT_NON_CHECKED_EMPTY_SPACE = 2
CHECK_FORMAT_NON_CHECKED_X = 1
CHECK_FORMAT_NON_CHECKED_O = 0

HISTORY_MOVES_SEPARATOR = "\n"
HISTORY_MOVES_IN_BETWEEN_MOVE_SEPARATOR = "|"
HISTORY_MOVE_VALUE_SEPARATOR = ". "
HISTORY_MOVE_NUMBER_OF_FIELDS = 3
HISTORY_MOVE_ROUND_INDEX = 0
HISTORY_MOVE_LETTER_INDEX = 1
HISTORY_MOVE_MOVE_O_INDEX = 0
HISTORY_MOVE_MOVE_X_INDEX = 1
HISTORY_MOVE_NUMBER_INDEX = 2
HISTORY_MOVE_PLAYER_INDEX = 0


class FileModule:
    """A class that handle all the operation related to extern files, load and save

    Attributes
    ----------

    __game_state: Game_State
        Current game_state structure describing the game
    """

    def __init__(self, game_state: GameState):
        """
        Parameters
        ----------
        game_state: Game_State
            Current game_state structure
        """
        self.__game_state = game_state

    def __check_extension(self, path: str) -> bool:
        """ Check if the given path is an hexgame file

        Parameters
        ----------
        path: string
            path to the file to checked, should be relative starting point is hex/

        Returns
        -------
        bool
            True if hexgame_file else False
        """
        splited_path = path.split(".")
        if len(splited_path) == 0:
            False
        return splited_path[-1].__eq__("hexgame")

    def __check_board_values(self, board_string: str, board_dim: str):
        """ Check if all the values in the string describing the board
        are legals. And the values distribution respects game's rules.
                Legal values are :
                        "X", "O", "."
                Legal Values distribution :
                        0 <= number_of_X <= number_of_O <= number_of_X +1 <= board_dim * board_dim / 2 + 1

        Parameters
        ----------
        board_string: str
            String describing the board, obtained by load method

        board_dim: str
            String of an int describing the board dimension

        Returns
        -------
        bool
            True if all values are legals and the values distribution is legal aswell else False
        """
        b_dim = int(board_dim)
        X_count = 0
        O_count = 0
        lines_array = board_string.splitlines(False)
        if len(lines_array) != b_dim:
            raise ValueError("Wrong number of lines")
        for line in lines_array:
            if len(line) != b_dim:
                raise ValueError("Wrong number of tile a line")
            for tile in line:
                match tile:
                    case "X":
                        X_count += 1
                    case "O":
                        O_count += 1
                    case ".":
                        pass
                    case _:
                        raise ValueError("A tile has an unknown value")
        if X_count > O_count or O_count - X_count > 1:
            raise ValueError("Illegal distribution of player tiles")

    def __check_history_values(
            self,
            history_string: str,
            board_dim: str) -> None:
        """ Check if all the values in the string describing the
        history are legals. And the values coordinates respects game's rules.
                Legal values are :
                        "X", "O", "."
                Legal Values coordinates :
                        a<= letter <= a+ board_dim && 1<= number <= board_dim

        Parameters
        ----------
        history_string: str
            String describing the history, obtained by load method

        board_dim: str
            String of an int describing the board dimension

        Returns
        -------
        bool
            True if all values are legals else False
        """
        splitted_moves = history_string.split(HISTORY_MOVES_SEPARATOR)
        round_counter = 0
        b_dim = int(board_dim)
        if len(splitted_moves) > int(b_dim * b_dim / 2) + 1:
            raise ValueError("Too many moves in history")
        for move in splitted_moves:
            if len(move) == 0:
                return
            move_splited = move.split(HISTORY_MOVE_VALUE_SEPARATOR)
            both_player_moves = move_splited[1].split("|")
            player_O_move = both_player_moves[PLAYER_O_VALUE]
            player_X_move = both_player_moves[PLAYER_X_VALUE]

            if len(player_O_move) != HISTORY_MOVE_NUMBER_OF_FIELDS and len(
                    player_O_move) != HISTORY_MOVE_NUMBER_OF_FIELDS + 1:
                raise ValueError("a O move is missing a field")
            if len(player_X_move) != HISTORY_MOVE_NUMBER_OF_FIELDS and len(
                    player_X_move) != 0 and len(player_X_move) != HISTORY_MOVE_NUMBER_OF_FIELDS + 1:
                raise ValueError("a X move is missing a field")

            round = move_splited[HISTORY_MOVE_ROUND_INDEX]
            if not round.isdigit():
                raise ValueError("Wrong round value in ", move)

            round_num = int(round)
            if round_num < round_counter:
                raise ValueError("Wrong round value not incremental")
            if round_num > round_counter + 1:
                raise ValueError("Wrong round value not incremental")
            round_counter = round_num

            if player_O_move[HISTORY_MOVE_PLAYER_INDEX] != "O":
                raise ValueError("Wrong player value in ", move)
            if len(player_X_move) != 0:
                if player_X_move[HISTORY_MOVE_PLAYER_INDEX] != "X":
                    raise ValueError("Wrong player value in ", move)

            letterO = player_O_move[HISTORY_MOVE_LETTER_INDEX]
            if not letterO.isalpha():
                raise ValueError("Wrong round value in ", move)
            if len(letterO) != 1 or letterO < "a" or ord(
                    letterO) - ord("a") > b_dim:
                ValueError("this letter is unknown ", letterO)

            if len(player_X_move) != 0:
                letterX = player_X_move[HISTORY_MOVE_LETTER_INDEX]
                if not letterX.isalpha():
                    raise ValueError("Wrong round value in ", move)
                if len(letterX) != 1 or letterX < "a" or ord(
                        letterX) - ord("a") > b_dim:
                    ValueError("this letter is unknown ", letterX)

            numberO = player_O_move[2:]
            if not numberO.isdigit():
                raise ValueError("Wrong number value in ", move)
            if len(numberO) > 2 or int(numberO) > b_dim:
                ValueError("this number is unknown ", numberO)

            if len(player_X_move) != 0:
                numberX = player_X_move[2:]
                if not numberX.isdigit():
                    raise ValueError("Wrong number value in ", move)
                if len(numberX) > 2 or int(numberX) > b_dim:
                    ValueError("this number is unknown ", numberX)

    def __get_2d_array_with_board_values(
            self, board_string: str, board_dim: str) -> list[list[int]]:
        """ From the string extracted from load game, create a 2d array containing the board values
                Legal values are :
                        "CHECK_FORMAT_NON_CHECKED_O", "CHECK_FORMAT_NON_CHECKED_X", "CHECK_FORMAT_NON_CHECKED_EMPTY_SPACE"


        Parameters
        ----------
        board_string: str
            String describing the board, obtained by load method

        board_dim: str
            String of an int describing the board dimension

        Returns
        -------
        List[List[int]]
            A 2d array containing the board values:
                Empty space: CHECK_FORMAT_NON_CHECKED_EMPTY_SPACE
                blacks : CHECK_FORMAT_NON_CHECKED_X
                whites : CHECK_FORMAT_NON_CHECKED_O
        """

        b_dim = int(board_dim)
        test_board = [[CHECK_FORMAT_NON_CHECKED_EMPTY_SPACE for x in range(
            b_dim)] for y in range(b_dim)]

        lines_array = board_string.splitlines(False)

        for line_number in range(b_dim):
            line_str = lines_array[line_number]

            for column in range(b_dim):
                bit_value = line_str[column]
                match bit_value:
                    case 'O':
                        test_board[line_number][column] = CHECK_FORMAT_NON_CHECKED_O
                    case 'X':
                        test_board[line_number][column] = CHECK_FORMAT_NON_CHECKED_X
        return test_board

    def __get_array_with_history_values(self, history_string: str) -> list:
        """ From history string extracted from load game, creates an array each cell contains a dictionary with a move from the history:
                keys:   letter
                        number
                        player's color

        Parameters
        ----------
        history_string: str
            String describing the history, obtained by load method

        Returns
        ----------
        List
            each cell represents a move from the history, each cell contains a dictionary with the following keys: letter, number, player

        """
        splitted_moves = history_string.split(HISTORY_MOVES_SEPARATOR)
        moves_list: list[dict[str, int | str]] = []
        # empty cell in the end due to separator location
        for move in splitted_moves:
            if len(move) == 0:
                return moves_list
            line_splited = move.split(HISTORY_MOVE_VALUE_SEPARATOR)
            both_player_moves = line_splited[1].split('|')
            player_O_move = both_player_moves[0]
            player_X_move = both_player_moves[1]

            letterO = player_O_move[HISTORY_MOVE_LETTER_INDEX]
            numberO = player_O_move[HISTORY_MOVE_NUMBER_INDEX]
            if len(
                    player_O_move) > 3 and player_O_move[HISTORY_MOVE_NUMBER_INDEX + 1].isdigit():
                numberO = numberO + \
                    player_O_move[HISTORY_MOVE_NUMBER_INDEX + 1]
            player = self._player_to_int(
                player_O_move[HISTORY_MOVE_PLAYER_INDEX])
            moves_list.append(
                {"player": player, "letter": letterO, "number": numberO})

            if len(player_X_move) != 0:
                letterX = player_X_move[HISTORY_MOVE_LETTER_INDEX]
                numberX = player_X_move[HISTORY_MOVE_NUMBER_INDEX]
                if len(
                        player_X_move) > 3 and player_X_move[HISTORY_MOVE_NUMBER_INDEX + 1].isdigit():
                    numberX = numberX + \
                        player_X_move[HISTORY_MOVE_NUMBER_INDEX + 1]
                player = self._player_to_int(
                    player_X_move[HISTORY_MOVE_PLAYER_INDEX])
                moves_list.append(
                    {"player": player, "letter": letterX, "number": numberX})
        return moves_list

    def _board_is_empty(self, board_string: str) -> bool:
        lines_array = board_string.splitlines(False)
        for line in lines_array:
            for tile in line:
                match tile:
                    case "X":
                        return False
                    case "O":
                        return False
                    case ".":
                        pass
                    case _:
                        pass
        return True

    def __are_history_and_board_matching(
            self,
            board_string: str,
            history_string: str,
            board_dim_str: str) -> None:
        """ Based on the string of the board and the history from a file check if those two are matching, if something is wrong raises a ValueError

        Parameters
        ----------
        history_string: str
            String describing the history, obtained by load method

        board_string: str
            String describing the board, obtained by load method

        board_dim: str
            String of an int describing the board dimension

        """

        history_to_test = self.__get_array_with_history_values(
            history_string)
        board_to_test = self.__get_2d_array_with_board_values(
            board_string, board_dim_str)
        board_dim = int(board_dim_str)

        for move in history_to_test:
            line = int(move["number"]) - 1
            column = ord((move["letter"])) - ord("a")
            expected_value = int(move["player"])

            if board_to_test[line][column] == expected_value:
                board_to_test[line][column] = CHECK_FORMAT_CHECKED_VALUE
            else:
                raise ValueError(
                    "Board and history are not matching from history matching")
        for line in range(board_dim):
            for column in range(board_dim):
                if board_to_test[line][column] == CHECK_FORMAT_NON_CHECKED_O or board_to_test[line][column] == CHECK_FORMAT_NON_CHECKED_X:
                    raise ValueError(
                        "Board and history are not matching from history matching")

    def __check_format(
            self,
            board_string: str,
            current_player_string: str,
            current_game_round_string: str,
            history_string: str,
            board_size: str) -> None:
        """ Checks if the strings given by the load method repsects games's rules and file format, raises a ValueError if anything is wrong

        Parameters
        ----------
        history_string: str
            String describing the history, obtained by load method

        board_string: str
            String describing the board, obtained by load method

        board_dim: str
            String of an int describing the board dimension

        current_game_round_string: str

        current_player_string: str


        """

        if board_string.__eq__("") or current_player_string.__eq__(
                "") or current_game_round_string.__eq__("") or board_size.__eq__(""):
            raise ValueError("One of the file section is empty")
        if history_string.__eq__(
                "") and not self._board_is_empty(board_string):
            raise ValueError("One of the file section is empty")
        self.__check_board_values(board_string, board_size)
        self.__check_history_values(history_string, board_size)
        self.__are_history_and_board_matching(
            board_string, history_string, board_size)

    def save_as_hexgame(self, path: str) -> None:
        """If given path is accurate (path should start from hex/), create a new file or truncate existing one and writes content of the current game state following the file format described in requirements sheet.

        Parameters
        ----------

        path: str
            path should start from hex/

        """
        final_path = path.__add__((".hexgame"))
        with open(final_path, 'w+') as file:

            for section_number in range(0, FILE_FORMAT_NUMBER_OF_SECTION):
                if section_number == FILE_FORMAT_COMMENT_SECTION_INDEX:
                    file.write(self.__game_state.get_game_comment())

                elif section_number == FILE_FORMAT_BOARD_SECTION_INDEX:
                    file.write(self._write_board_to_string())

                elif section_number == FILE_FORMAT_CURRENT_PLAYER_SECTION_INDEX:
                    file.write(self._write_current_player_to_string())

                elif section_number == FILE_FORMAT_CURRENT_GAME_ROUND_SECTION_INDEX:
                    file.write(self._write_current_game_round_to_string())

                elif section_number == FILE_FORMAT_HISTORY_SECTION_INDEX:
                    file.write(self._get_history_string_to_file_format())

                elif section_number == FILE_FORMAT_BOARD_DIM_SECTION_INDEX:
                    file.write(self._write_current_game_dim_to_string())
                else:
                    raise IndexError("cant save a section index error")
                file.write(FILE_FORMAT_SECTION_SEPARATOR)
            file.close()

    def _write_current_game_dim_to_string(self) -> str:
        result = "Game dimension is : " + str(self.__game_state.get_game_dim())
        return result

    def _write_current_game_round_to_string(self) -> str:
        result = "Current game round : " + \
            str(self.__game_state.get_current_game_round())
        return result

    def _write_current_player_to_string(self) -> str:
        result = "Next player to play : " + \
            str(self.__game_state.get_current_player())
        return result

    def _write_board_to_string(self) -> str:
        """Returns a string separated by the separator associated among the global variables of the file.
                Whites represented by "O"
                Blacks represented by "X"
                Empty space represented by "."
        """
        board_str = ""
        board_dim = self.__game_state.get_game_dim()
        for i in range(board_dim):
            for j in range(board_dim):
                bit_value = self.__game_state.get_value_of_space(
                    i * board_dim + j)
                match bit_value:
                    case 1:
                        board_str += "O"
                    case 2:
                        board_str += "X"
                    case 0:
                        board_str += "."
            board_str += "\n"
        return board_str

    def load_hexgame(self, path: str):
        """If given path is accurate (path should start from hex/, and contains file extension), opens the file, and load file information in current game_state

        Parameters
        ----------

        path: str
            path should start from hex/, and contains file extension
        """
        if (not self.__check_extension(path)):
            raise ValueError("Not an hexgame File")
        with open(path, 'r') as file:
            content = file.read()

            self.__game_state.reset_game_state()

            splited_content = content.split(sep=FILE_FORMAT_SECTION_SEPARATOR)

            # comment
            comment_string = splited_content[FILE_FORMAT_COMMENT_SECTION_INDEX]

            # board_string
            board_string = splited_content[FILE_FORMAT_BOARD_SECTION_INDEX]
            # current_player
            current_player_string = splited_content[FILE_FORMAT_CURRENT_PLAYER_SECTION_INDEX].split(": ")[
                1]
            # current_player
            current_game_round_string = splited_content[FILE_FORMAT_CURRENT_GAME_ROUND_SECTION_INDEX].split(": ")[
                1]
            # history
            history_string = splited_content[FILE_FORMAT_HISTORY_SECTION_INDEX]
            # history
            board_size = splited_content[FILE_FORMAT_BOARD_DIM_SECTION_INDEX].split(": ")[
                1]

            try:
                self.__check_format(
                    board_string,
                    current_player_string,
                    current_game_round_string,
                    history_string,
                    board_size)
            except ValueError as error_msg:
                file.close()
                raise ValueError(error_msg)

            self.__game_state.add_game_comment(comment_string)
            self.__game_state.set_board(
                self._use_string_to_create_board(board_string, board_size))
            self.__game_state.set_current_player(int(current_player_string))
            self.__game_state.set_current_game_round(
                int(current_game_round_string))
            self.__game_state.set_history(
                self._use_string_to_create_history(history_string))
            # set the correct state if the loaded game is already over
            self.__game_state.set_game_over(
                self.__game_state.get_board().has_connection())
            if self.__game_state.is_game_over():
                self.__game_state.set_winning_path()

            file.close()

    def _use_string_to_create_board(
            self,
            board_string: str,
            board_dim: str) -> Board:
        result_board = Board(int(board_dim))

        lines_array = board_string.splitlines(False)
        game_size = result_board.get_dim()

        for line_number in range(game_size):
            line_str = lines_array[line_number]

            for column in range(game_size):
                bit_value = line_str[column]
                match bit_value:
                    case 'O':
                        result_board.add_move(
                            position=game_size * line_number + column, player=0)
                    case 'X':
                        result_board.add_move(
                            position=game_size * line_number + column, player=1)

        return result_board

    def _player_to_string(self, player: int) -> str:
        if player == PLAYER_O_VALUE:
            return "O"
        elif player == PLAYER_X_VALUE:
            return "X"
        else:
            return "NaN"

    def _player_to_int(self, player: str) -> int:
        if player == "O":
            return PLAYER_O_VALUE
        elif player == "X":
            return PLAYER_X_VALUE
        else:
            return -1

    def _get_history_string_to_file_format(self) -> str:
        history_string = ""
        new_round = True
        moves = self.__game_state.get_done_moves()
        moves_to_write = moves.copy()
        moves_to_write.reverse()
        for move in moves_to_write:
            if new_round:
                history_string += str(move["round"])
                history_string += HISTORY_MOVE_VALUE_SEPARATOR

            history_string += self._player_to_string(move["player"])
            history_string += str(move["letter"])
            history_string += str(move["number"])
            if new_round:
                history_string += HISTORY_MOVES_IN_BETWEEN_MOVE_SEPARATOR
                new_round = False
            else:
                history_string += HISTORY_MOVES_SEPARATOR
                new_round = True

        return history_string

    def _use_string_to_create_history(self, history_string: str):
        result_history = History()
        splitted_moves = history_string.split(HISTORY_MOVES_SEPARATOR)

        # empty cell in the end due to separator location
        for move in splitted_moves:
            if len(move) == 0:
                return result_history
            move_splited = move.split(HISTORY_MOVE_VALUE_SEPARATOR)
            both_player_moves = move_splited[1].split("|")

            player_O_move = both_player_moves[PLAYER_O_VALUE]
            player_X_move = both_player_moves[PLAYER_X_VALUE]

            round = int(move_splited[HISTORY_MOVE_ROUND_INDEX])

            letterO = player_O_move[HISTORY_MOVE_LETTER_INDEX]
            numberO = player_O_move[2:]
            playerO = self._player_to_int(
                player_O_move[HISTORY_MOVE_PLAYER_INDEX])

            result_history.add_move(round, playerO, letterO, int(numberO))

            if len(player_X_move) != 0:
                letterX = player_X_move[HISTORY_MOVE_LETTER_INDEX]
                numberX = player_X_move[2:]
                playerX = self._player_to_int(
                    player_X_move[HISTORY_MOVE_PLAYER_INDEX])

                result_history.add_move(round, playerX, letterX, int(numberX))

        return result_history
