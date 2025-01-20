import os
import logging
import subprocess
import re as re
from obsidianknittrpy.modules.obsidian_html import ObsidianHTML


def convert_format_args(args):
    """Execute the convert command."""

    # Prepare a dictionary for the arguments
    arguments = {}

    # Handle pass-through arguments
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
            # work_dir=r"D:\Dokumente neu\Repositories\python\obsidian-html",
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
