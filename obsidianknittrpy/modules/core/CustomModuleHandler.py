import os
import shutil
import importlib.util
import inspect
from pathlib import Path
from obsidianknittrpy.modules.processing.processing_module_runner import BaseModule


class CustomModuleHandler:
    def __init__(self, custom_modules_dir):
        self.custom_modules_dir = Path(custom_modules_dir)
        self.custom_modules_dir.mkdir(parents=True, exist_ok=True)

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
            if confirm != 'y':
                new_name = input(
                    "Enter a new name for the file (with .py extension): "
                ).strip()
                if not new_name.endswith(".py"):
                    raise ValueError("The new name must end with .py.")
                destination = self.custom_modules_dir / new_name

        # Copy the file
        shutil.copy(file_path, destination)
        print(f"File '{file_path.name}' added as '{destination.name}'.")

        # Attempt to import the module
        try:
            spec = importlib.util.spec_from_file_location(destination.stem, destination)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print(f"Module '{destination.stem}' imported successfully.")
        except Exception as e:
            print(f"Warning: Failed to import module '{destination.stem}'. Error: {e}")

    def remove(self, module_name):
        """
        Remove a custom module file.

        Args:
            module_name (str): Name of the module file to remove (without .py).
        """
        module_path = self.custom_modules_dir / f"{module_name}.py"

        if not module_path.exists():
            raise FileNotFoundError(f"Module '{module_name}' does not exist.")

        confirm = (
            input(
                f"Are you sure you want to remove the module '{module_path.name}',\nlocated at: '{module_path}'? (y/n): "
            )
            .strip()
            .lower()
        )
        if confirm == 'y':
            module_path.unlink()
            print(f"Module '{module_path.name}' has been removed.")
        else:
            print("Operation canceled.")

    def list(self):
        """
        List all classes inheriting from BaseModule in custom_modules.
        """
        results = []
        built_in_classes = self._get_builtin_classes()

        for file in self.custom_modules_dir.glob("*.py"):
            try:
                spec = importlib.util.spec_from_file_location(file.stem, file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, BaseModule) and obj is not BaseModule:
                        class_info = name
                        if name in built_in_classes:
                            print(
                                f"Warning: Class '{name}' conflicts with a built-in module."
                            )
                        if any(r["class"] == name for r in results):
                            class_info += f" ({file})"
                        results.append({"class": class_info, "file": str(file)})

            except Exception as e:
                print(f"Warning: Could not process file '{file}'. Error: {e}")

        print("Custom Modules:")
        for entry in results:
            print(f"{entry['class']}\n- path: {entry["file"]}")

    def _get_builtin_classes(self):
        """
        Retrieve all class names inheriting from BaseModule in built-in modules.
        """
        built_in_classes = set()
        for name, obj in inspect.getmembers(BaseModule, inspect.isclass):
            if issubclass(obj, BaseModule) and obj is not BaseModule:
                built_in_classes.add(name)
        return built_in_classes
