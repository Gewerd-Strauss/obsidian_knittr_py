import os
import sys
import shutil
import importlib.util
import inspect
from pathlib import Path
from obsidianknittrpy.modules.processing.processing_module_runner import BaseModule
from obsidianknittrpy.modules.utils.dynamic_loader import import_custom_module
import logging
import pkgutil
import ast
import yaml


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

    def find_class_in_file(self, file_path, needle_class):
        # Read the file content
        found_modules = []
        with open(file_path, 'r') as file:
            file_content = file.read()

        # Parse the content into an Abstract Syntax Tree (AST)
        try:
            tree = ast.parse(file_content)
        except SyntaxError:
            print(f"Syntax error in file {file_path}")
            return

        # Iterate through all nodes in the AST and look for class definitions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if the class is inheriting from BaseModule
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == 'BaseModule':
                        if node.name in needle_class:
                            module = import_custom_module(
                                module_path=file_path, module_name=needle_class
                            )
                            # Dynamically instantiate the class AddSectionHeaderIDs or needle_class
                            class_to_instantiate = getattr(module, needle_class)
                            instance = class_to_instantiate()

                            # Only consider
                            if hasattr(instance, 'process') and hasattr(
                                instance, "initiate_base_config"
                            ):
                                try:
                                    instance.initiate_base_config()
                                    conf = instance.config
                                    yaml_struct = {
                                        "module_name": needle_class,
                                        "config": conf,
                                        "enabled": False,
                                        "file_name": Path(file_path).stem,
                                    }
                                    print(yaml.dump(yaml_struct))
                                except Exception as e:
                                    raise Exception(
                                        f"Error when calling process() on {needle_class}: {e}"
                                    )
                            else:
                                if not hasattr(instance, 'process'):
                                    self.logger.error(
                                        f"{needle_class} [File: {file_path}] does not have a process() method."
                                    )
                                if not hasattr(instance, "initiate_base_config"):
                                    self.logger.error(
                                        f"{needle_class} [File: {file_path}] does not have a initiate_base_config() method. The module's configuration could not be retrieved."
                                    )
                            return

    def iterate_over_files(self, needle_class):
        # Iterate over all .py files in the specified directory
        for root, dirs, files in os.walk(self.custom_modules_dir):
            for file_name in files:
                if file_name.endswith('.py') and not file_name.endswith(".backup.py"):
                    file_path = os.path.join(root, file_name)
                    self.find_class_in_file(file_path, needle_class)

    def _get_builtin_classes(self):
        """
        Retrieve all class names inheriting from BaseModule in the entire obsidianknittrpy package.
        """
        built_in_classes = set()
        package_name = "obsidianknittrpy"

        # Get all modules in the package
        for importer, module_name, is_pkg in pkgutil.walk_packages(
            path=sys.modules[package_name].__path__, prefix=f"{package_name}."
        ):
            try:
                # Import the module
                module = importlib.import_module(module_name)

                # Inspect for classes that inherit from BaseModule
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, BaseModule) and obj is not BaseModule:
                        built_in_classes.add(name)
            except Exception as e:
                self.logger.warning(
                    f"Warning: Failed to inspect module '{module_name}'. Error: {e}"
                )

        return built_in_classes
