import pytest
from hex.tools.history import History


@pytest.fixture
def testing_history():
    """
    Returns an instance of the History class that could be used for testing.
    """
    return History()


@pytest.fixture
def testing_moves():
    """
    Returns a set of moves that could be used for testing.
    """
    move_1 = (1, "O", "a", "1")
    move_2 = (1, "X", "b", "2")
    move_3 = (2, "O", "c", "3")
    move_4 = (2, "X", "d", "4")
    move_5 = (3, "O", "ea", "5")
    return move_1, move_2, move_3, move_4, move_5


def test_create(testing_history):
    """
    Tests that the create of a History instance is valid and that both done and undone moves lists are empty.
    """
    assert testing_history._History__done_moves == [
    ] and testing_history._History__undone_moves == []


def test_add_move(testing_history, testing_moves):
    """
    Tests that adding two moves to the history currectly puts them in the done moves list and in the correct order.
    """
    testing_history.add_move(*testing_moves[0])
    testing_history.add_move(*testing_moves[1])
    assert testing_history._History__undone_moves == []
    assert len(testing_history._History__done_moves) == 2
    assert testing_history._History__done_moves[0] == {
        "round": 1,
        "player": "X",
        "letter": "b",
        "number": "2",
        "white_time": None,
        "black_time": None}
    assert testing_history._History__done_moves[1] == {
        "round": 1,
        "player": "O",
        "letter": "a",
        "number": "1",
        "white_time": None,
        "black_time": None}


def test_undo(testing_history, testing_moves):
    """
    Tests that undoing moves works as intended by putting the undone move in the undone moves list.
    """
    assert testing_history.undo() == (False, False)
    for i in range(5):
        testing_history.add_move(*testing_moves[i])
    assert len(testing_history._History__done_moves) == 5
    assert len(testing_history._History__undone_moves) == 0
    for i in range(1, 5):
        assert testing_history.undo()[0] == testing_history._History__undone_moves[0] == {
            "round": testing_moves[-i][0], "player": testing_moves[-i][1], "letter": testing_moves[-i][2], "number": testing_moves[-i][3], "white_time": None, "black_time": None}
    assert len(testing_history._History__done_moves) == 1
    assert len(testing_history._History__undone_moves) == 4
    assert testing_history._History__done_moves[0] == {
        "round": testing_moves[0][0],
        "player": testing_moves[0][1],
        "letter": testing_moves[0][2],
        "number": testing_moves[0][3],
        "white_time": None,
        "black_time": None}


def test_redo(testing_history, testing_moves):
    """
    Tests that redoing moves works as intended by putting the redone move in the done moves list.
    """
    for i in range(5):
        testing_history.add_move(*testing_moves[i])
    assert testing_history.redo() == False
    for i in range(4):
        testing_history.undo()
    for i in range(1, 3):
        assert testing_history.redo() == testing_history._History__done_moves[0] == {
            "round": testing_moves[i][0],
            "player": testing_moves[i][1],
            "letter": testing_moves[i][2],
            "number": testing_moves[i][3],
            "white_time": None,
            "black_time": None}
    assert testing_history._History__done_moves[2] == {
        "round": testing_moves[0][0],
        "player": testing_moves[0][1],
        "letter": testing_moves[0][2],
        "number": testing_moves[0][3],
        "white_time": None,
        "black_time": None}
    assert len(testing_history._History__done_moves) == 3
    assert len(testing_history._History__undone_moves) == 2
    for i in range(2):
        assert testing_history._History__undone_moves[i] == {"round": testing_moves[3 +
                                                                                    i][0], "player": testing_moves[3 +
                                                                                                                   i][1], "letter": testing_moves[3 +
                                                                                                                                                  i][2], "number": testing_moves[3 +
                                                                                                                                                                                 i][3], "white_time": None, "black_time": None}


def test_reset(testing_history, testing_moves):
    """
    Tests that the reset method works as intended by emptying the done and undone moves lists.
    """
    testing_history.add_move(*testing_moves[0])
    testing_history.add_move(*testing_moves[1])
    testing_history.undo()
    testing_history.undo()
    testing_history.redo()
    assert len(testing_history._History__done_moves) == len(
        testing_history._History__undone_moves) == 1
    assert testing_history._History__done_moves[0] == {
        "round": 1,
        "player": "O",
        "letter": "a",
        "number": "1",
        "white_time": None,
        "black_time": None}
    assert testing_history._History__undone_moves[0] == {
        "round": 1,
        "player": "X",
        "letter": "b",
        "number": "2",
        "white_time": None,
        "black_time": None}
    testing_history.reset()
    assert testing_history._History__undone_moves == []
    assert testing_history._History__done_moves == []


def test_undo_then_add_move(testing_history, testing_moves):
    """
    Tests that adding a move after undoing a move correctly empties the undone moves list.
    """
    testing_history.add_move(*testing_moves[0])
    testing_history.add_move(*testing_moves[1])
    testing_history.add_move(*testing_moves[2])
    testing_history.undo()
    testing_history.undo()
    assert len(testing_history._History__done_moves) == 1
    assert len(testing_history._History__undone_moves) == 2
    testing_history.add_move(*testing_moves[3])
    assert len(testing_history._History__done_moves) == 2
    assert len(testing_history._History__undone_moves) == 0


def test_undo_then_redo_twice(testing_history, testing_moves):
    """
    Tests that both lists evolve as intended in a random scenario of several undos and redos.
    """
    for i in range(5):
        testing_history.add_move(*testing_moves[i])
    for i in range(4):
        testing_history.undo()
    for i in range(3):
        testing_history.redo()
    for i in range(2):
        testing_history.undo()
    for i in range(1):
        testing_history.redo()
    assert len(testing_history._History__done_moves) == 3
    assert len(testing_history._History__undone_moves) == 2
    for i in range(3):
        assert testing_history._History__done_moves[i] == {"round": testing_moves[2 -
                                                                                  i][0], "player": testing_moves[2 -
                                                                                                                 i][1], "letter": testing_moves[2 -
                                                                                                                                                i][2], "number": testing_moves[2 -
                                                                                                                                                                               i][3], "white_time": None, "black_time": None}
    for i in range(2):
        assert testing_history._History__undone_moves[i] == {"round": testing_moves[3 +
                                                                                    i][0], "player": testing_moves[3 +
                                                                                                                   i][1], "letter": testing_moves[3 +
                                                                                                                                                  i][2], "number": testing_moves[3 +
                                                                                                                                                                                 i][3], "white_time": None, "black_time": None}
