class History():
    """
    Class that represents and handles the lists of done and undone moves.

    Attributes
    ----------
    done_moves: list[dict[str, int | str | float | None]]
        The list that store the done moves.
    undone_moves: list[dict[str, int | str | float | None]]
        The list that store the undone moves.
    default_time: float | None
        When a move is being undone, the two players timers have to be reset to the values of the move made before.
        If it is the first move that is being undone, the default time needs to be known
        because it is the value that both timers have to be set to.

    Methods
    -------
    reset(self) -> None:
        Simply empties the done and undone moves lists.
        Made to be called when a game is restarted.
    get_last_moves(self, len: int) -> tuple[list[dict[str, int | str | float | None]], list[dict[str, int | str | float | None]]]:
        Returns the last moves of done and undone moves lists.
        Used for displaying the history.
    undo(self) -> tuple[bool | dict[str, int | str | float | None], bool]:
        Used when the "undo" command is called, and places the last move of the done moves list in the undone moves one.
        Also handles an undo after a swap, in which cases it places the move that have been swapped in the undone moves list.
    redo(self) -> dict[str, int | str | float | None]:
        Used when the "redo" command is called, and places the last move of the undone moves list in the done moves one.
    add_move(self, round: int, player: int, letter: str, number: int,
                 white_time: float | None = None,
                 black_time: float | None = None) -> None:
        Adds a move in the done moves list.
        Made to be called after a move have been played.
        Also empties the undone moves list (no move should be redone after a valid move has been played).
    get_done_moves(self) -> list[dict[str, int | str | float | None]]:
        Simply returns the done moves list.
    get_undone_moves(self) -> list[dict[str, int | str | float | None]]:
        Simply returns the undone moves list.
    """

    def __init__(self, default_time: float | None = None):
        """
        History's constructor.

        Parameters
        ----------
        default_time: float | None
            When a move is being undone, the two players timers have to be reset to the values of the move made before.
            If it is the first move that is being undone, the default time needs to be known
            because it is the value that both timers have to be set to.
        """
        self.__done_moves: list[dict[str, int | str | float | None]] = []
        self.__undone_moves: list[dict[str, int | str | float | None]] = []
        self.__default_time = default_time

    def reset(self) -> None:
        """
        Simply empties the done and undone moves lists.
        Made to be called when a game is restarted.
        """
        self.__done_moves = []
        self.__undone_moves = []

    def get_last_moves(self,
                       len: int) -> tuple[list[dict[str,
                                                    int | str | float | None]],
                                          list[dict[str,
                                                    int | str | float | None]]]:
        """
        Returns the last moves of done and undone moves lists.
        Used for displaying the history.

        Parameters
        ----------
        len: int
            The maximum number of (last) moves that have to be returned for each list.
            Used for display, so that too many values won't be displayed.

        Returns
        -------
        tuple[list[dict[str, int | str | float | None]], list[dict[str, int | str | float | None]]]
            The done and undone moves lists
        """
        return self.__done_moves[:len], self.__undone_moves[:len]

    def undo(self) -> tuple[bool | dict[str, int | str | float | None], bool]:
        """
        Used when the "undo" command is called, and places the last move of the done moves list in the undone moves one.
        Also handles an undo after a swap, in which cases it places the move that have been swapped in the undone moves list.

        Parameters
        ----------
        len: int
            The maximum number of (last) moves that have to be returned for each list.
            Used for display, so that too many values won't be displayed.

        Returns
        -------
        tuple[bool | dict[str, int | str | float | None], bool]
            The move that has been undone or False if no move have been undone.
            Value used to tell if a swap have been undone or not (used to uptade current player value accordingly).
        """
        if len(self.__done_moves) == 0:
            return False, False
        move = self.__done_moves.pop(0)
        swap_undone = False
        if len(self.__done_moves) == 1 and self.__done_moves[0]["letter"] == move[
                "letter"] and self.__done_moves[0]["number"] == move["number"]:
            self.__undone_moves.insert(0, self.__done_moves.pop(0))
            swap_undone = True
        else:
            self.__undone_moves.insert(0, move.copy())
        if len(self.__done_moves) == 0:
            move["white_time"] = self.__default_time
            move["black_time"] = self.__default_time
        elif len(self.__done_moves) > 0:
            move["white_time"] = self.__done_moves[0]["white_time"]
            move["black_time"] = self.__done_moves[0]["black_time"]
        return move, swap_undone

    def redo(self) -> dict[str, int | str | float | None]:
        """
        Used when the "redo" command is called, and places the last move of the undone moves list in the done moves one.

        Returns
        -------
        dict[str, int | str | float | None]
            The move that has been redone or False if no move have been redone.
        """
        if len(self.__undone_moves) == 0:
            return False
        move = self.__undone_moves.pop(0)
        self.__done_moves.insert(0, move)
        return move

    def add_move(self, round: int, player: int, letter: str, number: int,
                 white_time: float | None = None,
                 black_time: float | None = None) -> None:
        """
        Adds a move in the done moves list.
        Made to be called after a move have been played.
        Also empties the undone moves list (no move should be redone after a valid move has been played).

        Parameters
        -------
        round: int
            The round of the move being added.
        player: int
            The player who made the move being added.
        letter: str
            The letter of the coordinates of the move being added.
        number: int
            The number of the coordinates of the move being added.
        white_time: float | None
            The value of the white player's timer when the move being added have been played.
        black_time: float | None
            The value of the black player's timer when the move being added have been played.
        """
        self.__done_moves.insert(
            0,
            {"round": round, "player": player,
             "letter": letter, "number": number,
             "white_time": white_time, "black_time": black_time})
        self.__undone_moves = []

    def get_done_moves(self) -> list[dict[str, int | str | float | None]]:
        """
        Simply returns the done moves list.

        Returns
        -------
        list[dict[str, int | str | float | None]]
            The done moves list.
        """
        return self.__done_moves

    def get_undone_moves(self) -> list[dict[str, int | str | float | None]]:
        """
        Simply returns the undone moves list.

        Returns
        -------
        list[dict[str, int | str | float | None]]
            The undone moves list.
        """
        return self.__undone_moves
