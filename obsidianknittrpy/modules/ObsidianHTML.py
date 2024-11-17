import os
import subprocess
import re
import shutil
import yaml
import importlib.util
import logging


class ObsidianHTML:
    def __init__(
        self,
        manuscript_path="",
        config_path="",
        use_convert=True,
        use_own_fork=False,
        verbose=False,
        output_dir="",
        work_dir="",
        own_ohtml_fork_dir="",
        auto_submit_gui=False,
        encoding="utf-16-le",
    ):
        # Set initial variables
        self.logger = logging.getLogger(
            self.__class__.__module__ + "." + self.__class__.__qualname__
        )
        self.logger.info(f"Converting '{manuscript_path}' to standard markdown.")
        self.manuscript_path = manuscript_path
        self.encoding = encoding
        self.encoding = self.encoding if use_own_fork else "utf-8"
        self.config_path = os.path.normpath(os.path.abspath(config_path))
        self.config_template = None
        self.initialise_configuration()
        self.use_convert = use_convert
        self.use_own_fork = use_own_fork
        self.verbose = verbose
        self.output_dir = output_dir or os.path.join(
            os.path.expanduser("~"), "Desktop", "ObsidianHTMLOutput"
        )
        self.work_dir = work_dir or os.path.join(
            os.path.expanduser("~"), "Desktop", "ObsidianHTMLOutput"
        )
        self.own_ohtml_fork_dir = own_ohtml_fork_dir
        self.auto_submit_gui = auto_submit_gui
        self.obsidianhtml_path = ""
        self.obsidianhtml_available = self.check_obsidianhtml()
        self.python_available = self.check_python()
        # Initialize if checks passed
        if not self.obsidianhtml_available or not self.python_available:
            self.initialized = False
        else:
            self.initialized = True

    def initialise_configuration(self):
        # Define the configuration template as a multi-line string with the manuscript path injected
        self.config_template = f"""
# Input and output path of markdown files
obsidian_entrypoint_path_str: {os.path.normpath(self.manuscript_path)}
max_note_depth: 15
copy_vault_to_tempdir: True

module_config:
  get_file_list:
    include_glob:
      value: '*'
    exclude_glob:
      value:
        - "/.git/**/*"
        - "/.github/**/*"
        - "/.obsidian/**/*"
        - "/.quarto/**/*"
        - "/.renv/**/*"
        - "/.Rproj.user/**/*"
        - "/.trash/**/*"
        - "/.vscode/**/*"
        - "/002 templates/**/*"
        - "/_freeze/**/*"
        - "/_site/**/*"
        - "/.DS_Store/**/*"

toggles:
  strict_line_breaks: True
  wrap_inclusions: False
  strip_inclusion_headers: True
  features:
    embedded_note_titles:
      enabled: False
    graph:
      enabled: False
      show_inclusions_in_graph: False
    search:
      enabled: False
    mermaid_diagrams:
      enabled: False
    math_latex:
      enabled: False
    code_highlight:
      enabled: False
    callouts:
      enabled: False
"""

    def remove_config(self):
        if os.path.exists(self.config_path):
            os.remove(self.config_path)

    def create_config(self):
        # Write the configuration template to a YAML file at the specified path
        if not self.use_own_fork:
            self.config_template = self.config_template.replace(
                "strip_inclusion_headers: True", ""
            )
        with open(self.config_path, "w", encoding=self.encoding) as file:
            yaml.safe_dump(
                yaml.safe_load(self.config_template), file, encoding=self.encoding
            )
        self.logger.info(f"ObsidianHTML-Configuration written to {self.config_path}")

    def check_obsidianhtml(self):
        """Attempt to import the obsidianhtml main module based on the selected fork to see if it is installed."""
        try:
            if self.use_own_fork:
                # Construct the path to the custom fork's module
                custom_module_path = os.path.join(
                    self.own_ohtml_fork_dir, "obsidianhtml", "__init__.py"
                )
                # Load the custom module
                spec = importlib.util.spec_from_file_location(
                    "obsidianhtml", custom_module_path
                )
                obsidianhtml_custom = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(obsidianhtml_custom)
                self.obsidianhtml_path = os.path.abspath(
                    os.path.join(self.own_ohtml_fork_dir, "obsidianhtml")
                )

            else:
                # Dynamically find the installed obsidianhtml package
                spec = importlib.util.find_spec("obsidianhtml")
                if spec is not None:
                    obsidianhtml_default = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(obsidianhtml_default)
                    self.obsidianhtml_path = os.path.dirname(spec.origin)
                else:
                    self.logger.critical("ObsidianHTML package could not be found.")
                    return False

            return True
        except ImportError:
            self.logger.critical(
                "ObsidianHTML could not be found. Please install it before proceeding."
            )
            return False

    def check_python(self):
        """Check if Python is available."""
        try:
            result = subprocess.run(
                ["python", "--version"], capture_output=True, text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            self.logger.error(
                "Python could not be found. Please install it before proceeding."
            )
        return False

    def validate_config(self):
        """Validate configuration file and entry point."""
        if not os.path.exists(self.config_path):
            self.logger.critical("Config file does not exist.")
            return False
        with open(self.config_path, "r", encoding=self.encoding) as file:
            config_contents = file.read()
            if (
                "obsidian_entrypoint_path_str:" not in config_contents
                and self.use_convert
            ):
                self.logger.critical(
                    "Config file missing 'obsidian_entrypoint_path_str' setting."
                )
                return False
        return True

    def construct_command(self, version=False):
        """Constructs the command to run ObsidianHTML."""
        if version:
            command = [
                "obsidianhtml",
                "version",
            ]
        elif self.use_convert or not self.manuscript_path:
            self.use_convert = True
            command = [
                "obsidianhtml",
                "convert",
                "-i",
                f"{os.path.abspath(self.config_path)}",
            ]
        else:
            command = [
                "obsidianhtml",
                "run",
                "-f",
                self.manuscript_path,
                "-i",
                os.path.abspath(self.config_path),
            ]

        if self.verbose:
            command.append("-v")
        if self.use_own_fork:
            command.insert(0, "-m")
            command.insert(0, "python")

        return command

    def execute_command(self, command, work_dir, env=None):
        """Executes a command and returns its output."""
        if os.path.exists(work_dir):
            result = subprocess.run(
                command, cwd=work_dir, capture_output=True, text=True, env=env
            )
            return result

    def parse_output(self, output):
        """Parse specific paths and versions from ObsidianHTML output."""
        md_path_regex = r"md: (?P<md_path>.*)"
        match = re.search(md_path_regex, output)
        if match and os.path.exists(match.group("md_path")):
            return match.group("md_path").strip()
        return ""

    def run(self):
        """Main method to run ObsidianHTML."""
        if not self.initialized:
            return False

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.remove_config()
        self.create_config()
        if not self.validate_config():
            return False
        work_dir = self.work_dir

        env = os.environ.copy()  # Copy the current environment
        if self.use_own_fork:
            env["PYTHONPATH"] = os.path.dirname(
                self.obsidianhtml_path
            )  # Add module path to PYTHONPATH
        # get ohtml version
        command_version = self.construct_command(True)
        output_version = self.execute_command(command_version, work_dir, env)
        output_version = output_version.stdout
        if "commit:" in output_version:
            output_version = output_version.replace("\n commit:", "(commit:")
            output_version = output_version.replace("\n", ")")  # .join(")")
        else:
            output_version = output_version.replace("\n", "")
            output_version = "(" + output_version + ")"

        command = self.construct_command()
        output = self.execute_command(command, work_dir, env)

        md_path = self.parse_output(output.stdout)
        if not md_path:
            self.logger.critical(
                "Failed to parse output. Please check manually.The utility will exit."
            )
            return False
        self.output = {}
        self.output["command"] = "".join(command)
        self.output["obsidian_html_path"] = self.obsidianhtml_path
        self.output["obsidian_html_version"] = output_version
        self.output["obsidian_html_copydir"] = ""
        self.output["output_path"] = md_path
        self.output["stdOut"] = output.stdout
        self.output["stdErr"] = output.stderr
        self.output["working_directory"] = self.work_dir
