import configparser
import os
from .logger import LogLevel, log
from typing import Union, Dict


class Config:
    """A class representing the configuration of the game.

    Attributes
    ----------
    _EXPECTED_TYPES: dict[str, any]
        Contains all the properties of the configuration and their expected
        type.
    FILE_FORMAT : str
        The file format (extension) used for the configuration file.
    _config_path : str
        The path to the configuration file.
    _config : configparser.ConfigParser
        The config parser object to manage the configuration file contents.

    Methods
    -------
    is_file_valid(config_path: str) -> None
        Checks if the given path points to a valid configuration file. Throws
        an error if the file is invalid (invalid file extension, invalid path,
        corrupted data).
    load_config(new_config_path: str = None) -> None
        Loads the configuration from the current config_path, or replaces it
        with a new one.
    save_config() -> None
        Saves the current configuration to the file.
    _convert_type(key: str, value: str) -> int | bool | str
        Returns 'value' in its expected type if possible.
    get(key: str) -> int | bool | str | None
        Retrieves the value for a given key from the configuration.
        Returns None if the key is not found.
    get_sections() -> list
        Return every sections of the config as a list of strings.
    get_all() -> dict[str, dict[str, str]]
        Returns the current configuration in a key-value dictionary.
    set(key: str, value: str) -> None
        Sets the value for a given key in the configuration, if the key is
        valid.
    """

    _EXPECTED_TYPES = {
        "board-size": int,
        "swap": bool,
        "contest": str,
        "blitz": bool,
        "time": int,
        "gui": bool,
        "language": str,
        "load": str,
        "ai": str,
        "ai-mode": str,
        "ai-mode-player-o": str,
        "ai-mode-player-x": str,
        "ai-depth": int,
        "ai-heuristic": str,
        "ai-heuristic-player-o": str,
        "ai-heuristic-player-x": str,
        "ai-time": int,
        "version": bool,
        "verbose": bool,
        "debug": bool,
    }

    FILE_FORMAT = ".checkersrc"

    def __init__(self, config_path=os.path.join(os.path.dirname(__file__),
                                                "../config.checkersrc")):
        """Initializes the game configuration.

        Parameters
        ----------
        config_path : str
            The path to the configuration file. It must be a valid extension
            and the file must exists.
        """
        log(LogLevel.INFO, "[CONFIG] Initializing game configuration")
        self.__config = configparser.ConfigParser()
        self.__is_file_valid(config_path)

        self.__config_path = config_path
        self.load_config()

    def __is_file_valid(self, config_path: str) -> None:
        """Checks if the provided path is correct.

        Parameters
        ----------
        config_path : str
            The path to the configuration file.

        Raises
        ------
        ValueError
            If the file extension is not recognized or a key in the
            configuration file does not match the expected type.
        FileNotFoundError
            If the path is incorrect.
        configparser.Error
            If the data can't be parsed (corrupted).
        """
        if not config_path.endswith(self.FILE_FORMAT):
            raise ValueError("Incorrect Config file format.")

        if not os.path.exists(config_path):
            raise FileNotFoundError("Incorrect Config file path.")

        # Check if the file is properly formatted
        tmp_config = configparser.ConfigParser()
        try:
            tmp_config.read(config_path)
        except configparser.Error as error:
            raise configparser.Error("Configuration file not formatted "
                                     "properly.") from error
        # Check if the types found for each key matches the expected type
        tmp_config_keys = []
        for section in tmp_config.sections():
            for key, value in tmp_config[section].items():
                tmp_config_keys.append(key)
                try:
                    self.__convert_type(key, value)
                except ValueError as error:
                    raise ValueError(
                        f"Invalid type for key '{key}': "
                        f"Expected {self._EXPECTED_TYPES.get(key)}") from error

        # Check if there is a missing entry in the configuration file
        for key in self._EXPECTED_TYPES.keys():
            if key not in tmp_config_keys:
                raise ValueError(f"Missing entry '{key}'")

    def load_config(self, new_config_path: str | None = None) -> None:
        """
        Loads the configuration from the current config_path. If a
        new_config_path is provided and valid, it replaces the current path.

        Parameters
        ----------
        new_config_path : str, optional
            The new configuration file path to load.

        Raises
        ------
        ValueError
            If the configuration file has an incorrect format.
        """
        log(LogLevel.INFO, "[CONFIG] Loading game configuration")

        # analyze the new path
        if new_config_path is not None:
            try:
                self.__is_file_valid(new_config_path)
                self.__config_path = new_config_path
                log(LogLevel.DEBUG, "New config path valid. Replacing current "
                    "path.")
            except (ValueError, configparser.Error, FileNotFoundError):
                log(LogLevel.WARNING, "New config path invalid. Keeping the "
                    "old path.")

        try:
            self.__config.read(self.__config_path)
        except configparser.Error as error:
            error_message = "Unexpected : Configuration file not " \
                "formatted properly."
            log(LogLevel.CRITICAL, error_message)
            raise ValueError(error_message) from error

    def save_config(self) -> None:
        """ Saves the current configuration to the file. """
        log(LogLevel.INFO, "[CONFIG] Saving current game configuration")

        try:
            self.__is_file_valid(self.__config_path)
            with open(self.__config_path, 'w', encoding="ascii") as configfile:
                self.__config.write(configfile)
        except (ValueError, configparser.Error, FileNotFoundError):
            log(LogLevel.ERROR, "Invalid configuration file, can't save the "
                "current configuration.")

    def __convert_type(self, key: str, value: str) -> Union[int, bool, str]:
        """Converts a value to its expected type.

        Parameters
        ----------
        key : str
            The key to verify.
        value: str
            The value to return in its expected type.

        Raises
        ------
        ValueError
            If the expected type does not match the type found in the
            configuration.

        Returns
        -------
        int | bool | str
            The value associated with the key or None if the key is not known.
        """

        expected_type = self._EXPECTED_TYPES.get(key)

        if expected_type == int:
            if value.isdigit():
                return int(value)
            raise ValueError(f"Invalid integer value for '{key}': {value}")

        if expected_type == bool:
            if value.lower() in {"true", "false"}:
                return value.lower() == "true"
            raise ValueError(f"Invalid boolean value for '{key}': {value}")

        return value

    def get(self, key: str) -> Union[int, bool, str, None]:
        """Retrieves the value for a given key from the configuration.

        Parameters
        ----------
        key : str
            The key to look up in the configuration.

        Returns
        -------
        int | bool | str | None
            The value associated with the key in its correct type or None
            if the key is not known.
        """
        sections = self.__get_sections()
        section = None
        for s in sections:
            if key in self.__config[s]:
                section = s
                break

        if section is None:
            log(LogLevel.WARNING, f"Key '{key}' not found in this "
                "configuration.")
            return None

        # No need to check if the key is invalid because if it was,
        # section would be None

        str_value = self.__config.get(section, key)

        try:
            return self.__convert_type(key, str_value)
        except ValueError:
            log(LogLevel.ERROR, f"Invalid type for '{key}': '{str_value}'.")
            return None

    def __get_sections(self) -> list:
        """
        Retrieves all section names from the current configuration.

        Returns
        -------
        list
            A list containing the name of all sections defined in the
            configuration.
        """
        return [section for section in self.__config.keys()
                if section != "DEFAULT"]

    def get_all(self) -> Dict[str, Dict[str, str]]:
        """
        Retrieves all configuration sections, keys and values.

        Returns
        -------
        dict[str, dict[str, str]]
            A dictionary containing the entire configuration.
        """
        return {section: dict(self.__config[section])
                for section in self.__config.sections()}

    def set(self, key: str, value: str) -> None:
        """Sets the value for a given key in the configuration.

        Parameters
        ----------
        key: str
            The key to be set in the configuration.
        value: str
            The value to associate with the key.

        Raises
        ------
        ValueError
            If value is not of the correct type for key.
        """
        try:
            # We always store strings in _config so we don't need the returned
            # value, we just check if the type of value is valid.
            self.__convert_type(key, value)
        except ValueError as error:
            raise ValueError(f"Invalid type for '{key}': '{value}'.") \
                from error

        sections = self.__get_sections()
        section = None
        for s in sections:
            if key in self.__config[s]:
                section = s
                break

        if section is None:
            log(LogLevel.WARNING, f"Key '{key}' not found in this "
                "configuration.")
            return

        # No need to check if the key is invalid because if it was,
        # section would be None

        self.__config.set(section, key, str(value))

    def __str__(self):
        result = []
        for section in self.__config:
            if section == "DEFAULT":
                continue
            result.append(f"[{section}]")
            for key in self.__config[section]:
                result.append(f"{key} = {self.__config[section][key]}")
        return '\n'.join(result)
