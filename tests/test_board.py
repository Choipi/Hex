import pytest
from hex.tools import board
from hex.tools.bitboard import Bitboard
from random import randint, seed

seed(10)
TESTING_DIMS = 20


@pytest.fixture
def testing_boards():
    """Create all boards of dim between 1 and 20"""
    test_boards = []
    for i in range(1, TESTING_DIMS + 1):
        test_boards.append(board.Board(i))
    return test_boards


def test_check_legal_move(testing_boards):
    """
    Test that check_legal_move returns True on every space of the board at
    the start and that after playing a move on said space the function returns
    False. Also test that it raises IndexError when position in out of bounds.
    """
    for test_board in testing_boards:
        for i in range(test_board._Board__size):
            assert test_board.check_legal_move(i)
            test_board.add_move(i, 0)
            assert test_board.check_legal_move(i) == False

        with pytest.raises(IndexError):
            test_board.check_legal_move(test_board._Board__size)
        with pytest.raises(IndexError):
            test_board.check_legal_move(
                randint(test_board._Board__size, 4000000000))
        with pytest.raises(IndexError):
            test_board.check_legal_move(
                (chr(test_board._Board__dim + ord('a')), 1))
        with pytest.raises(TypeError):
            test_board.check_legal_move(('b', '4'))
        with pytest.raises(TypeError):
            test_board.check_legal_move((4, 'b'))
        with pytest.raises(TypeError):
            test_board.check_legal_move((4, 8))


def test_get_legal_moves(testing_boards):
    """
    Test that get_legal_moves returns the correct quantity of legal moves by checking
    the length and the legality of the retured moves.
    """
    for i in range(TESTING_DIMS):
        # Test that all moves are legal on a new board and
        # that get_legal_moves returns a list with every single legal move
        # possible
        assert len(testing_boards[i].get_legal_moves()) == (i + 1)**2
        for move in testing_boards[i].get_legal_moves():
            assert testing_boards[i].check_legal_move(i)
        # Play a random move and test that the returned list is 1 move shorter
        # and that all moves returned after that are legal.
        position = randint(0, (i + 1)**2 - 1)
        testing_boards[i].add_move(position, 0)
        assert len(testing_boards[i].get_legal_moves()) == (i + 1)**2 - 1
        for move in testing_boards[i].get_legal_moves():
            assert testing_boards[i].check_legal_move(move)
        # Play every possible legal move and test that the returned list
        # is empty.
        for move in range((i + 1)**2):
            testing_boards[i].add_move(move, 1)
        assert len(testing_boards[i].get_legal_moves()) == 0


def test_add_move(testing_boards):
    """
    Test that add_move makes the space illegal to play on the board
    and that it raises IndexError when the given position is out of bounds.
    """
    for i in range(TESTING_DIMS):
        position = randint(0, (i + 1)**2 - 1)
        assert testing_boards[i].check_legal_move(position)
        testing_boards[i].add_move(position, 1)
        assert testing_boards[i].check_legal_move(position) == False

        with pytest.raises(IndexError):
            testing_boards[i].add_move((i + 1)**2, 0)
        with pytest.raises(IndexError):
            testing_boards[i].add_move(-1, 0)
        with pytest.raises(IndexError):
            testing_boards[i].add_move(randint((i + 1)**2, 2000000000), 0)

        with pytest.raises(TypeError):
            testing_boards[i].add_move(('b', '4'), 0)
        with pytest.raises(TypeError):
            testing_boards[i].add_move((4, 'b'), 0)
        with pytest.raises(TypeError):
            testing_boards[i].add_move((4, 8), 0)

        with pytest.raises(ValueError):
            testing_boards[i].add_move(i, -1)


