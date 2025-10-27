import pytest
from hex.tools import board
from hex.tools.bitboard import Bitboard
from hex.tools.connection_checking import *
from hex.tools.game_over_state import GameOverState


def test_has_connection_patterns():
    """
    Test that has_connection returns the desired value on boards
    representing some patterns.
    """
    dim = 20
    testing_board = board.Board(dim)
    # Testing on two vertical lines
    for i in range(dim - 1):
        testing_board.add_move(dim * i, 0)
        testing_board.add_move(dim*i + 1, 1)
        assert testing_board.has_connection() == GameOverState.NO_WINNER
    testing_board.add_move(dim * (dim - 1), 0)
    assert testing_board.has_connection() == GameOverState.WHITE_WON

    testing_board.reset()

    # Testing on two horizontal lines
    for i in range(dim - 1):
        testing_board.add_move(i, 0)
        testing_board.add_move(dim + i, 1)
        assert testing_board.has_connection() == GameOverState.NO_WINNER
    testing_board.add_move(dim - 1, 0)
    assert testing_board.has_connection() == GameOverState.NO_WINNER
    testing_board.add_move(dim + dim - 1, 1)
    assert testing_board.has_connection() == GameOverState.BLACK_WON

    testing_board.reset()

    # Testing on a zigzagging path
    for i in range(dim):
        if (i % 4) == 0 or (i % 4) == 2:
            for j in range(dim):
                testing_board.add_move(i*dim + j, 0)
        elif (i % 4) == 1:
            for j in range(dim - 1):
                testing_board.add_move(i*dim + j, 1)
            testing_board.add_move(i*dim + dim - 1, 0)
        elif (i % 4) == 3:
            for j in range(1, dim):
                testing_board.add_move(i*dim + j, 1)
            testing_board.add_move(i * dim, 0)
    assert testing_board.has_connection() == GameOverState.WHITE_WON


def test_has_connection_pre_calculated():
    """
    Test that has_connection and its sub functions return the desired
    value on pre-calculated boards.
    """
    # Y-reduction structure - white is winning
    bits1 = [Bitboard('00000000000010100110'),
             Bitboard('01101000011001100110'),
             Bitboard('10011010100001100110'),
             Bitboard('01000101010010011010'),
             Bitboard('00011001100010100110'),
             Bitboard('00011010000000000010'),
             Bitboard('00010000000000000010'),
             Bitboard('00000000000000000010'),
             Bitboard('00000000000000000011'),
             Bitboard('01010101010101011111')]
    # Y-reduction structure - nobody is winning
    bits2 = [Bitboard('00000000000010100110'),
             Bitboard('01101000011001100110'),
             Bitboard('10011010100001100110'),
             Bitboard('01000101010010010110'),
             Bitboard('00011001100010100110'),
             Bitboard('00011010000000000010'),
             Bitboard('00010000000000000010'),
             Bitboard('00000000000000000010'),
             Bitboard('00000000000000000011'),
             Bitboard('01010101010101011111')]
    # Y-reduction structure - black is winning
    bits3 = [Bitboard('01000000000010100110'),
             Bitboard('01101000011001100110'),
             Bitboard('01011010100001100110'),
             Bitboard('01000101010010010110'),
             Bitboard('01011001100010100110'),
             Bitboard('01011010000000000010'),
             Bitboard('01010000000000000010'),
             Bitboard('01000000000000000010'),
             Bitboard('01000000000000000011'),
             Bitboard('01010101010101011111')]
    # Bitboards representing the first board (bits1)
    black_board = Bitboard('010100000001011100000100000000110000010100000000 \
                           000000011000000000100000111010000')
    white_board = Bitboard('001000000010000000011011000001001000001010000010 \
                           000000100110000111010000000100000')

    testing_board = board.Board(9)
    testing_board._Board__bbits = black_board
    testing_board._Board__wbits = white_board

    bits4 = convert_bitboards_to_Y_reduction(white_board, black_board,
                                             testing_board.get_dim(),
                                             testing_board.get_dim()**2)
    for i in range(10):
        assert bits1[i] == bits4[i]
    assert testing_board.has_connection() == GameOverState.WHITE_WON
    assert bitwise_parallel_reduction(bits1, 9) == GameOverState.WHITE_WON
    assert bitwise_parallel_reduction(bits2, 9) == GameOverState.NO_WINNER
    assert bitwise_parallel_reduction(bits3, 9) == GameOverState.BLACK_WON
