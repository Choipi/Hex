from bitarray import bitarray


class Bitboard(bitarray):
    """ A class to represent and handle a bitboard.

    Methods
    -------
    get_bit(position: int) -> int:
        Get the bit position of the Bitboard
    set_bit_at(index: int, value: int | bool) -> None:
        Change the value of the bit at position index in the bitboard
        to the specified value.
    reset() -> None:
        Reset the bitboard by setting all its bits to 0.
    """

    def __init__(self, initializer: int | str):
        """
        Parameters
        ----------
        initializer: int | str
            - if an integer is given: creates a Bitboard of specified
            length
            - if a string is given: initialize from string
        """

        bitarray(initializer, endian='little')

    def get_bit(self, index: int) -> int:
        """Get the bit position in the Bitboard

        Parameters
        ----------
        index: int
            position to check

        Returns
        -------
        int
            value of the bit

        Raises
        ------
        IndexError
            If index is out of bounds
        """
        if (index >= len(self) or index < 0):
            raise IndexError
        return self[index]

    def set_bit_at(self, index: int, value: int | bool) -> None:
        """ Change the value of the bit at position index in the
        bitboard to the specified value.

        Parameters
        ----------
        index: int
            index in the bitboard
        value: int | bool
            value that will replace the current value of the bit
            (either 0, 1, True or False)

        Raises
        ------
        IndexError
            If index is out of bounds
        ValueError
            If value is not 0, 1, True or False
        """
        if (index >= len(self) or index < 0):
            raise IndexError("Index out of bounds")
        if (value not in [0, 1, False, True]):
            raise ValueError(
                "value is expected to be either 0, 1, True or False")
        self[index] = value

    def reset(self) -> None:
        """Reset the bitboard by setting all its bits to 0."""
        self.setall(0)
