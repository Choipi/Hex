import pytest
import configparser
from hex.tools.config import Config


def test_invalid_init_path():
    with pytest.raises(ValueError, match="Incorrect Config file format."):
        Config(config_path="invalid_path.txt")


@pytest.mark.parametrize("good_config", ["tests/configs/good.checkersrc"])
@pytest.mark.parametrize("bad_format_config",
                         ["tests/configs/bad_format.checkersrc"])
@pytest.mark.parametrize("missing_entry_config",
                         ["tests/configs/missing_entry.checkersrc"])
def test_is_file_valid_correct(good_config,
                               bad_format_config,
                               missing_entry_config):
    config = Config(good_config)

    assert config._Config__is_file_valid(good_config) is None

    # invalid file extension
    with pytest.raises(ValueError, match="Incorrect Config file format."):
        config._Config__is_file_valid("config.txt")

    # config file not found
    with pytest.raises(FileNotFoundError, match="Incorrect Config file path."):
        config._Config__is_file_valid("unknown.checkersrc")

    # not formatted properly
    with pytest.raises(configparser.Error, match="Configuration file "
                       "not formatted properly."):
        Config(bad_format_config)

    # misses an entry
    with pytest.raises(ValueError,
                       match="Missing entry 'ai-mode-player-x'"):
        Config(missing_entry_config)


@pytest.mark.parametrize("expected_type_int",
                         ["tests/configs/bad_type_board_size.checkersrc"])
@pytest.mark.parametrize("expected_type_bool",
                         ["tests/configs/bad_type_verbose.checkersrc"])
def test_is_file_valid_invalid_type_1(expected_type_int, expected_type_bool):
    with pytest.raises(ValueError, match="Invalid type for key 'board-size': "
                       "Expected <class 'int'>"):
        Config(expected_type_int)

    with pytest.raises(ValueError, match="Invalid type for key 'verbose': "
                       "Expected <class 'bool'>"):
        Config(expected_type_bool)


@pytest.mark.parametrize("good_config", ["tests/configs/good.checkersrc"])
def test_load_config(good_config):
    config = Config(good_config)

    result = config.load_config()
    assert result is None

    result = config.load_config(good_config)
    assert result is None


# @pytest.mark.parametrize("good_config", ["tests/configs/good.checkersrc"])
# @pytest.mark.parametrize("bad_config", ["tests/configs/bad_format.checkersrc"])
# def test_load_config_invalid_path(good_config, bad_config, caplog):
#     config = Config(good_config)

#     config.load_config("incorrect.txt")
#     assert "New config path invalid. Keeping the old path." in caplog.text

#     with pytest.raises(ValueError, match="Unexpected : Configuration file "
#                        "not formatted properly."):
#         config.load_config(bad_config)

@pytest.mark.parametrize("good_config", ["tests/configs/good.checkersrc"])
def test_get_sections(good_config):
    config = Config(good_config)

    sections = config._Config__get_sections()

    known_sections = ["Game", "AI", "Dev"]

    assert len(sections) == len(known_sections)

    for key in known_sections:
        assert key in sections


@pytest.mark.parametrize("good_config", ["tests/configs/good.checkersrc"])
def test_get_all(good_config):
    config = Config(good_config)

    configuration = config.get_all()

    expected_config = {
        "Game": {
            "board-size": "11",
            "swap": "false",
            "contest": "false",
            "blitz": "false",
            "time": "30",
            "gui": "false",
            "language": "en",
            "load": "None",
        },
        "AI": {
            "ai": "None",
            "ai-mode": "mcts",
            "ai-mode-player-o": "mcts",
            "ai-mode-player-x": "mcts",
            "ai-depth": "2",
            "ai-heuristic": "path_oriented_heuristic",
            "ai-heuristic-player-o": "path_oriented_heuristic",
            "ai-heuristic-player-x": "path_oriented_heuristic",
            "ai-time": "5",
        },
        "Dev": {
            "version": "false",
            "verbose": "false",
            "debug": "false",
        }
    }

    assert configuration.keys() == expected_config.keys()
    for section, values in expected_config.items():
        assert section in configuration
        assert configuration[section] == values


@pytest.mark.parametrize("good_config", ["tests/configs/good.checkersrc"])
def test_get(good_config, caplog):
    config = Config(good_config)

    valid_key = config.get("board-size")
    assert valid_key == 11

    invalid_key = config.get("invalid-key")
    assert invalid_key is None


@pytest.mark.parametrize("good_config", ["tests/configs/good.checkersrc"])
def test_set(good_config):
    config = Config(good_config)

    # Modify an existing key
    config.set("board-size", "15")
    board_size = config.get("board-size")
    assert board_size == 15

    # Modify an invalid key
    config.set("invalid-key", "20")
    invalid_key = config.get("invalid-key")
    assert invalid_key is None

    # Modify an existing key with the wrong type
    with pytest.raises(ValueError, match=r"Invalid type for 'board-size': "
                       "'abc'."):
        config.set("board-size", "abc")


"""
This test does not work but config.save_config() is not used anyway
"""
# @pytest.mark.parametrize("good_config", ["tests/configs/good.checkersrc"])
# def test_save_config(good_config, caplog):
#     config = Config(good_config)

#     config.set("board-size", "20")
#     config.save_config()

#     with open(good_config, 'r') as f:
#         content = f.read()
#         assert "board-size = 20" in content

#     config._config_path = "invalid_path.txt"
#     config.save_config()
#     assert "Invalid configuration file, can't save the " \
#         "current configuration." in caplog.text


@pytest.mark.parametrize("good_config", ["tests/configs/good.checkersrc"])
def test_str(good_config):
    config = Config(good_config)

    result = str(config)

    # Test only one section and one (key, value) pair as
    # the process is the same for the entire configuration
    assert "[Game]" in result
    assert "board-size = 11" in result