def test_remove_move(testing_boards):
    """
    Test that remove_move restores the legality of the position on the board
    and that it raises IndexError when the given position is out of bounds.
    """
    for i in range(TESTING_DIMS):
        position = randint(0, (i + 1)**2 - 1)
        assert testing_boards[i].check_legal_move(position)
        testing_boards[i].add_move(position, 1)
        assert testing_boards[i].check_legal_move(position) == False
        testing_boards[i].remove_move(position, 1)

        assert testing_boards[i].check_legal_move(position)
        testing_boards[i].add_move(position, 0)
        assert testing_boards[i].check_legal_move(position) == False
        testing_boards[i].remove_move(position, 0)
        assert testing_boards[i].check_legal_move(position)

        with pytest.raises(IndexError):
            testing_boards[i].remove_move((i + 1)**2, 0)
        with pytest.raises(IndexError):
            testing_boards[i].remove_move(-1, 0)
        with pytest.raises(IndexError):
            testing_boards[i].remove_move(randint((i + 1)**2, 2000000000), 0)

        with pytest.raises(TypeError):
            testing_boards[i].remove_move(('b', '4'), 0)
        with pytest.raises(TypeError):
            testing_boards[i].remove_move((4, 'b'), 0)
        with pytest.raises(TypeError):
            testing_boards[i].remove_move((4, 8), 0)

        with pytest.raises(ValueError):
            testing_boards[i].remove_move(i, -1)


def test_get_dim(testing_boards):
    """ Test that get_dim returns the correct dimension. """
    for i in range(TESTING_DIMS):
        assert testing_boards[i].get_dim() == i + 1


def test_reset(testing_boards):
    """ Test that rest resets both bitboards. """
    for i in range(1, TESTING_DIMS):
        # Playing some moves
        for j in range(randint(i * i // 2, i * i - 1)):
            testing_boards[i].add_move(randint(0, i * i - 1), 0)
            testing_boards[i].add_move(randint(0, i * i - 1), 1)
        # resetting
        testing_boards[i].reset()
        assert testing_boards[i]._Board__bbits == Bitboard((i + 1)**2)
        assert testing_boards[i]._Board__wbits == Bitboard((i + 1)**2)


def test_get_space_value(testing_boards):
    """
    Test that get_space_value returns the correct code
    depending on the player that owns the space.
    """
    for n in range(1, TESTING_DIMS):
        position = randint(0, n)
        player = randint(0, 1)
        assert testing_boards[n].get_space_value(position) == 0
        testing_boards[n].add_move(position, player)
        assert testing_boards[n].get_space_value(position) == player + 1
        testing_boards[n].remove_move(position, player)
        assert testing_boards[n].get_space_value(position) == 0


def test_translate(testing_boards):
    """ Test that the translate methods correctly convert positions. """
    for n in range(TESTING_DIMS):
        dim = n + 1
        # Testing every possible legal move
        for i in range(dim):
            for j in range(dim):
                letter = chr(i + ord('a'))
                number = j + 1

                int_position = testing_boards[n]._Board__translate(
                    (letter, number))
                testing_boards[n].add_move(int_position, 1)

                tuple_position = testing_boards[n]._Board__reverse_translate(
                    int_position)
                assert tuple_position == (letter, number)

                testing_boards[n].remove_move(tuple_position, 1)
                empty_board = board.Board(dim)
                assert testing_boards[n]._Board__wbits == empty_board._Board__wbits
                assert testing_boards[n]._Board__bbits == empty_board._Board__bbits

    with pytest.raises(ValueError):
        testing_boards[0]._Board__translate(('ab', 4))
    with pytest.raises(ValueError):
        testing_boards[0]._Board__translate((4, 4))
    with pytest.raises(ValueError):
        testing_boards[0]._Board__translate(('b', '4'))
    with pytest.raises(ValueError):
        testing_boards[0]._Board__translate(('b', -1))
    with pytest.raises(IndexError):
        testing_boards[10]._Board__translate(('l', 4))


def test_str():
    """ Test that the str method returns the correct string. """
    testing_board = board.Board(5)
    test_string = "  a b c d e\n   o o o o o\n1 x . . . . . x \n 2 x . . . "
    test_string += ". . x \n  3 x . . . . . x \n   4 x . . . . . x \n"
    test_string += "    5 x . . . . . x \n         o o o o o "
    assert test_string == str(testing_board)
