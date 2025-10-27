import pytest
import argparse
from hex.tools.parser import parse_args


@pytest.fixture
def testing_parser():
    """
    Test that parse_args set True or False on a list of parameter given
    wich is: -v --size 10 --blitz_time 60
    verbose need to be True,
    size needs to be set to 10 , blitz_time to 60
    and the -ia parameter needs to contain X
    Same with load containing test.txt
    """
    parser = parse_args(['-v', '--size', '10', "--blitz_time",
                        "60", "-ia", "X", "-load", "test.txt"], None)
    assert parser.verbose
    assert parser.debug == False
    assert parser.size == 10
    assert parser.blitz_time == 60
    assert parser.ia == "X"
    assert parser.load == "test.txt"


def testing_false_parser():
    """
    Test that parse_args exits on a board that is too big
    which is: --size 100
    size wants to be set to 100 but is normally limited to 20

    Test that parse_args exits on an unknown command
    which is: --dudufjijfd

    Test that parse_args exits on an unknown ai parameter
    which is: -ai V

    Test that parse_args exits on parameter size if it was not given
    any size
    which is: -z
    """
    with pytest.raises(SystemExit):
        parser = parse_args(['--size', '100'], None)
    with pytest.raises(SystemExit):
        parser = parse_args(['--dudufjijfd'], None)
    with pytest.raises(SystemExit):
        parser = parse_args(['-ai', 'V'], None)
    with pytest.raises(SystemExit):
        parser = parse_args(['-z'], None)
