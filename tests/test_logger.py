import logging
import pytest
from hex.tools.logger import setup_logging_level, LogLevel, log


@pytest.mark.parametrize("log_option, expected_level", [
    ("-v", logging.INFO),
    ("--verbose", logging.INFO),
    ("-d", logging.DEBUG),
    ("--debug", logging.DEBUG),
])
def test_setup_logging_level_valid(mocker, log_option,
                                   expected_level):
    """Tests every logging setup at once"""
    mock_basicConfig = mocker.patch("logging.basicConfig")

    setup_logging_level(log_option)

    mock_basicConfig.assert_called_once_with(
        level=expected_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        force=True
    )


"""TODO: Il faudra un test pour s'assurer que setup_logging_level est
appelé correctement selon l'option en ligne de commande
"""


def test_setup_logging_level_invalid():
    """Test separately setup logging with invalid param"""
    with pytest.raises(RuntimeError, match="Unknown logging level "
                       "'invalid_option'."):
        setup_logging_level("invalid_option")


@pytest.mark.parametrize("log_level, logging_function", [
    (LogLevel.DEBUG, "debug"),
    (LogLevel.INFO, "info"),
    (LogLevel.WARNING, "warning"),
    (LogLevel.ERROR, "error"),
    (LogLevel.CRITICAL, "critical"),
])
def test_log(mocker, log_level, logging_function):
    """Test that log() calls the correct logging function based on LogLevel."""

    mock_debug = mocker.patch("logging.Logger.debug")
    mock_info = mocker.patch("logging.Logger.info")
    mock_warning = mocker.patch("logging.Logger.warning")
    mock_error = mocker.patch("logging.Logger.error")
    mock_critical = mocker.patch("logging.Logger.critical")

    log(log_level, "Test message")

    expected_mock = {
        "debug": mock_debug,
        "info": mock_info,
        "warning": mock_warning,
        "error": mock_error,
        "critical": mock_critical,
    }[logging_function]

    # assert that the correct LogLevel has been used
    expected_mock.assert_called_once_with("Test message")

    for func_name, mock_func in {
        "debug": mock_debug,
        "info": mock_info,
        "warning": mock_warning,
        "error": mock_error,
        "critical": mock_critical,
    }.items():
        if func_name != logging_function:
            # assert that every other LogLevel hasn't been used
            mock_func.assert_not_called()
