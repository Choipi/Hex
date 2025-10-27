from __future__ import annotations
from .game_over_state import GameOverState
from .bitboard import Bitboard
from .connection_checking import connection_check
from .winning_path_search import winning_path_search


EMPTY_TILE = 0
WHITE_TILE = 1
BLACK_TILE = 2

PLAYER_O = 0
PLAYER_X = 1


class Board:
    """ A class to represent the game board

    Attributes
    ----------
    dim: int
        the dimension of the board. Example: for a 9x9 board, dim = 9
    size: int
        size of the board's bitboards. It's always equal to dim * dim
    wbits: Bitboard
        Bitboard that represents white's pieces
    bbits: Bitboard
        Bitboard that represents black's pieces

    Methods
    -------
    - check_legal_move(position: int) -> bool:
        returns True if the position is free in both Bitboards
    - get_legal_moves() -> list[int]:
        returns a list of all legal moves according to the board's
        current state
    - add_move(position: int, player: int) -> None:
        sets the bit position of player's bitboard to 1
    - remove_move(position: int, player: int) -> None:
        sets the bit position of player's bitboard to 0
    - reset() -> None:
        sets all bits of all Bitboards to 0
    - has_connection() -> int:
        checks if the board contains a connection and returns an
        integer value that represents the winner
    - winning_path(self, player: int) -> list[tuple[str, int]]:
        returns the winning path of the winning player.
    """

    def __init__(self, dim: int):
        """ Board class's constructor.

        Parameters
        ----------
        dim: int
            the dimension of the board. Example: for a 9x9 board,
            dim = 9
        """
        self.__dim = dim
        self.__size = dim * dim
        self.__wbits = Bitboard(self.__size)
        self.__bbits = Bitboard(self.__size)

    def check_legal_move(self, position: int | tuple[str, int]) -> bool:
        """ Check if the move is legal by verifying that the position
        is empty.

        Parameters
        ----------
        position: int | tuple[str, int]
            Either an integer representing a one dimensional position
            or a tuple containing the letter representing the column
            of the board and the number representing the line of the
            board.

        Returns
        -------
        bool
            True if legal else False

        Raises
        ------
        TypeError
            If position is a tuple but not of str and int
        IndexError
            If position is out of bounds
        """
        if isinstance(position, tuple):
            if isinstance(position[0], str) and isinstance(position[1], int):
                position = self.__translate(position)
            else:
                raise TypeError("position is a tuple but not of str and int")
        if position >= self.__size:
            raise IndexError("position is out of bounds")
        bitboard_of_empty_spaces = ~(self.__wbits | self.__bbits)
        return bool(bitboard_of_empty_spaces[position])

    def get_legal_moves(self) -> list[tuple[str, int]]:
        """ Get all possible legal moves according to the board's
        current configuration.

        Returns
        -------
        list[tuple[str, int]]
            list of all legal moves
        """
        legal_moves = []
        for move in range(self.__size):
            if self.check_legal_move(move):
                letter, number = self.__reverse_translate(move)
                legal_moves.append((letter, number))
        return legal_moves

    def add_move(self, position: int | tuple[str, int], player: int) -> None:
        """ Set bit position of player's bitboard to 1.

        Parameters
        ----------
        position: int | tuple[str, int]
            Either an integer representing a one dimensional position
            or a tuple containing the letter representing the column
            of the board and the number representing the line of the
            board.
        player: int
            which player's bitboard to change

        Raises
        ------
        TypeError
            if position is a tuple but not of str and int
        IndexError
            if position is out of bounds
        ValueError
            if an unknown player identifier is given
        """
        if isinstance(position, tuple):
            if isinstance(position[0], str) and isinstance(position[1], int):
                position = self.__translate(position)
            else:
                raise TypeError("position is a tuple but not of str and int")
        if position >= self.__size:
            raise IndexError("position is out of bounds")
        if player == PLAYER_O:
            self.__wbits.set_bit_at(position, 1)
        elif player == PLAYER_X:
            self.__bbits.set_bit_at(position, 1)
        else:
            raise ValueError("Unknown player identifier")

    def remove_move(self, position: int | tuple[str, int],
                    player: int) -> None:
        """ Set bit position of player's bitboard to 0.

        Parameters
        ----------
        position: int | tuple[str, int]
            Either an integer representing a one dimensional position
            or a tuple containing the letter representing the column
            of the board and the number representing the line of
            the board.
        player: int
            which player's bitboard to change

        Raises
        ------
        TypeError
            if position is a tuple but not of str and int
        IndexError
            if position is out of bounds
        ValueError
            if an unknown player identifier is given
        """
        if isinstance(position, tuple):
            if isinstance(position[0], str) and isinstance(position[1], int):
                position = self.__translate(position)
            else:
                raise TypeError("position is a tuple but not of str and int")
        if position >= self.__size:
            raise IndexError("position is out of bounds")
        if player == PLAYER_O:
            self.__wbits.set_bit_at(position, 0)
        elif player == PLAYER_X:
            self.__bbits.set_bit_at(position, 0)
        else:
            raise ValueError("Unknown player identifier")

    def reset(self) -> None:
        """Resets both player's bitboard"""
        self.__wbits.reset()
        self.__bbits.reset()

    def has_connection(self) -> GameOverState:
        """ Check if the board contains a connection

        Returns
        -------
        GameOverState
            - NO_WINNER (0) if nobody has a connection
            - WHITE_WON (1) if white has a connection
            - BLACK_WON (2) if black has a connection
        """
        return connection_check(self.__wbits, self.__bbits,
                                self.__dim, self.__size)

    def get_dim(self) -> int:
        """Returns the dimension of the board"""
        return self.__dim

    def get_space_value(self, position: int | tuple[str, int]) -> int:
        """ Get the value of a tile.

        Parameters
        ----------
        position: int | tuple[str, int]
            Either an integer representing a one dimensional position
            or a tuple containing the letter representing the column
            of the board and the number representing the line of the
            board.

        Returns
        -------
        int
            0 if empty;
            1 if white;
            2 if black

        Raises
        ------
        TypeError
            if the given position is a tuple but not an instance of
            tuple[str, int]
        """
        if isinstance(position, tuple):
            if isinstance(position[0], str) and isinstance(position[1], int):
                position = self.__translate(position)
            else:
                raise TypeError(
                    "Given tuple position isn't an instance of tuple[str, int]")
        if self.__wbits.get_bit(position):
            return 1
        if self.__bbits.get_bit(position):
            return 2
        return 0

    def __translate(self, position: int | tuple[str, int]) -> int:
        """ Translate a position represented by a letter representing
        columns and a number representing lines to a one dimensional
        integer position used in bitboards.

        Parameters
        ----------
        position: tuple[str, int]
            The letter representing the column of the board and
            the number representing the line of the board.

        Returns
        -------
        int
            one dimensional position

        Raises
        ------
        ValueError
            if the first element of position  isn't a single character
            or if the second element isn't a non null positive
            integer
        IndexError
            if the computed position is out of bounds
        """
        if not isinstance(position[0], str) \
                or not position[0].isalpha() \
                or not len(position[0]) == 1:
            raise ValueError(
                "First element of position is supposed to be a single character")
        if not isinstance(position[1], int) or position[1] <= 0:
            raise ValueError("Second element of position is supposed to be a"
                             " non null positive integer")
        if ord(position[0]) - ord('a') >= self.__dim:
            raise IndexError("Given position is out of bounds")
        index = (position[1] - 1) * self.__dim + ord(position[0]) - ord('a')
        return index

    def __reverse_translate(self, position: int):
        """ Translate a position represented by an integer to a
        position represented by a letter and a number.

        Parameters
        ----------
        position: int
            Integer position

        Returns
        -------
        str
            character representing the column of the board
        int
            number representing the line of the board

        Raises
        ------
        ValueError
            if given position is out of bounds
        """
        if position < 0 or position > self.__dim**2:
            raise ValueError("Given position is out of bounds")
        letter = chr(position % self.__dim + ord('a'))
        number = position // self.__dim + 1
        return letter, number

    def winning_path(self, player: int) -> list[tuple[str, int]]:
        """ Gets the path of the winning player.

        Parameters
        ----------
        player: int
            winning player

        Returns
        -------
        list[tuple[str, int]]
            The winning path connecting the player's two sides
        """
        path = winning_path_search(player, self.__wbits, self.__dim) \
            if player == PLAYER_O else \
            winning_path_search(player, self.__bbits, self.__dim)
        return path

    def duplicate_board(self) -> Board:
        """Duplicate the board.

        Returns
        -------
        Board
            an exact copy of this board
        """
        clone = Board(self.__dim)
        for i in range(self.__size):
            space_value = self.get_space_value(i)
            if space_value != EMPTY_TILE:
                if space_value == WHITE_TILE:
                    clone.add_move(i, PLAYER_O)
                if space_value == BLACK_TILE:
                    clone.add_move(i, PLAYER_X)
        return clone

    def get_neighbors(self, position: int | tuple[str, int]) -> list[int]:
        """ Get the neighbors of a given position.

        Parameters
        ----------
        position: int | tuple[str, int]
            Either an integer representing a one-dimensional position
            or a tuple containing the letter representing the column
            of the board and the number representing the line of the
            board.

        Returns
        -------
        list[int]
            A list of one-dimensional positions representing the
            neighbors.

        Raises
        ------
        TypeError
            If position is a tuple but not of str and int.
        IndexError
            If position is out of bounds.
        """
        if isinstance(position, tuple):
            if isinstance(position[0], str) and isinstance(position[1], int):
                position = self.__translate(position)
            else:
                raise TypeError("position is a tuple but not of str and int")
        if position >= self.__size:
            raise IndexError("position is out of bounds")

        neighbors = []
        row, col = divmod(position, self.__dim)

        # Define possible neighbor offsets
        offsets = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1)]

        for dr, dc in offsets:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.__dim and 0 <= nc < self.__dim:
                neighbors.append(nr * self.__dim + nc)

        return neighbors

    def __str__(self) -> str:
        board_str = " "
        for i in range(self.__dim):
            board_str += f" {chr(ord('a') + i)}"
        board_str += "\n  "
        for i in range(self.__dim):
            board_str += " o"
        board_str += "\n"
        for i in range(self.__dim):
            board_str += f"{' '*(i-min(1, (i+1)//10))}{i+1} x"
            for j in range(self.__dim):
                if self.__wbits.get_bit(i * self.__dim + j) == 1:
                    board_str += " O"
                elif self.__bbits.get_bit(i * self.__dim + j) == 1:
                    board_str += " X"
                else:
                    board_str += " ."
            board_str += " x \n"
        board_str += " " * self.__dim + "    " + "o " * self.__dim
        return board_str

    def __eq__(self, board) -> bool:
        if not isinstance(board, Board):
            return False
        for row in range(self.__dim):
            for col in range(self.__dim):
                if self.get_space_value(row * self.__dim + col) \
                        != board.get_space_value(row * self.__dim + col):
                    return False
        return True
