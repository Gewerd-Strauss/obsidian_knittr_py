import os
import logging
import subprocess
import re as re
import sys
from obsidianknittrpy.modules.obsidian_html import ObsidianHTML


def pre_configure_obsidianhtml_fork(CH, EH, args):
    """
    Applies custom Obsidian-HTML path if found in either of the following places.
    First, it looks at the External Handler, whose static data is written to the `interface`-subdirectory in the application-directory.
    Afterwards, it looks if the commandline arguments `--OHTML.Forkpath` and `--OHTML.UseCustomFork` are provided, and applies this path if relevant.
    Finally, if neither of the first two occur, the relevant configuration keys are unset. This ensures that the user cannot provide
    """
    ## handle custom OHTML fork
    if ("obsidian-html" in EH.list(return_type="set")) or (
        "OHTML.UseCustomFork" in args and args["OHTML.UseCustomFork"]
    ):
        if "obsidian-html" in EH.list(return_type="set"):
            # 1. provided by external handler.
            # introduce the own OHTML-fork directory if set.
            try:
                own_ohtml_fork_dir = EH.get("obsidian-html", "path")
                if own_ohtml_fork_dir is not None:
                    CH.applied_settings["DIRECTORIES_PATHS"][
                        "own_ohtml_fork_dir"
                    ] = own_ohtml_fork_dir
                    CH.applied_settings["OBSIDIAN_HTML"]["use_custom_fork"] = True
                    CH.is_own_ohtml_fork_available = True
            except KeyError:
                CH.is_own_ohtml_fork_available = False
        if (
            ("OHTML.UseCustomFork" in args)
            and args["OHTML.UseCustomFork"]
            and (args["OHTML.UseCustomFork"] is not None)
        ):
            # 2. provided by commandline-args `OHTML.UseCustomFork` and `OHTML.ForkPath`:
            if ("OHTML.ForkPath" in args) and (
                args["OHTML.ForkPath"] is not None
            ):  # if fork path is provided by commandline, insert it.
                if os.path.exists(args["OHTML.ForkPath"]) and (
                    os.path.isdir(args["OHTML.ForkPath"])
                    or is_exe(args["OHTML.ForkPath"])
                ):
                    CH.applied_settings["DIRECTORIES_PATHS"]["own_ohtml_fork_dir"] = (
                        args["OHTML.ForkPath"]
                    )
                else:
                    raise FileNotFoundError(
                        f"The path '{args["OHTML.ForkPath"]}' does not point to an existing directory or executable file ('.exe')."
                    )
                CH.applied_settings["OBSIDIAN_HTML"]["use_custom_fork"] = True
    else:  # 3. no custom fork used. Unset related config-keys.
        CH.applied_settings["OBSIDIAN_HTML"]["use_custom_fork"] = False
        CH.applied_settings["DIRECTORIES_PATHS"]["own_ohtml_fork_dir"] = None

    return CH


def convert_format_args(args):
    """Execute the convert command."""

    # Prepare a dictionary for the arguments
    arguments = {}

    # Handle pass-through arguments
    try:
        if args.pass_through:
            for item in args.pass_through:
                if "::" in item and "=" in item:
                    key, value = item.split("=", 1)
                    arguments[key.strip()] = value.strip()
                else:
                    # Here, we can just store the item as is
                    arguments[item.strip()] = (
                        ""  # Assuming you want an empty value for other pass-through items
                    )
    finally:  # necessary to allow the ExtensionHandler set/unset/list methods to bypass without erroring.
        pass
    try:
        # Add other arguments to the dictionary
        for key, value in vars(
            args
        ).items():  # Use vars() to convert Namespace to dictionary
            if key != "pass_through":  # Skip pass_through since it's already handled
                arguments[key] = value  # Add each argument to the dictionary

        # Print all arguments in the specified format
        logging.debug("Formatted Arguments:")
        for k, v in arguments.items():
            logging.debug(f'["{k}"] = "{v}"')
    finally:  # necessary to allow the ExtensionHandler set/unset/list methods to bypass without erroring.
        pass

    return arguments


