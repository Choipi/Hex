import pytest
from random import randint, seed
from hex.tools import bitboard

seed(10)
TESTING_SIZES = 400


@pytest.fixture
def testing_bitboard():
    """Create all bitboards of size between 1 and 400"""
    bitboards = []
    for size in range(1, TESTING_SIZES + 1):
        string = ""
        for i in range(size):
            string = string + str(randint(0, 1))
        bitboards.append(bitboard.Bitboard(string))
    return bitboards


def test_get_bit():
    """
    Test that get_bit returns the correct value and raises IndexError
    if index is out of bounds.
    """
    string = ""
    size = randint(1, TESTING_SIZES)
    for i in range(size):
        string = string + str(randint(0, 1))
    position = randint(0, size - 1)
    random_bit = ord(string[position]) - ord('0')
    board = bitboard.Bitboard(string)
    assert board.get_bit(position) == random_bit

    with pytest.raises(IndexError):
        empty_board = bitboard.Bitboard(0)
        empty_board.get_bit(0)

    with pytest.raises(IndexError):
        board.get_bit(randint(20, 2000000000))

    with pytest.raises(IndexError):
        board.get_bit(randint(-2000000000, -1))


def test_set_bit(testing_bitboard):
    """
    Test that set_bit_at works with either a bit or a bool and raises
    IndexError if index is out of bounds and ValueError when the value isn't
    a bit or a bool.
    """
    for i in range(TESTING_SIZES):
        position = randint(0, i)
        testing_bitboard[i].set_bit_at(position, 1)
        assert testing_bitboard[i].get_bit(position) == 1

        position = randint(0, i)
        testing_bitboard[i].set_bit_at(position, False)
        assert testing_bitboard[i].get_bit(position) == 0

        position = randint(0, i)
        testing_bitboard[i].set_bit_at(position, 1)
        assert testing_bitboard[i].get_bit(position) == True

        with pytest.raises(IndexError):
            empty_board = bitboard.Bitboard(0)
            empty_board.set_bit_at(0, 1)

        with pytest.raises(IndexError):
            testing_bitboard[i].set_bit_at(randint(i + 1, 2000000000), 1)

        with pytest.raises(IndexError):
            testing_bitboard[i].set_bit_at(randint(-2000000000, -1), 1)

        with pytest.raises(ValueError):
            position = randint(0, i)
            testing_bitboard[i].set_bit_at(position, 'hello')

        with pytest.raises(ValueError):
            position = randint(0, i)
            testing_bitboard[i].set_bit_at(position, 35)


def test_reset(testing_bitboard):
    """Test that reset properly resets the bitboard."""
    for i in range(TESTING_SIZES):
        testing_bitboard[i].reset()
        assert testing_bitboard[i] == bitboard.Bitboard(i + 1)
