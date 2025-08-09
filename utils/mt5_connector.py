# --- START OF FILE mt5_connector.py ---

import configparser
import os

import MetaTrader5 as mt5


class MT5Connector:
    """
    A class to manage the connection to a MetaTrader 5 terminal.
    It encapsulates all configuration reading, separating terminal initialization
    from account login for greater flexibility and security.
    """

    def __init__(self, config_path, terminal_section):
        """
        Initializes the connector by loading the terminal path from a config file.

        :param config_path: Path to the configuration file.
        :param terminal_section: The section in the config file that contains the 'path' to terminal64.exe.
        """
        self.path = None
        self.config_path = config_path
        self.config = configparser.ConfigParser()

        self._load_terminal_config(terminal_section)

    def _load_terminal_config(self, terminal_section):
        """Loads the terminal path from the specified config section."""
        if not os.path.exists(self.config_path):
            print(f"Error: Configuration file not found at: {self.config_path}")
            return

        self.config.read(self.config_path)

        if not self.config.has_section(terminal_section):
            print(f"Error: Section '{terminal_section}' not found in config file.")
            return

        try:
            self.path = self.config.get(terminal_section, "path", fallback=None)
            if self.path == "":
                self.path = None

            print(f"Terminal configuration loaded from section '{terminal_section}'.")

        except Exception as e:
            print(f"Error reading section '{terminal_section}': {e}")

    def initialize_terminal(self):
        """Establishes the technical connection to the MT5 terminal."""
        if not mt5.initialize(path=self.path):
            print(f"Terminal initialize() failed, error code = {mt5.last_error()}")
            return False

        print(
            f"Terminal at '{self.path or 'auto-detected path'}' initialized successfully."
        )
        return True

    def login_to_account(self, account_section):
        """
        Logs into a specific trading account using credentials from a config section.
        This method reads the credentials itself, they are not passed as arguments.

        :param account_section: The section in the config file containing login, password, and server.
        :return: True if login is successful, False otherwise.
        """
        if not self.config.has_section(account_section):
            print(
                f"Error: Account section '{account_section}' not found in config file."
            )
            return False

        try:
            creds = self.config[account_section]
            login = int(creds["login"])
            password = creds["password"]
            server = creds["server"]

            if not mt5.login(login=login, password=password, server=server):
                print(
                    f"Failed to login to account #{login}, error code: {mt5.last_error()}"
                )
                return False

            print(
                f"Successfully logged into account #{login} from section '{account_section}'."
            )
            return True

        except KeyError as e:
            print(f"Error: Missing key {e} in account section '{account_section}'.")
            return False
        except Exception as e:
            print(f"An unexpected error occurred during login: {e}")
            return False

    def shutdown_terminal(self):
        """Shuts down the connection to the MT5 terminal."""
        mt5.shutdown()
        print("Connection to MetaTrader 5 terminal has been shut down.")

    def __enter__(self):
        """Initializes the terminal when entering the 'with' block."""
        if self.initialize_terminal():
            return self
        else:
            raise ConnectionError("Failed to initialize the MetaTrader 5 terminal.")

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Shuts down the terminal when exiting the 'with' block."""
        self.shutdown_terminal()


# --- END OF FILE mt5_connector.py ---