def init_picknick_basket():
    # Define the settings dictionary
    settings = {
        "bVerboseCheckbox": bool,  # boolean
        "bKeepFilename": bool,  # boolean
        "bBackupOutput": bool,  # boolean
        "bRendertoOutputs": bool,  # boolean
        "bRemoveHashTagFromTags": bool,  # boolean
        "bRemoveQuartoReferenceTypesFromCrossrefs": bool,  # boolean
        "bConvertInsteadofRun": bool,  # boolean
        "bRemoveObsidianHTMLErrors": bool,  # boolean
        "bRestrictOHTMLScope": bool,  # boolean
        "bStripLocalMarkdownLinks": bool,  # boolean
        "ExecutionDirectory": str,  # path/directory
        "bAutoSubmitOTGUI": bool,  # boolean
        "bUseOwnOHTMLFork": bool,  # boolean
    }
    manuscript = {
        "manuscript_path": str,  # path
        "manuscript_dir": str,  # directory
        "manuscript_name": str,  # filename
    }
    # Define the other dictionary
    other = {
        "sel": list,  # placeholder for selection
        "output_formats": {},  # list of output formats
        "input_suffixes": [],  # list of input suffixes
        "file_suffixes": [],  # list of file suffixes
    }

    return {"settings": settings, "objects": other, "manuscript": manuscript}


def get_text_file_path(file_directory, file_name="index.md"):
    try:
        file_path = os.path.normpath(os.path.join(file_directory, file_name))
        return file_path
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return None


def load_text_file(file_path):
    """Load the text from a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return None


def get_util_version(type=str, work_dir=""):
    if type == "quarto":
        command = ["quarto", "-v"]
    elif type == "R":
        command = ["R", "--version"]
    elif type == "python":
        command = ["python", "-V"]
    elif type == "pandoc":
        command = ["pandoc", "-v"]
    elif type == "ohtml":
        obsidian_html = ObsidianHTML(
            manuscript_path=CH.get_key("MANUSCRIPT", "manuscript_path"),
            config_path=CH.default_obsidianhtmlconfiguration_location,
            use_convert=CH.get_key("OBSIDIAN_HTML", "verb") in ["convert", True],
            use_own_fork=CH.get_key("OBSIDIAN_HTML", "use_custom_fork"),
            verbose=CH.get_key("OBSIDIAN_HTML", "verbose_flag"),
            own_ohtml_fork_dir=CH.get_key("DIRECTORIES_PATHS", "own_ohtml_fork_dir"),
            work_dir=CH.get_key("DIRECTORIES_PATHS", "work_dir"),
            output_dir=CH.get_key("DIRECTORIES_PATHS", "output_dir"),
        )
        # obsidianhtml_available = self.check_obsidianhtml()
    result = subprocess.run(
        command,
        check=True,
        cwd=work_dir,
        capture_output=True,
        text=True,
    )
    result = get_util_version_sub(result=result, type=type)
    return result


def get_util_version_sub(result, type=""):
    if type == "R":
        # Try to match the version in stdout first
        needle = r"R version (\d+\.\d+\.\d+)"
    elif type == "python":
        needle = r"(\d+\.\d+\.\d+)\s+"
    elif type == "quarto":
        needle = r"(\d+\.\d+\.\d+)\s+"
    elif type == "pandoc":
        needle = r"(\d+\.\d+\.\d+)"
    match = re.search(needle, result.stdout)
    if not match:  # If no match in stdout, try stderr
        match = re.search(needle, result.stderr)
    if match:
        return match.group(1)  # Return the version number
    raise ValueError("Version number not found in the output.")


def open_folder(folder_path):
    """opens a directory-path on windows, macos and linux/unix"""
    if sys.platform == "win32":
        # Windows
        subprocess.run(["explorer", folder_path])
    elif sys.platform == "darwin":
        # macOS
        subprocess.run(["open", folder_path])
    else:
        # Linux or other Unix-like systems
        subprocess.run(["xdg-open", folder_path])


def open_file(file_path):
    if os.path.isfile(file_path):
        # Path is a file
        try:
            if sys.platform == "win32":
                subprocess.run(["open", file_path], shell=True)
            elif sys.platform == "darwin":
                subprocess.run(["open", file_path])
            else:
                subprocess.run(["xdg-open", file_path])
        except Exception as e:  # Catch any exception from subprocess
            raise OSError(f"Failed to open the file {file_path}: {str(e)}")
    else:
        raise FileNotFoundError(f"The path {file_path} is not a valid file.")


def is_exe(path):
    """Check if a path points to an executable '.exe'-file."""
    return os.path.isfile(path) and path.lower().endswith('.exe')
