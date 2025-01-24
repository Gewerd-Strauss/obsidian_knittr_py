import os
import shutil
import importlib.util
import inspect
from pathlib import Path
from obsidianknittrpy.modules.processing.processing_module_runner import BaseModule
import logging


class CustomModuleHandler:
    def __init__(self, custom_modules_dir, loglevel=None):
        self.custom_modules_dir = Path(custom_modules_dir)
        self.custom_modules_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(
            self.__class__.__module__ + "." + self.__class__.__qualname__
        )
        self.logger.setLevel(loglevel)

    def add(self, file_path):
        """
        Add a Python file as a custom module.

        Args:
            file_path (str): Absolute path to the Python file to add.
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.suffix != ".py":
            raise ValueError("Only Python files (.py) can be added as modules.")

        destination = self.custom_modules_dir / file_path.name

        if destination.exists():
            confirm = (
                input(
                    f"A file named '{file_path.name}' already exists. Overwrite? (y/n): "
                )
                .strip()
                .lower()
            )
            if confirm == "y":
                backup_path = destination.with_suffix(".backup.py")
                shutil.copy(destination, backup_path)
                self.logger.info(f"Existing module backed up as '{backup_path.name}'.")
            else:
                new_name = input(
                    "Enter a new name for the file (with .py extension): "
                ).strip()
                if not new_name.endswith(".py"):
                    raise ValueError("The new name must end with .py.")
                destination = self.custom_modules_dir / new_name
        else:
            backup_path = None

        # Copy the new file
        shutil.copy(file_path, destination)
        self.logger.info(f"File '{file_path.name}' added as '{destination.name}'.")

        # Attempt to import the module
        try:
            spec = importlib.util.spec_from_file_location(destination.stem, destination)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.logger.info(f"Module '{destination.stem}' imported successfully.")
            if backup_path is not None:
                if backup_path.exists():
                    os.remove(backup_path)
            # TODO: remove backup file after import was found to be successfull.
            return destination
        except Exception as e:
            # Reintroduce the backup if the import fails
            if destination.exists():
                destination.unlink()  # Remove the problematic file
            if backup_path is not None:
                if backup_path.exists():
                    shutil.move(backup_path, destination)  # Restore the backup
                    self.logger.warning(
                        f"Warning: Failed to import module '{destination.stem}'. "
                        f"Reverted to the original module. Error: {e}"
                    )
                else:
                    self.logger.warning(
                        f"Warning: Failed to import module '{destination.stem}'. "
                        f"Original file was not found. Error: {e}"
                    )

    def remove(self, module_name):
        """
        Remove a custom module file.

        Args:
            module_name (str): Name of the module file to remove (without .py).

        Returns:
            Path: Path of the removed module file.
        """
        module_path = self.custom_modules_dir / f"{module_name}.py"

        if not module_path.exists():
            raise FileNotFoundError(f"Module '{module_name}' does not exist.")

        confirm = (
            input(
                f"Are you sure you want to remove the module '{module_path.name}',\n"
                f"located at: '{module_path}'? (y/n): "
            )
            .strip()
            .lower()
        )
        if confirm == "y":
            module_path.unlink()
            self.logger.info(f"Module '{module_path.name}' has been removed.")
            return module_path
        else:
            self.logger.info("Operation canceled.")
            return None

    def list(self):
        """
        List all classes inheriting from BaseModule in custom_modules.
        """
        results = []
        built_in_classes = self._get_builtin_classes()

        for file in self.custom_modules_dir.glob("*.py"):
            if not file.name.endswith(".backup.py"):
                try:
                    spec = importlib.util.spec_from_file_location(file.stem, file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, BaseModule) and obj is not BaseModule:
                            class_info = name
                            if name in built_in_classes:
                                self.logger.warning(
                                    f"Warning: Module '{name}' conflicts with a built-in module."
                                )
                            if any(r["class"] == name for r in results):
                                class_info += f" ({file})"
                            results.append({"class": class_info, "file": str(file)})
                except Exception as e:
                    self.logger.warning(
                        f"Warning: Could not process file '{file}'. Error: {e}"
                    )

        print("Custom Modules:")
        for entry in results:
            print(f"{entry['class']}\n- path: {entry['file']}")

    def _get_builtin_classes(self):
        """
        Retrieve all class names inheriting from BaseModule in the entire obsidianknittrpy package.
        """
        built_in_classes = set()
        for name, obj in inspect.getmembers(BaseModule, inspect.isclass):
            if issubclass(obj, BaseModule) and obj is not BaseModule:
                built_in_classes.add(name)
        return built_in_classes
