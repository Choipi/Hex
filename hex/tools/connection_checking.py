from .bitboard import Bitboard
from .game_over_state import GameOverState


def convert_bitboards_to_Y_reduction(wbits: Bitboard, bbits: Bitboard,
                                     dim: int, size: int) -> list[Bitboard]:
    """ Converts both player's bitboard to a structure used in a Hex
    adapted Y-reduction.

    Returns
    -------
    list[Bitboard]
        Y-reduction structure
    """
    # initialize columns of pairs of bits
    bits = [Bitboard(dim * 2 + 2) for i in range(dim + 1)]
    # Filling in the bottom left square that contains the board
    for i in range(size):
        assert (wbits.get_bit(i) != 1
                or bbits.get_bit(i) != 1)
        if wbits.get_bit(i) == 1:
            bits[i % dim][i // dim * 2] = 1
            bits[i % dim][i // dim * 2 + 1] = 0
        elif bbits.get_bit(i) == 1:
            bits[i % dim][i // dim * 2] = 0
            bits[i % dim][i // dim * 2 + 1] = 1
    # Filling the last line of each column besides the last two
    # with the template (here white)
    for i in range(dim - 1):
        bits[i % dim][dim * 2] = 1
        bits[i % dim][dim * 2 + 1] = 0
    # Setting the last pair of bits of the penultimate column to 11
    bits[dim - 1][dim * 2] = 1
    bits[dim - 1][dim * 2 + 1] = 1
    # Filling the last column with the template (here black)
    # the last column is always 010101...01011111
    for i in range(dim * 2 - 2):
        bits[dim][i] = i % 2
    for i in range(dim * 2 - 2, dim * 2 + 2):
        bits[dim][i] = 1
    return bits


def bitwise_parallel_reduction(bits: list[Bitboard],
                               dim: int) -> GameOverState:
    """ Perform the Bitwise Parallel Reduction algorithm on the structure.

    Parameters
    ----------
    bits: list[Bitboard]
        Y-reduction structure
    dim: int
        dimension of the board

    Returns
    -------
    GameOverState
        color that has the majority on the last triplet
    """
    cols = 2 * dim - 1
    pas = 0
    while pas < cols - 1:
        col = 0
        while col < (min(dim + 1, cols - pas) - 1):
            a = bits[col]
            b = (a << 2)  # SE neighbors (little endian)
            c = bits[col + 1]  # E neighbors
            bits[col] = (a & (b | c)) | (b & c)
            col += 1
        pas += 1
    if bits[0].get_bit(1) == 1:
        return GameOverState.BLACK_WON
    if bits[0].get_bit(0) == 1:
        return GameOverState.WHITE_WON
    return GameOverState.NO_WINNER


def connection_check(wbits: Bitboard, bbits: Bitboard,
                     dim: int, size: int) -> GameOverState:
    """ Check if the board contains a connection

    Returns
    -------
    GameOverState
        - NO_WINNER (0) if nobody has a connection
        - WHITE_WON (1) if white has a connection
        - BLACK_WON (2) if black has a connection
    """
    return bitwise_parallel_reduction(
        convert_bitboards_to_Y_reduction(wbits, bbits, dim, size), dim)
