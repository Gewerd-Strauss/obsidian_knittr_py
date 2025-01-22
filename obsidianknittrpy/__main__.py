# __main__.py
import sys
import os

# Ensure obsidianknittrpy is importable in both source and compiled states
if hasattr(sys, '_MEIPASS'):  # Running in PyInstaller's compiled mode
    meipass_path = sys._MEIPASS
    if meipass_path not in sys.path:
        sys.path.insert(0, meipass_path)
else:
    # Ensure source context resolves the package directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

# Import and run the main function
from obsidianknittrpy.main import main

if __name__ == "__main__":
    main()
