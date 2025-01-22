import importlib.util
import sys
import os


def import_custom_module(module_path, module_name):
    """Dynamically load a module by its path and name."""
    # Ensure obsidianknittrpy is importable in both source and compiled states
    if hasattr(sys, '_MEIPASS'):  # Compiled executable
        meipass_path = sys._MEIPASS
        if meipass_path not in sys.path:
            sys.path.insert(0, meipass_path)

    # Import the custom module dynamically
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module  # Register the module
            spec.loader.exec_module(module)
            return module
    raise ImportError(f"Could not load module {module_name} from {module_path}")
