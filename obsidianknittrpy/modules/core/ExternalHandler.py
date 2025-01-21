import argparse
import os
import yaml
from pathlib import Path


class ExternalHandler:
    def __init__(self, interface_dir):
        self.interface_dir = interface_dir
        os.makedirs(self.interface_dir, exist_ok=True)
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
        # if self.is_path(value):
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        data[key] = value
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(data, f)
        print(f"Set '{file}.{key}' to '{value}'.")

    def unset(self, file, key):
        """Removes the configuration for a given key."""
        filepath = self._get_filepath(file)
        with open(filepath, "r", encoding="utf-8") as f:
            data_ = yaml.safe_load(f)  # get the data
            data_.pop(key, None)
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(data_, f)
        print(f"Removed '{file}.{key}'.")

    def list(self, unset=False, unrecognised=False):
        """Lists all configured keys and their paths or tools without configuration."""
        configured_tools = {}
        unconfigured_tools = set(self.configurable_tools)
        unrecognised_tools = set()

        # Check all files in the directory
        for file in os.listdir(self.interface_dir):
            if file.endswith(".yml"):
                key = os.path.splitext(file)[0]
                filepath = os.path.join(self.interface_dir, file)

                if key in self.configurable_tools:
                    # Handle tools that are recognized and have configuration
                    unconfigured_tools.discard(key)
                    with open(filepath, encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                        configured_tools[key] = data.get("DIRECTORIES_PATHS", {}).get(
                            key, "(unknown path)"
                        )
                else:
                    # Tools that are not recognized
                    unrecognised_tools.add(key)

        # Return unconfigured tools if requested
        if unset:
            return {key: None for key in unconfigured_tools}

        # Return unrecognised tools if requested
        if unrecognised:
            return {key: None for key in unrecognised_tools}

        # Return configured tools if none of the above flags are set
        return configured_tools

    def get(self, key):
        """Gets the path for a specific key."""
        filepath = self._get_filepath(key)
        if os.path.exists(filepath):
            with open(filepath, encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data.get("DIRECTORIES_PATHS", {}).get(key)
        return None
