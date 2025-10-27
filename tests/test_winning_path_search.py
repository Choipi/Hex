import pytest
from random import randint, seed
from hex.tools.board import Board
from hex.tools.bitboard import Bitboard
from hex.tools.winning_path_search import __neighbors, winning_path_search


seed(10)
TESTING_DIMS = 20


@pytest.fixture
def testing_full_bitboards() -> list[Bitboard]:
    """Create full bitboards of dim between 1 and 20"""
    test_bitboards = []
    for dim in range(1, TESTING_DIMS + 1):
        bitboard = Bitboard(dim*dim)
        bitboard.setall(1)
        test_bitboards.append(bitboard)
    return test_bitboards


def test_neighbor_count(testing_full_bitboards):
    """
    Test that the correct number of neighbors is found for each
    tile.
    """
    assert len(__neighbors(0, 0, testing_full_bitboards[0], 1)) == 0
    for n in range(1, TESTING_DIMS):
        dim = n + 1
        bitboard = testing_full_bitboards[n]
        for i in range(dim*dim):
            is_left = i % dim == 0
            is_right = i % dim == dim - 1
            is_top = i // dim == 0
            is_bottom = i // dim == dim - 1
            if (is_left and is_top) or (is_right and is_bottom):
                assert len(__neighbors(0, i, bitboard, dim)) == 2
            elif (is_left and is_bottom) or (is_right and is_top):
                assert len(__neighbors(0, i, bitboard, dim)) == 3
            elif is_left or is_right or is_top or is_bottom:
                assert len(__neighbors(0, i, bitboard, dim)) == 4
            else:
                assert len(__neighbors(0, i, bitboard, dim)) == 6
                

def test_neighbor_order():
    """ Test that the neighbors are added in the right order. """
    # Setting the middle tile to 1
    bitboard = Bitboard("000010000")
    assert len(__neighbors(0, 4, bitboard, 3)) == 0
    # West neighbor
    bitboard.set_bit_at(3, 1)
    assert __neighbors(0, 4, bitboard, 3) == [3]
    assert __neighbors(1, 4, bitboard, 3) == [3]
    # Both north neighbors
    bitboard.set_bit_at(1, 1)
    bitboard.set_bit_at(2, 1)
    assert __neighbors(0, 4, bitboard, 3) == [3, 2, 1]
    assert __neighbors(1, 4, bitboard, 3) == [2, 1, 3]
    # East neighbor
    bitboard.set_bit_at(5, 1)
    assert __neighbors(0, 4, bitboard, 3) == [5, 3, 2, 1]
    assert __neighbors(1, 4, bitboard, 3) == [5, 2, 1, 3]
    # Both south neighbors
    bitboard.set_bit_at(6, 1)
    bitboard.set_bit_at(7, 1)
    assert __neighbors(0, 4, bitboard, 3) == [7, 6, 5, 3, 2, 1]
    assert __neighbors(1, 4, bitboard, 3) == [5, 7, 6, 2, 1, 3]


def test_winning_path_search():
    """ Test the depth first search on complex paths. """
    """
    1 . 1 1 .
     . . 1 . 1
      1 1 . 1 1
       . 1 1 . 1
        . . . . 1
    """
    white_bitboard = Bitboard("1011000101110110110100001")
    path = [('c', 1), ('c', 2), ('b', 3), ('b', 4), ('c', 4), ('d', 3),
            ('e', 3), ('e', 4), ('e', 5)]
    assert winning_path_search(0, white_bitboard, 5) == path
    """
    1 . . 1 .
     . 1 1 . .
      1 . 1 1 .
       . 1 . . 1
        . 1 1 1 .
    """
    black_bitboard = Bitboard("1001001100101100100101110")
    path = [('a', 3), ('b', 2), ('c', 2), ('c', 3), ('b', 4), ('b', 5),
            ('c', 5), ('d', 5), ('e', 4)]
    assert winning_path_search(1, black_bitboard, 5)
