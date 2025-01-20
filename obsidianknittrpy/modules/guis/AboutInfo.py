import tkinter as tk
import subprocess
import os
import sys
import logging as logging
from obsidianknittrpy.modules.utility import get_util_version
from obsidianknittrpy.modules.obsidian_html.ObsidianHTML import ObsidianHTML
from obsidianknittrpy import __version__, __author__
import importlib.util
import shutil as shutil


class AboutInfo:

    def __init__(
        self,
        settings,
        loglevel=None,
    ):
        self.logger = logging.getLogger(
            self.__class__.__module__ + "." + self.__class__.__qualname__
        )
        self.logger.setLevel(level=loglevel)
        self.settings = settings
        self.closed = False

        self.classname = "AboutInfoGUI"

    def show_about_info(self):
        """
        Show about-information in a new GUI window:
        - recognised tools (R, quarto, python, pandoc, obsidian-html, tex/tinytex)
        - capabilities
        - versions
        - tool locations
        """
        # Create a new Tkinter window (overlay)
        self.root = tk.Tk()
        self.root.focus_force()
        self.title = "Obsidian Knittr - required tool information"
        self.root.title(self.title)
        self.width = 750
        self.height = 550
        self.root.geometry(f"{self.width}x{self.height}")  # set geometry
        self.root.minsize(self.width, self.height)  # set minimum size
        self.root.resizable(False, False)  # disable resizing of GUI
        self.root.wm_attributes("-topmost", 1)
        # self.root = tk.Toplevel()
        # self.root.title("About Information")

        # Set window size
        self.root.geometry("600x400")

        # Get tool versions and locations
        info = self.get_tool_info()

        # Display the information in the window
        info_text = "\n".join(info)

        capabilities = self.get_tool_capabilities()

        # Add a label with the information
        label = tk.Label(
            self.root, text=info_text, justify="left", anchor="w", padx=10, pady=10
        )
        label.pack(fill="both", expand=True)

        # Add a button to close the window
        close_button = tk.Button(self.root, text="Close", command=self.root.destroy)
        close_button.pack(pady=10)

    def get_tool_capabilities(self):
        """Gather recognized tool info: capabilities"""
        capabilities = []
        # Quarto
        try:
            quarto_capabilities = (
                subprocess.check_output(["quarto", "check"], stderr=subprocess.STDOUT)
                .decode()
                .strip()
            )

            capabilities.append(f"Quarto:\n {quarto_capabilities}")
        except subprocess.CalledProcessError:
            capabilities.append("Quarto: Not installed")

    def get_package_path(self, package_name):
        package_spec = importlib.util.find_spec(package_name)
        if package_spec is not None:
            return os.path.dirname(package_spec.origin)
        else:
            return ""

    def get_tool_info(self):
        """Gather recognized tool info: versions and locations"""

        info = []

        # Example usage
        try:
            package_path = self.get_package_path("obisidian_knittr_py")
            okpy_version = __version__
            okpy_location = os.path.dirname(os.path.abspath(__file__))
            # python_version = get_util_version(
            #     "python", work_dir=self.settings["DIRECTORIES_PATHS"]["work_dir"]
            # )
            # python_location = (
            #     subprocess.check_output(["which", "python"]).decode().strip()
            # )
            info.append(
                f"obsidian_knittr_py:\n  Version: {okpy_version}\n  Path: '{okpy_location}'"
            )
        except subprocess.CalledProcessError:
            info.append("obsidian_knittr_py: Not installed")

        # Python
        python_version = sys.version
        python_location = sys.executable
        try:
            python_version = get_util_version(
                "python", work_dir=self.settings["DIRECTORIES_PATHS"]["work_dir"]
            )
            python_location = (
                subprocess.check_output(["which", "python"]).decode().strip()
            )
            info.append(
                f"Python:\n  Version: {python_version}\n  Path: '{python_location}'"
            )
        except subprocess.CalledProcessError:
            info.append("Python: Not installed")

        # R
        try:
            r_version = get_util_version(
                "R", work_dir=self.settings["DIRECTORIES_PATHS"]["work_dir"]
            )
            r_location = subprocess.check_output(["which", "R"]).decode().strip()
            info.append(f"R:\n  Version: {r_version}\n  Path: '{r_location}'")
        except subprocess.CalledProcessError:
            info.append("R: Not installed")

        # Quarto
        try:
            quarto_version = (
                subprocess.check_output(
                    ["quarto", "--version"], stderr=subprocess.STDOUT
                )
                .decode()
                .strip()
            )
            quarto_location = (
                subprocess.check_output(["which", "quarto"]).decode().strip()
            )
            info.append(
                f"Quarto:\n  Version: {quarto_version}\n  Path: '{quarto_location}'"
            )
        except subprocess.CalledProcessError:
            info.append("Quarto: Not installed")

        # Pandoc
        try:
            # pandoc_version = (
            #     subprocess.check_output(
            #         ["pandoc", "--version"], stderr=subprocess.STDOUT
            #     )
            #     .decode()
            #     .strip()
            # )
            pandoc_version = get_util_version(
                "pandoc", work_dir=self.settings["DIRECTORIES_PATHS"]["work_dir"]
            )
            pandoc_location = (
                subprocess.check_output(["which", "pandoc"]).decode().strip()
            )
            info.append(
                f"Pandoc:\n  Version: {pandoc_version}\n  Path: '{pandoc_location}'"
            )
        except subprocess.CalledProcessError:
            info.append("Pandoc: Not installed")

        # Obsidian HTML (Assuming it's some kind of software installed)
        try:
            ohtml_info = self.get_obsidianhtml_info()

            info.append(
                f"Obsidian-HTML (bundled):\n  Version: {ohtml_info["default"]["version"].lower()}\n  Path: '{ohtml_info["default"]["location"].lower()}'"
            )
            if "custom" in ohtml_info:
                if ".exe" in ohtml_info["custom"]["location"].lower():
                    info.append(
                        f"Obsidian-HTML (custom, compiled):\n  Version: {ohtml_info["custom"]["version"].lower()}\n  Path: '{ohtml_info["custom"]["location"].lower()}'"
                    )
                else:
                    info.append(
                        f"Obsidian-HTML (custom, source-code):\n  Version: {ohtml_info["custom"]["version"].lower()}\n  Path: '{ohtml_info["custom"]["location"].lower()}'"
                    )
        except subprocess.CalledProcessError:
            info.append("Obsidian-HTML: Not installed")
        self.logger.debug(info)
        return info

    def get_obsidianhtml_info(self):
        """
        Special handler to retrieve version of obsidian_html used - since it can be run with a custom ohtml-path provided
        """
        print("TODO: write OHTML_version_getter for AboutInfo-GUI")
        info = {}
        info["custom"] = {}
        info["default"] = {}
        isset_own_obsidian_html = (
            "own_ohtml_fork_dir" in self.settings["DIRECTORIES_PATHS"]
        )
        if isset_own_obsidian_html:
            # custom fork is declared.
            # Thus, get its path and version
            # Afterwards, also get the default path and version
            own_obsidian_html_location = self.settings["DIRECTORIES_PATHS"][
                "own_ohtml_fork_dir"
            ]
            own_obsidian_html_version = (
                subprocess.check_output(
                    ["python", "-m" "obsidianhtml", "version"],
                    stderr=subprocess.PIPE,
                )
                .decode()
                .strip()
            )
            info["custom"]["location"] = own_obsidian_html_location
            info["custom"]["version"] = own_obsidian_html_version

        which_obsidianhtml = shutil.which('obsidianhtml')

        isset_default_obsidian_html = "obsidianhtml.exe" in which_obsidianhtml.lower()
        if isset_default_obsidian_html:
            default_obsidian_html_version = (
                subprocess.check_output(
                    ["obsidianhtml", "version"], stderr=subprocess.STDOUT
                )
                .decode()
                .strip()
            )
            default_obsidian_html_location = self.get_package_path("obsidianhtml")
            info["default"]["location"] = default_obsidian_html_location
            info["default"]["version"] = default_obsidian_html_version
        return info
