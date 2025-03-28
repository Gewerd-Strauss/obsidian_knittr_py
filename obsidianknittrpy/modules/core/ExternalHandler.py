import argparse
import os
import yaml
from pathlib import Path
import logging


class ExternalHandler:
    """
    This class handles the pre-loading of external dependencies (paths).

    It does _not_ handle the implementation of said dependencies in the
    processing-code within `main()`/`handle_x()`.
    """

    def __init__(
        self,
        interface_dir,
        loglevel=None,
    ):
        self.interface_dir = interface_dir
        os.makedirs(self.interface_dir, exist_ok=True)
        self.logger = logging.getLogger(
            self.__class__.__module__ + "." + self.__class__.__qualname__
        )
        self.logger.setLevel(loglevel)
        self.configurable_tools = ["obsidian-html", "R"]

    def _get_filepath(self, key):
        return os.path.join(self.interface_dir, f"{key}.yml")

    def is_path(self, value):
        # Check if value is a string and represents an existing path
        return isinstance(value, str) and (
            os.path.exists(value) or Path(value).exists()
        )

    def set(self, file, key, value):
        """Sets the path for a given key."""

        filepath = self._get_filepath(file)
        if not os.path.exists(filepath):  # create file if not existent
            with open(filepath, "w", encoding="utf-8") as f:
                yaml.dump({}, f)
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        data[key] = value
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(data, f)
        self.logger.info(f"Set '{file}.{key}' to '{value}'.")

    def unset(self, file, key):
        """Removes the configuration for a given key."""
        filepath = self._get_filepath(file)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                data_ = yaml.safe_load(f)  # get the data
                data_.pop(key, None)
            with open(filepath, "w", encoding="utf-8") as f:
                yaml.dump(data_, f)
            self.logger.info(f"Removed '{file}.{key}'.")
            if len(data_) == 0:
                os.remove(filepath)
                self.logger.warning(f"Removed '{file}'.")
        else:
            raise FileNotFoundError(f"File '{filepath}' does not exist.")

    def list(self, file=None, return_type=None):
        """Lists all tools, their configured keys, as well as unconfigured and unrecognised tools."""
        if file is not None:
            # Handle case where a specific file is set
            filepath = self._get_filepath(file)
            if os.path.exists(filepath):
                with open(filepath, encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                print(f"Configuration for '{file}':")
                for key, value in data.items():
                    print(f"    {key}: {value}")
                if file not in self.configurable_tools:
                    raise NotImplementedError(
                        f"A tool with the identifier '{file}' has not been implemented. Changes made to this tool's configuration will not be considered by the utility."
                    )
            else:
                raise FileNotFoundError(
                    f"File '{filepath}' does not exist. Please declare a configuration-file for '{file}' and populate it using the 'set'-verb before attempting to list its entries."
                )
            return

        set_tools = {}
        unset_tools = set(self.configurable_tools)
        unrecognised_tools = set()

        # Iterate through all YAML files in the directory
        for filename in os.listdir(self.interface_dir):
            if filename.endswith(".yml"):
                tool = os.path.splitext(filename)[0]
                filepath = os.path.join(self.interface_dir, filename)
                with open(filepath, encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}

                if tool in self.configurable_tools:
                    unset_tools.discard(tool)
                    set_tools[tool] = data
                else:
                    unrecognised_tools.add(tool)
        if return_type is None:
            # Print Set tools
            print("Set tools:")
            for tool, config in set_tools.items():
                print(f"    {tool}")
                if file is not None:
                    for key, value in config.items():
                        print(f"        {key}: {value}")

            # Print Unset tools
            print("\nUnset tools:")
            for tool in unset_tools:
                print(f"    {tool}")

            # Print Unrecognised tools
            print("\nUnrecognised tools:")
            for tool in unrecognised_tools:
                print(f"    {tool}")
        else:
            if return_type == "set":
                return set_tools
            elif return_type == "unset":
                return unset_tools
            elif return_type == "unrecognised":
                return unrecognised_tools
            raise ValueError(
                f"Invalid option for return_type, must be member of [None,'set','unset','unrecognised']"
            )

    def get(self, file, key):
        """Gets the value for a specific key in a specific configuration-file."""
        filepath = self._get_filepath(file)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                data_ = yaml.safe_load(f)  # get the data
                if key in data_:
                    return data_[key]
                else:
                    raise KeyError(
                        f"Key '{key}' not present in handled configuration-file {filepath}"
                    )
        else:
            raise FileNotFoundError(f"File '{filepath}' does not exist.")
