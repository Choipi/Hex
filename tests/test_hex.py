import pytest
from pytest_mock import *
from hex.__main__ import main
from hex.userinterfaces import cli


class DummyCli:
    def __init__(self, config):
        self.config = config

    def start_game():
        return


def test_main_and_quit(mocker):
    mocked_input = mocker.patch('builtins.input')
    mocked_input.side_effect = ['q', 'y']
    with pytest.raises(SystemExit):
        main()
